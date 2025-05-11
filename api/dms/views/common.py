import logging

from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.utils import timezone

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from dateutil import parser
from django_filters.rest_framework import DjangoFilterBackend

from common.constants import ProjectStatus, OrderConstants, VehicleStatus
from dms.filters import ZoneListFilter, ProjectsListFilter
from dms.helpers import generate_excel_report, generate_zone_feature_collections
from dms.models import (
    Project,
    StatusKeyword,
    UserNotification,
    Zone,
    PlanningTemplate,
    Order,
    Tag,
    Vehicle,
)
from dms.serializers import (
    ProjectSerializer,
    StatusKeywordSerializer,
    ZoneSerializer,
    PlanningTemplateSerializer,
    UserNotificationSerializer,
    TagSerializer,
    OrderValidationSerializer,
    ZoneValidationSerializer,
    DriverValidationSerializer,
)

logger = logging.getLogger(__name__)


class PlanningTemplateViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = PlanningTemplateSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ("template_name",)
    search_fields = ("template_name",)

    def get_queryset(self):
        return PlanningTemplate.objects.all().order_by("id")

    def list(self, request, *args, **kwargs):
        limit = request.query_params.get("limit")
        queryset = self.filter_queryset(self.get_queryset())
        if limit == "all":
            page = None
        else:
            page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


class ProjectViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    serializer_class = ProjectSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ProjectsListFilter
    search_fields = ("project_name", "project_id", "base_address")

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(project_id__in=user.projects_with_access)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        projects = Project.objects.filter(status=ProjectStatus.ACTIVE)
        context["all_projects"] = projects
        return context

    def list(self, request, *args, **kwargs):
        limit = request.query_params.get("limit")
        queryset = self.filter_queryset(self.get_queryset())
        if limit == "all":
            page = None
        else:
            page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

    @action(methods=["GET"], detail=True)
    def validate_trip_plan(self, request, pk):
        query_date = self.request.query_params.get("date", None)

        if not query_date:
            return JsonResponse(
                {"message": "No date provided. Date format is YYYY-MM-DD"},
                status=HTTP_400_BAD_REQUEST,
            )
        try:
            project = Project.objects.prefetch_related("project_zones", "project_drivers").get(
                id=pk
            )
        except Project.DoesNotExist as prdne:
            logger.exception(prdne)
            return JsonResponse(
                {"message": f"No project found with id {pk}"}, status=HTTP_400_BAD_REQUEST
            )

        try:
            date = parser.parse(query_date)
        except parser.ParserError:
            return JsonResponse(
                {"message": "Incorrect date format provided. Date format is YYYY-MM-DD"},
                status=HTTP_400_BAD_REQUEST,
            )

        drivers = project.project_drivers.exclude(is_active=False).order_by("user")
        zone_summary = None
        planning_template = project.planning_template
        zone_constraint_enabled = planning_template.zone_constraint
        disabled_time_windows = planning_template.disable_time_windows
        template_timings = {
            "loading_start_time": planning_template.loading_start_time,
            "loading_end_time": planning_template.loading_end_time,
            "offloading_start_time": planning_template.offloading_start_time,
            "offloading_end_time": planning_template.offloading_end_time,
        }
        driver_summary = DriverValidationSerializer(
            drivers,
            context={
                "template_timings": template_timings,
                "zone_constraint": zone_constraint_enabled,
            },
            many=True,
        ).data

        order_context = {}

        unassigned_orders = (
            Order.objects.select_related("customer_address")
            .prefetch_related("order_items")
            .filter(
                Q(project=project)
                & Q(execution_date=date)
                & Q(status=OrderConstants.OrderStatus.UNASSIGNED)
            )
            .annotate(
                total_quantity=Sum("order_items__original_quantity"),
                total_weight=Sum("order_items__line_item_weight"),
                total_cbm=Sum("order_items__line_item_cbm"),
            )
        )
        if zone_constraint_enabled:
            zones = (
                Zone.objects.filter(project=project)
                .annotate(
                    driver_count=Count("zone_drivers"),
                    available_weight_capacity=Sum(
                        "zone_drivers__vehicle_assigned__tonnage_capacity",
                        filter=Q(zone_drivers__vehicle_assigned__isnull=False),
                    ),
                    available_volume_capacity=Sum(
                        "zone_drivers__vehicle_assigned__cbm_capacity",
                        filter=Q(zone_drivers__vehicle_assigned__isnull=False),
                    ),
                )
                .order_by("zone_name")
            )
            zone_summary = ZoneValidationSerializer(
                zones,
                context={"date": date, "drivers": drivers, "orders": unassigned_orders},
                many=True,
            ).data

            zone_details = {}
            for zone_dtl in zone_summary:
                zone_name = zone_dtl["zone_name"]
                details = zone_dtl["zone_details"]

                zone_details.update(
                    {
                        zone_name: {
                            "zone_shift_start": details.get("zone_shift_start"),
                            "zone_shift_end": details.get("zone_shift_end"),
                            "geofence": details.get("geofence"),
                            "drivers": details.get("driver_count", 0),
                        }
                    }
                )
            order_context.update({"zone_details": zone_details})
            drivers = drivers.filter(zone__in=zones)

        vehicles_with_tags = Vehicle.objects.prefetch_related("vehicle_drivers").exclude(
            status=VehicleStatus.DEACTIVATED, vehicle_drivers__isnull=True
        )

        if zone_constraint_enabled:
            z = Zone.objects.filter(project=project)
            vehicles_with_tags = vehicles_with_tags.filter(vehicle_drivers__zone__in=z)

        vehicle_tags = list()
        for vehicle in vehicles_with_tags:
            vehicle_tags.append(list(vehicle.tags.values_list("tag", flat=True)))
        order_context.update(
            {
                "vehicles": vehicles_with_tags,
                "zone_constraint": zone_constraint_enabled,
                "disabled_time_windows": disabled_time_windows,
                "drivers": drivers,
            }
        )
        orders = OrderValidationSerializer(unassigned_orders, many=True, context=order_context).data

        data = {
            "orders": orders,
            "zones": zone_summary,
            "drivers": driver_summary,
            "zone_constraint": zone_constraint_enabled,
            "drivers_without_vehicle": [],
            "drivers_without_zone": [],
            "orders_mismatch_with_driver_zone": [],
            "orders_with_zone": [],
        }

        return JsonResponse(data=data, status=HTTP_200_OK, safe=False)


class StatusKeywordViewSet(viewsets.ModelViewSet):
    serializer_class = StatusKeywordSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (OrderingFilter, SearchFilter)
    filterset_fields = ("status_category", "keyword")
    search_fields = ("status_category", "keyword")
    queryset = StatusKeyword.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        count = queryset.count()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"count": count, "result": serializer.data})


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (OrderingFilter, SearchFilter)
    pagination_class = None
    filterset_fields = ("tag",)
    search_fields = ("tag",)

    def get_queryset(self):
        return Tag.objects.all()


class ZoneViewset(viewsets.ModelViewSet):
    serializer_class = ZoneSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ZoneListFilter
    search_fields = (
        "zone_name",
        "zone_desc",
        "geofence",
        "project__project_name",
        "project__project_id",
    )
    queryset = Zone.objects.all()

    def get_queryset(self):
        return Zone.objects.filter(project__project_id__in=self.request.user.projects_with_access)

    def get_serializer(self, *args, **kwargs):
        if self.action != "retrieve":
            kwargs["exclude"] = ["remaining_zones"]
        return super().get_serializer(*args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        projects = Project.objects.filter(
            status=ProjectStatus.ACTIVE, project_id__in=self.request.user.projects_with_access
        )
        context["all_projects"] = projects
        context["all_zones"] = Zone.objects.filter(project__in=projects)
        return context

    def paginate_queryset(self, queryset):
        limit = self.request.query_params.get("limit")
        if limit == "all":
            page = None
        else:
            page = super(ZoneViewset, self).paginate_queryset(queryset)
        return page

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def download(self, request):
        report_name = "Zones"
        headers = ["Zone Name", "Zone Description", "Project Id", "Geofence"]
        zones = Zone.objects.select_related("project")
        rows = []
        for zone in zones:
            rows.append(
                [zone.zone_name, zone.zone_desc, zone.project.project_id, zone.geofence.geojson]
            )

        response = generate_excel_report(rows, report_name, headers)
        return response

    @action(methods=["get"], detail=False)
    def display_zones(self, request, *args, **kwargs):
        project_id = request.query_params.get("project_id", None)
        if project_id:
            zones = Zone.objects.filter(project__project_id=project_id)
            zone_section = generate_zone_feature_collections(zones)
            return JsonResponse({"success": True, "zones": zone_section}, status=HTTP_200_OK)
        else:
            return JsonResponse(
                {"success": False, "message": "Project id is required"},
                status=HTTP_400_BAD_REQUEST,
            )


class UserNotificationViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
):
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("is_read",)

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user, is_read=False).order_by(
            "-created"
        )

    @action(methods=["PATCH"], detail=True)
    def mark_as_read(self, request, pk):
        notification_object = UserNotification.objects.get(id=pk)
        notification_object.is_read = True
        notification_object.read_on = timezone.now()
        notification_object.save()

        return JsonResponse(
            {"success": True, "message": "Marked as read successfully."}, status=HTTP_200_OK
        )

    @action(methods=["PATCH"], detail=False)
    def mark_all_as_read(self, request):
        if request.data:
            try:
                for notification_id in request.data:
                    notification_object = UserNotification.objects.get(id=notification_id)
                    notification_object.is_read = True
                    notification_object.read_on = timezone.now()
                    notification_object.save()
            except Exception as e:
                logger.error(e)

            return JsonResponse(
                {"success": True, "message": "All notifications are mark as read successfully"},
                status=HTTP_200_OK,
            )

    @action(methods=["GET"], detail=False)
    def get_notification_count(self, request):
        notifications_count = UserNotification.objects.filter(
            user=self.request.user, is_read=False
        ).count()
        return JsonResponse(
            {
                "success": True,
                "data": notifications_count,
                "message": f"New {notifications_count} notifications found",
            },
            status=HTTP_200_OK,
        )
