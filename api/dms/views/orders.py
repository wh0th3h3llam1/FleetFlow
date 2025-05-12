import json
import logging
import math
import os
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
import django_filters
from dateutil import parser
from django.contrib.gis.geos import Point
from django.db import models
from django.db.models import Q, Sum, When, Case, Value, F
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from common.mixins import CreateListMixin
from common.utils import get_days_hours_minutes
from dms.forms import DeliveryDetailsForm
from dms.helpers import (
    generate_excel_report,
    generate_zone_feature_collections,
    get_vehicle_partition,
)
from dms.models import (
    CustomerAddress,
    ItemMaster,
    Order,
    Project,
    OrderItem,
    OrderNotification,
    Driver,
    Zone,
    OrderAttachment,
    OrderUploadFile,
    ProjectUser,
)
from dms.serializers import (
    CustomerAddressSerializer,
    ItemMasterSerializer,
    BulkUploadOrderItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    BulkUpdateOrderSerializer,
    OrderAttachmentSerializer,
    BulkUploadB2COrderSerializer,
    OrderListSerializer,
)
from dms.tasks import send_notification, orders_bulk_create
from common.choices import PAYMENT_TYPE_CHOICES
from common.constants import (
    ProjectStatus,
    OrderConstants,
    NotificationPriority,
    NotificationCategory,
    NotificationType,
    FieldConstants,
)
from common.osrm import OSRMClient
from dms.filters import ItemMasterListFilter

logger = logging.getLogger(__name__)


class CustomerAddressFilterSet(django_filters.FilterSet):
    project_id = django_filters.CharFilter(method="project_id__in")
    project = django_filters.CharFilter(method="project_id__in")
    ordering = django_filters.OrderingFilter(
        fields=[
            "customer_code",
            "customer_name",
            "customer_type",
            "contact_number",
        ]
    )
    customer_type = django_filters.CharFilter(method="customer_type__in")
    from_time = django_filters.TimeFilter(method="customer_from_time")
    to_time = django_filters.TimeFilter(method="customer_to_time")
    tags = django_filters.CharFilter(method="customer_tags")

    def customer_from_time(self, queryset, key, value):
        try:
            queryset = queryset.filter(time_slots__from_time__gte=value)
        except:
            pass
        return queryset

    def customer_to_time(self, queryset, key, value):
        try:
            queryset = queryset.filter(time_slots__to_time__lte=value)
        except:
            pass
        return queryset

    def customer_tags(self, queryset, key, value):
        try:
            selected_tags = value.split(",")
            queryset = queryset.filter(customer_tags__tag__tag__in=selected_tags)
        except:
            pass
        return queryset

    def customer_type__in(self, queryset, value, *args, **kwargs):
        try:
            if args:
                customer_type = [x.strip() for x in args[0].split(",")]
                queryset = queryset.filter(customer_type__in=customer_type)
        except ValueError:
            pass

        return queryset

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            projects_id_list = args[0]
            if projects_id_list:
                projects_id_list = projects_id_list.split(",")
                queryset = queryset.filter(project__project_id__in=projects_id_list)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = CustomerAddress
        fields = (
            "project_id",
            "ordering",
        )


class OrderFilterSet(django_filters.FilterSet):
    project_id = django_filters.CharFilter(method="project_id__in", label="Project ID")
    payment_type = django_filters.ChoiceFilter(
        choices=PAYMENT_TYPE_CHOICES,
    )
    # status = django_filters.ChoiceFilter(choices=ORDER_STATUS_CHOICES,)
    project = django_filters.CharFilter(method="projects")
    status = django_filters.CharFilter(method="status__in")
    from_date = django_filters.DateFilter(field_name="execution_date", lookup_expr="gte")
    to_date = django_filters.DateFilter(field_name="execution_date", lookup_expr="lte")
    ordering = django_filters.OrderingFilter(
        fields=["customer_name", "reference_number", "status", "execution_date"]
    )

    def status__in(self, queryset, value, *args, **kwargs):
        try:
            statuses = args[0]
            if statuses:
                statuses = statuses.split(",")
                queryset = queryset.filter(status__in=statuses)
        except ValueError:
            pass
        return queryset

    def projects(self, queryset, value, *args, **kwargs):
        try:
            projects_list = args[0]
            if projects_list:
                projects_list = projects_list.split(",")
                queryset = queryset.filter(project__id__in=projects_list)
        except ValueError:
            pass
        return queryset

    def project_id__in(self, queryset, value, *args, **kwargs):
        try:
            projects_id_list = args[0]
            if projects_id_list:
                projects_id_list = projects_id_list.split(",")
                queryset = queryset.filter(project__project_id__in=projects_id_list)
        except ValueError:
            pass
        return queryset

    class Meta:
        model = Order
        fields = (
            "project_id",
            "payment_type",
            "status",
            "project",
            "from_date",
            "to_date",
            "ordering",
        )


class CustomerAddressViewSet(
    CreateListMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = CustomerAddressSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ("customer_code", "address", "customer_name", "project__project_id")
    filterset_class = CustomerAddressFilterSet

    # filterset_fields = ("customer_code", "address", "customer_name", "project")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # context["all_projects"] = Project.objects.filter(status=ProjectStatus.ACTIVE)
        existing_customer_codes = list(
            CustomerAddress.objects.values_list("customer_code", flat=True)
        )
        context["existing_customer_codes"] = existing_customer_codes
        context["all_projects"] = Project.objects.filter(
            Q(status=ProjectStatus.ACTIVE)
            & Q(project_id__in=self.request.user.projects_with_access)
        )
        return context

    def get_serializer(self, *args, **kwargs):
        exclude = []

        if self.action in ["list", "create", "update"]:
            exclude.extend(
                [
                    "projects",
                ]
            )

        if exclude:
            kwargs["exclude"] = exclude
        return super().get_serializer(*args, **kwargs)

    # lookup_field = "customer_code"

    def get_queryset(self):
        # return CustomerAddress.objects.all()
        return CustomerAddress.objects.filter(
            project__project_id__in=self.request.user.projects_with_access
        )

    @action(
        detail=False,
        methods=[
            "post",
        ],
    )
    def exists(self, request):
        existing_customer_codes = list(
            CustomerAddress.objects.values_list("customer_code", flat=True)
        )
        customer_codes = request.data.get("customer_codes")
        if customer_codes:
            customer_codes = customer_codes.split(",")
            non_existing_customer_codes = ",".join(
                [
                    customer_code
                    for customer_code in customer_codes
                    if customer_code not in existing_customer_codes
                ]
            )
            if non_existing_customer_codes:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Some customer codes don't exist.",
                        "data": {"customer_codes": non_existing_customer_codes},
                    },
                    status=HTTP_400_BAD_REQUEST,
                )
            else:
                return JsonResponse(
                    {
                        "success": True,
                        "message": "All customer codes exist.",
                    },
                    status=HTTP_200_OK,
                )
        else:
            return JsonResponse(
                {"message": "Please provide list of customer codes in comma separated form."},
                status=HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], detail=False)
    def get_zone_wise_address(self, request):
        project_id = request.query_params.get("project_id", None)
        if project_id:
            customer_details = []
            try:
                project = Project.objects.get(project_id=project_id)
            except Project.DoesNotExist as e:
                logger.error(e)
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Project with project_id={project_id} not found",
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

            z = Zone.objects.filter(project__project_id=project_id)
            zone_section = generate_zone_feature_collections(z)

            addresses = self.get_queryset().filter(project__project_id=project_id)
            for address in addresses:
                customer_details.append(
                    {
                        "id": address.id,
                        "customer_code": address.customer_code,
                        "customer_name": address.customer_name,
                        "address": address.address,
                        "coordinates": [address.coordinates.x, address.coordinates.y],
                    }
                )
            response_data = {"customer_details": customer_details, "zones": zone_section}
            return JsonResponse(
                {
                    "success": True,
                    "data": response_data,
                },
                status=HTTP_200_OK,
            )
        else:
            return JsonResponse(
                {"success": False, "message": "please provide project id."},
                status=HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def download(self, request):
        project_list = request.query_params.get("project__project_id")
        if not project_list:
            project_list = self.request.user.projects_with_access
        else:
            project_list = project_list.split(",")
        report_name = "Customer Addresses"
        headers = [
            "Customer Code",
            "Customer Name",
            "Customer Type",
            "Contact Person",
            "Customer Number",
            "Contact Email",
            "Project Id",
            "Processing time",
            "Address",
            "Latitude",
            "Longitude",
            "From time",
            "To time",
            "Whatsapp Notification",
            "Email Notification",
        ]
        customer_addresses = (
            CustomerAddress.objects.select_related("project")
            .prefetch_related("time_slots")
            .filter(project__project_id__in=project_list)
        )
        rows = []
        for cust_addr in customer_addresses:
            slot = cust_addr.time_slots.first()
            from_time = to_time = lat = lng = ""
            if cust_addr.coordinates:
                lat = cust_addr.coordinates.y
                lng = cust_addr.coordinates.x
            if slot:
                from_time = slot.from_time.strftime(FieldConstants.TIME_FORMAT)
                to_time = slot.to_time.strftime(FieldConstants.TIME_FORMAT)

            rows.append(
                [
                    cust_addr.customer_code,
                    cust_addr.customer_name,
                    cust_addr.customer_type,
                    cust_addr.contact_person,
                    cust_addr.contact_number,
                    cust_addr.contact_email,
                    cust_addr.project.project_id,
                    cust_addr.processing_time,
                    cust_addr.address,
                    lat,
                    lng,
                    from_time,
                    to_time,
                    "yes" if cust_addr.whatsapp_notification else "no",
                    "yes" if cust_addr.email_notification else "no",
                ]
            )

        response = generate_excel_report(rows, report_name, headers)
        return response


class ItemMasterViewSet(
    CreateListMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = ItemMasterSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_class = ItemMasterListFilter
    search_fields = ("item_no", "storage_type", "unit")
    renderer_classes = [
        JSONRenderer,
    ]
    parser_classes = [
        JSONParser,
    ]

    def get_queryset(self):
        return ItemMaster.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        existing_item_nos = {
            item["item_no"]: item["id"] for item in ItemMaster.objects.values("item_no", "id")
        }
        context["existing_item_nos"] = existing_item_nos
        return context

    @action(detail=False, methods=["post"])
    def exists(self, request):
        existing_item_nos = list(ItemMaster.objects.values_list("item_no", flat=True))
        item_nos = request.data.get("item_numbers")
        if item_nos:
            item_nos = item_nos.split(",")
            non_existing_item_nos = ",".join(
                [item_no for item_no in item_nos if item_no not in existing_item_nos]
            )
            if non_existing_item_nos:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Some item numbers don't exist.",
                        "data": {"item_numbers": non_existing_item_nos},
                    },
                    status=HTTP_400_BAD_REQUEST,
                )
            else:
                return JsonResponse(
                    {
                        "success": True,
                        "message": "All item numbers exist.",
                    },
                    status=HTTP_200_OK,
                )
        else:
            return JsonResponse(
                {"message": "Please provide list of item numbers in comma separated form."},
                status=HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        methods=[
            "get",
        ],
    )
    def download(self, request):
        report_name = "Item Masters"
        headers = [
            "Item name",
            "Item No",
            "Storage Type",
            "Unit",
            "Case Factor",
            "Length",
            "Width",
            "Height",
            "Volume (CBM)",
            "Weight",
        ]
        choice_mapping = {"D": "Dry", "C": "Chilled", "F": "Frozen"}

        unit_mapping = {"kg": "Kg", "each": "Each", "case": "Case"}

        storage_whens = [When(storage_type=k, then=Value(v)) for k, v in choice_mapping.items()]
        unit_whens = [When(unit=k, then=Value(v)) for k, v in unit_mapping.items()]
        item_lists = ItemMaster.objects.annotate(
            v_storage_type=Case(*storage_whens, output_field=models.CharField()),
            v_unit=Case(*unit_whens, output_field=models.CharField()),
        ).values_list(
            "item_description",
            "item_no",
            "v_storage_type",
            "v_unit",
            "case_factor",
            "length",
            "width",
            "height",
            "cbm",
            "weight",
        )
        response = generate_excel_report(item_lists, report_name, headers)

        return response


class BulkUploadOrderItemView(APIView):
    http_method_names = [
        "post",
    ]
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer_kwargs = {}
        if isinstance(request.data, list):
            serializer_kwargs.update({"many": True})
        context = {
            "request": request,
            "item_nos": ItemMaster.objects.values_list("item_no", flat=True),
            "customer_codes": CustomerAddress.objects.values_list("customer_code", flat=True),
        }
        serializer = BulkUploadOrderItemSerializer(
            data=request.data, context=context, **serializer_kwargs
        )
        if serializer.is_valid():
            order_dtl = {}
            processed_orders = []

            for i, line_dtl in enumerate(serializer.data):
                customer_code = line_dtl["customer_code"]
                item_no = line_dtl["item_no"]
                ref_no = line_dtl["reference_number"]

                if ref_no not in processed_orders:
                    order_dtl.update(
                        {
                            ref_no: {
                                "reference_number": ref_no,
                                "customer_code": customer_code,
                                "execution_date": line_dtl["delivery_date"],
                                "order_items": [
                                    {"item_no": item_no, "quantity": line_dtl["quantity"]}
                                ],
                                # "unassigned_on": timezone.now()
                            }
                        }
                    )
                    processed_orders.append(ref_no)
                else:
                    order_dtl[ref_no]["order_items"].append(
                        {"item_no": line_dtl["item_no"], "quantity": line_dtl["quantity"]}
                    )
            uploaded_file = OrderUploadFile.objects.create(
                payload=order_dtl, uploaded_by=request.user
            )
            orders_bulk_create.apply_async(args=(uploaded_file.id,))
            return JsonResponse({"message": "File uploaded successfully."}, status=HTTP_200_OK)
        else:
            return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST, safe=False)


class BulkUploadB2COrderView(APIView):

    http_method_names = ("post",)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer_kwargs = {}
        if isinstance(request.data, list):
            serializer_kwargs.update({"many": True})

        context = dict()
        context = {
            "request": request,
            "item_no_list": ItemMaster.objects.values_list("item_no", flat=True),
            "all_projects": Project.objects.filter(
                status=ProjectStatus.ACTIVE, project_id__in=self.request.user.projects_with_access
            ),
        }
        serializer = BulkUploadB2COrderSerializer(
            data=request.data, context=context, **serializer_kwargs
        )

        if serializer.is_valid():

            data = serializer.data
            order_dtl = {}
            processed_orders = []

            for _, line_dtl in enumerate(data):
                contact_number = line_dtl["customer_number"]
                customer_type = line_dtl["customer_type"]
                customer = CustomerAddress.objects.filter(
                    contact_number=contact_number, customer_type=customer_type
                ).last()
                customer_code = customer.customer_code
                item_no = line_dtl["item_no"]
                ref_no = line_dtl["reference_number"]

                if ref_no not in processed_orders:
                    order_dtl.update(
                        {
                            ref_no: {
                                "reference_number": ref_no,
                                "customer_code": customer_code,
                                "execution_date": line_dtl["delivery_date"],
                                "order_items": [
                                    {"item_no": item_no, "quantity": line_dtl["quantity"]}
                                ],
                            }
                        }
                    )
                    processed_orders.append(ref_no)
                else:
                    order_dtl[ref_no]["order_items"].append(
                        {"item_no": line_dtl["item_no"], "quantity": line_dtl["quantity"]}
                    )
            uploaded_file = OrderUploadFile.objects.create(
                payload=order_dtl, uploaded_by=request.user
            )
            orders_bulk_create.apply_async(args=(uploaded_file.id,))
            return JsonResponse({"message": "File uploaded successfully."}, status=HTTP_200_OK)
        return JsonResponse(data=serializer.errors, status=HTTP_400_BAD_REQUEST, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class UpdateDeliveryDetails(FormView):
    form_class = DeliveryDetailsForm
    template_name = "dms/order_details_share.html"
    context_object_name = "order_object"

    def get_object(self, *args, **kwargs):
        return OrderNotification.objects.get(
            notification_id=self.kwargs.get("notification_id")
        ).order

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        try:
            notification_id = self.kwargs.get("notification_id")
            notification_object = OrderNotification.objects.get(notification_id=notification_id)
            order_object = notification_object.order
        except:
            return context
        context["order_ref_no"] = order_object.reference_number
        context["driver"] = order_object.trip.driver.user.full_name if order_object.trip else ""
        context["last_location"] = order_object.address
        context["curr_location"] = order_object.coordinates
        context["order_type"] = order_object.order_type
        context["notification_id"] = notification_id
        context["customer_name"] = order_object.customer_name
        context["status"] = order_object.status
        context["order_value"] = order_object.order_value
        context["service_type"] = order_object.service_type
        context["contact_email"] = order_object.contact_email
        context["customer_contact_number"] = order_object.contact_number
        context["eta"] = order_object.etc
        if order_object.order_type == OrderConstants.OrderType.DELIVERY:
            coordinates = order_object.drop_point
        else:
            coordinates = order_object.pickup_point
        context["details_form"] = DeliveryDetailsForm(
            initial={
                "address": order_object.address(),
                "lat": coordinates.y if coordinates else "",
                "long": coordinates.x if coordinates else "",
            }
        )

        return context

    def form_valid(self, form):

        from core.models import Notification, UserNotification

        user_notifications = []
        notification_id = self.kwargs.get("notification_id")
        notification_object = OrderNotification.objects.get(notification_id=notification_id)
        order_object = notification_object.order
        remarks = form.cleaned_data["remarks"]
        order_object.order_remarks = remarks
        address = form.cleaned_data.get("address")
        lat = form.cleaned_data["lat"]
        long = form.cleaned_data["long"]
        if order_object.order_type == OrderConstants.OrderType.DELIVERY:
            order_object.drop_address = address
            order_object.drop_point = Point(x=long, y=lat)
        else:
            order_object.pickup_address = address
            order_object.pickup_point = Point(x=long, y=lat)
        order_object.save()
        title = f"{notification_object.order.reference_number}'s location updated"
        message = f" Customer has updated its location for order f{notification_object.order.reference_number}"
        notification = Notification.objects.create(
            title=title,
            message=message,
            priority=NotificationPriority.LOW,
            notification_category=NotificationCategory.ORDER,
            notification_type=NotificationType.SUCCESS,
            expiration_time=timezone.now() + timedelta(days=1),
        )
        project_users = ProjectUser.objects.filter(project=notification_object.order.project)
        for project_user in project_users:
            user_notifications.append(
                UserNotification(user=project_user.user, notification=notification)
            )
        UserNotification.objects.bulk_create(user_notifications)
        return JsonResponse({"status": 200, "message": "Location details updated successfully."})

    def form_invalid(self, form):
        return JsonResponse({"status": 400, "message": form.errors})


class OrderViewSet(
    CreateListMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin,
):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = [
        "project__project_name",
        "reference_number",
        "invoice_number",
        "trip__reference_number",
        "customer_name",
        "status",
        "pickup_address",
        "order_type",
    ]
    filterset_class = OrderFilterSet

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        read_only_fields = None
        exclude = None
        fields = None

        if self.action == "create":
            exclude = [
                "status",
            ]

        if self.action in [
            "list",
        ]:
            fields = (
                "id",
                "reference_number",
                "customer_name",
                "execution_date",
                "order_type",
                "contact_number",
                "total_cbm",
                "total_kg",
                "status",
                "no_of_items",
                "invoice_number",
            )

        if self.action in [
            "retrieve",
        ]:
            exclude = [
                "projects",
            ]

        if fields:
            kwargs["fields"] = fields

        if exclude:
            kwargs["exclude"] = exclude

        if read_only_fields:
            kwargs["read_only_fields"] = read_only_fields

        return self.serializer_class(*args, **kwargs)

    def get_queryset(self):
        return (
            Order.objects.select_related("customer_address")
            .prefetch_related("order_items")
            .filter(project__project_id__in=self.request.user.projects_with_access)
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["all_items"] = ItemMaster.objects.all()
        context.update(
            {
                "all_items": ItemMaster.objects.all(),
                "user": self.request.user,
                "all_projects": Project.objects.filter(
                    Q(status=ProjectStatus.ACTIVE)
                    & Q(project_id__in=self.request.user.projects_with_access)
                ),
                "all_customer_addresses": CustomerAddress.objects.prefetch_related(
                    "time_slots"
                ).filter(project__project_id__in=self.request.user.projects_with_access),
            }
        )
        return context

    @action(methods=["get"], detail=False)
    def routes(self, request, *args, **kwargs):
        orders = []
        trip_route = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {}, "geometry": dict()}],
        }
        base_address_marker = {
            "type": "Feature",
            "properties": {
                "marker-symbol": "warehouse",
                "name": "Warehouse",
            },
            "geometry": {"type": "Point", "coordinates": None},
        }
        route_response = {
            "distance_in_km": None,
            "duration_in_min": None,
            "driving_directions": dict(),
        }
        if request.data:
            for ord_id in request.data:
                orders.append(Order.objects.get(id=ord_id))
            project_base_coordinates = orders[0].project.base_coordinates
            coords = [[project_base_coordinates.x, project_base_coordinates.y]]
            base_address_marker["geometry"]["coordinates"] = [
                project_base_coordinates.x,
                project_base_coordinates.y,
            ]
            trip_route["features"].append(base_address_marker)
            counter = 1
            for order in orders:
                order_marker = {
                    "type": "Feature",
                    "properties": {"name": "Warehouse", "marker-symbol": "1"},
                    "geometry": {"type": "Point", "coordinates": None},
                }
                try:
                    if order.order_type == OrderConstants.OrderType.DELIVERY and order.drop_point:
                        coords.append([order.drop_point.x, order.drop_point.y])
                        order_marker["geometry"]["coordinates"] = [
                            order.drop_point.x,
                            order.drop_point.y,
                        ]
                        order_marker["properties"]["name"] = order.reference_number
                        order_marker["properties"]["marker-symbol"] = counter
                        trip_route["features"].append(order_marker)
                    elif order.pickup_point:
                        coords.append([order.pickup_point.x, order.pickup_point.y])
                        order_marker["geometry"]["coordinates"] = [
                            order.pickup_point.x,
                            order.pickup_point.y,
                        ]
                        order_marker["properties"]["name"] = order.reference_number
                        order_marker["properties"]["marker-symbol"] = counter
                        trip_route["features"].append(order_marker)
                    counter += 1
                except Exception as e:
                    logger.error(e)
                    return JsonResponse(
                        {
                            "success": False,
                            "message": f"No route for f{order.reference_number} due to coordinates not found",
                            "error": e,
                        },
                        status=HTTP_400_BAD_REQUEST,
                    )

            client = OSRMClient()
            result = client.get_trip(
                coords, roundtrip=True, source="first", destination="last", driving_directions=True
            )
            route_response["distance_in_km"] = result["trip_distance_in_km"]
            route_response["duration_in_min"] = result["trip_duration_in_min"]
            if result["driving_directions"]:
                trip_route["features"][0]["geometry"] = result["driving_directions"]
                route_response["driving_directions"] = trip_route

            if route_response:
                return JsonResponse(
                    {
                        "success": True,
                        "data": route_response,
                        "message": "Route generated for given order list.",
                    },
                    status=HTTP_200_OK,
                )
            else:
                return JsonResponse({"message": "No Response"}, status=HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(
                {"message": "Please provide a list of orders"}, status=HTTP_400_BAD_REQUEST
            )

    @action(methods=["post"], detail=True)
    def send_order_notification(self, request, *args, **kwargs):
        order_id = kwargs.get("pk")
        try:
            order_object = Order.objects.get(pk=order_id)
        except Exception as e:
            logger.exception(e)
            return JsonResponse({"status": 404, "message": "No such order found!"})
        else:
            send_notification.apply_async(args=[json.dumps(order_id)])
            return JsonResponse(
                {
                    "success": True,
                    "message": "Order detail sent successfully.",
                },
                status=HTTP_200_OK,
            )

    @action(methods=["post"], detail=False)
    def get_trip_recommendations(self, request, *args, **kwargs):
        order_info_list = []
        warehouse_details = []
        dry_items_cbm = Decimal("0.0")
        chilled_items_cbm = Decimal("0.0")
        frozen_items_cbm = Decimal("0.0")
        dry_case_count = 0
        chilled_case_count = 0
        frozen_case_count = 0
        trip_route = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {}, "geometry": dict()}],
        }
        route_response = {
            "order_details": None,
            "vehicle_partition": None,
            "trip_route": dict(),
            "distance_in_km": None,
            "total_time": None,
            "travelling_time": None,
            "warehouse_details": None,
            "cbm_capacity_exceeds": False,
            "weight_capacity_exceeds": False,
            "vehicle": dict(),
            "total_no_of_items": 0,
            "total_no_of_cases": 0,
            "dry_cases": 0,
            "chilled_cases": 0,
            "frozen_cases": 0,
            "boxes": "",
        }
        if request.data:
            driver = Driver.objects.get(id=request.data.get("driver"))
            vehicle_tonnage_capacity = driver.vehicle_assigned.tonnage_capacity
            vehicle_cbm_capacity = driver.vehicle_assigned.cbm_capacity
            vehicle_box_capacity = driver.vehicle_assigned.box_capacity

            route_response["vehicle"] = {
                "vehicle_plate_no": driver.vehicle_assigned.vehicle_plate_no,
                "tonnage_capacity": vehicle_tonnage_capacity,
                "cbm_capacity": vehicle_cbm_capacity,
            }

            orders = Order.objects.annotate(
                total_weight=Sum("order_items__line_item_weight"),
                total_cbm=Sum("order_items__line_item_cbm"),
            ).filter(id__in=request.data["orders"])
            total_order_weight = orders.aggregate(total_kg=Sum("total_weight")).get("total_kg")
            total_order_volume = orders.aggregate(total_volume=Sum("total_cbm")).get("total_volume")

            route_response["total_weight"] = (
                f"{round(total_order_weight / 1000, 2)} / {vehicle_tonnage_capacity} TON"
            )
            route_response["total_volume"] = (
                f"{round(total_order_volume, 2)} / {vehicle_cbm_capacity} CBM"
            )

            if total_order_volume is not None and total_order_volume > vehicle_cbm_capacity:
                route_response["cbm_capacity_exceeds"] = True
            elif total_order_volume is None:
                route_response["cbm_capacity_exceeds"] = "N/A"
            else:
                route_response["cbm_capacity_exceeds"] = False

            if total_order_weight is not None:
                total_order_weight_in_tonnage = total_order_weight / 1000
                if total_order_weight_in_tonnage > vehicle_tonnage_capacity:
                    route_response["weight_capacity_exceeds"] = True
                else:
                    route_response["weight_capacity_exceeds"] = False
            elif total_order_weight is None:
                route_response["weight_capacity_exceeds"] = "N/A"

            drv_shift_start_time = driver.shift_start
            drv_shift_end_time = driver.shift_end
            project = driver.project
            coords = [[project.base_coordinates.x, project.base_coordinates.y]]
            order_info_list.append(
                {
                    "base_address": "warehouse",
                    "sequence_number": "",
                    "coordinates": [project.base_coordinates.x, project.base_coordinates.y],
                    "address": driver.project.base_address,
                }
            )
            warehouse_details.append(
                {
                    "address": driver.project.base_address,
                    "coordinates": [project.base_coordinates.x, project.base_coordinates.y],
                }
            )

            client = OSRMClient()
            for order in orders:
                dry_items = order.order_items.filter(
                    item__storage_type=OrderConstants.StorageTypes.DRY
                )
                chilled_items = order.order_items.filter(
                    item__storage_type=OrderConstants.StorageTypes.CHILLED
                )
                frozen_items = order.order_items.filter(
                    item__storage_type=OrderConstants.StorageTypes.FROZEN
                )

                dry_items_count = dry_items.count()
                dry_items_total = dry_items.aggregate(
                    cases=Sum("total_cases"), total_cbm=Sum("line_item_cbm")
                )
                dry_items_total_cbm = dry_items_total.get("total_cbm")
                dry_item_cases = dry_items_total.get("cases")
                dry_items_cbm += dry_items_total_cbm if dry_items_total_cbm else Decimal("0.00")
                dry_case_count += dry_item_cases if dry_item_cases else Decimal("0.00")

                chilled_items_count = chilled_items.count()
                chilled_items_total = chilled_items.aggregate(
                    cases=Sum("total_cases"), total_cbm=Sum("line_item_cbm")
                )
                chilled_items_total_cbm = chilled_items_total.get("total_cbm")
                chilled_item_cases = chilled_items_total.get("cases")
                chilled_items_cbm += (
                    chilled_items_total_cbm if chilled_items_total_cbm else Decimal("0.00")
                )
                chilled_case_count += chilled_item_cases if chilled_item_cases else Decimal("0.00")

                frozen_items_count = frozen_items.count()
                frozen_items_total = frozen_items.aggregate(
                    cases=Sum("total_cases"), total_cbm=Sum("line_item_cbm")
                )
                frozen_items_total_cbm = frozen_items_total.get("total_cbm")
                frozen_item_cases = frozen_items_total.get("cases")
                frozen_items_cbm += (
                    frozen_items_total_cbm if frozen_items_total_cbm else Decimal("0.00")
                )
                frozen_case_count += frozen_item_cases if frozen_item_cases else Decimal("0.00")

                total_items_count = order.order_items.count()
                route_response["total_no_of_items"] += order.order_items.aggregate(
                    total_items=Sum("original_quantity")
                ).get("total_items")
                order_item_counts = {
                    "total": total_items_count,
                    "dry": dry_items_count,
                    "chilled": chilled_items_count,
                    "frozen": frozen_items_count,
                }

                route_response["total_no_of_cases"] += order.order_items.aggregate(
                    cases=Sum("total_cases")
                ).get("cases", 0)

                try:
                    coords.append([order.coordinates.x, order.coordinates.y])
                    order_info_list.append(
                        {
                            "id": order.id,
                            "reference_number": order.reference_number,
                            "customer_name": order.customer_name,
                            "total_weight": order.total_weight,
                            "total_cbm": order.total_cbm,
                            "sequence_number": "",
                            "status": order.status,
                            "type": order.order_type,
                            "address": order.address(),
                            "coordinates": [order.coordinates.x, order.coordinates.y],
                            "order_item_counts": order_item_counts,
                            "eta": "",
                        }
                    )
                except Exception as e:
                    logger.error(e)
                    return JsonResponse(
                        {
                            "success": False,
                            "message": f"No Trip Recommendation for f{order.reference_number} due to coordinates not found",
                            "error": e,
                        },
                        status=HTTP_400_BAD_REQUEST,
                    )

            data = {
                "vehicle_cbm_capacity": vehicle_cbm_capacity,
                "frozen_items_cbm": frozen_items_cbm,
                "chilled_items_cbm": chilled_items_cbm,
                "dry_items_cbm": dry_items_cbm,
            }

            vehicle_partition = get_vehicle_partition(data)

            total_items_cbm = frozen_items_cbm + chilled_items_cbm + dry_items_cbm

            used_boxes_capacity = Decimal(total_items_cbm) / Decimal(settings.BOX_UNIT)
            route_response["boxes"] = f"{math.ceil(used_boxes_capacity)}/{vehicle_box_capacity}"
            route_response["dry_cases"] = dry_case_count
            route_response["chilled_cases"] = chilled_case_count
            route_response["frozen_cases"] = frozen_case_count

            result = client.get_trip(
                coords, roundtrip=True, source="first", destination="last", driving_directions=True
            )

            for f, o in zip(order_info_list, result["waypoints"]):
                f["sequence_number"] = o["waypoint_index"]

            sorted_order_list = sorted(order_info_list, key=lambda i: i["sequence_number"])
            warehouse_coords = sorted_order_list.pop(0)

            # order eta calculation logic
            eta_coords = [warehouse_coords["coordinates"]]
            prv_order_processing_time_min = 0

            for order_info in sorted_order_list:
                order_detail = orders.get(id=order_info["id"])
                trip_start_datetime = datetime.combine(
                    order_detail.execution_date, drv_shift_start_time
                )
                # prv_order_processing_time_min += order_detail.processing_time
                prv_order_processing_time_min += order_detail.planned_processing_time
                eta_coords.append(order_info["coordinates"])
                route_result = client.get_route(eta_coords)
                order_eta_min = (
                    math.ceil(route_result["duration_in_min"]) + prv_order_processing_time_min
                )
                order_eta = trip_start_datetime + timedelta(minutes=order_eta_min)
                order_info["eta"] = order_eta.time()
                if (
                    order_eta.time() > drv_shift_start_time
                    and order_eta.time() < drv_shift_end_time
                ):
                    order_info["eta_violation"] = False
                else:
                    order_info["eta_violation"] = True

            route_response["order_details"] = sorted_order_list
            route_response["vehicle_partition"] = vehicle_partition
            route_response["distance_in_km"] = f"{result['trip_distance_in_km']} KMS"

            travelling_time = result["trip_duration_in_min"]
            total_time = result["trip_duration_in_min"] + prv_order_processing_time_min

            route_response["travelling_time"] = get_days_hours_minutes(travelling_time)
            route_response["total_time"] = get_days_hours_minutes(total_time)

            route_response["order_details"] = sorted_order_list
            route_response["warehouse_details"] = warehouse_details
            if result["driving_directions"]:
                trip_route["features"][0]["geometry"] = result["driving_directions"]
                route_response["trip_route"] = trip_route
            return JsonResponse(
                {
                    "success": True,
                    "data": route_response,
                    "message": "Trip recommendations generated",
                },
                status=HTTP_200_OK,
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "No Recommendation found for trip",
                },
                status=HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], detail=False)
    def get_zone_wise_orders(self, request):
        project_id = request.query_params.get("project_id", None)
        if project_id:
            order_details = []
            try:
                project = Project.objects.get(project_id=project_id)
            except Project.DoesNotExist as e:
                logger.error(e)
                return JsonResponse(
                    {
                        "success": False,
                        "message": f"Project with project_id={project_id} not found",
                    },
                    status=HTTP_400_BAD_REQUEST,
                )

            z = Zone.objects.filter(project__project_id=project_id)
            zone_section = generate_zone_feature_collections(z)
            orders = self.get_queryset().filter(project__project_id=project_id)
            for order in orders:
                order_details.append(
                    {
                        "id": order.id,
                        "reference_number": order.reference_number,
                        "customer_name": order.customer_name,
                        "status": order.status,
                        "type": order.order_type,
                        "address": order.address(),
                        "coordinates": [order.coordinates.x, order.coordinates.y],
                    }
                )
            response_data = {"order_details": order_details, "zones": zone_section}
            return JsonResponse({"success": True, "data": response_data}, status=HTTP_200_OK)
        else:
            return JsonResponse(
                {"success": False, "message": "please provide project id."},
                status=HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], detail=False)
    def download(self, request):
        order_filter = {}
        project_id = request.query_params.get("project_id")
        execution_date = request.query_params.get("execution_date")
        if execution_date:
            execution_date = parser.parse(execution_date)
            order_filter.update({"order__execution_date": execution_date})
        if project_id:
            order_filter.update({"order__project__project_id": project_id})
        order_items = (
            OrderItem.objects.select_related("order__project", "item", "order__customer_address")
            .filter(**order_filter)
            .annotate(
                item_no=F("item__item_no"),
                so_number=F("order__reference_number"),
                customer_code=F("order__customer_address__customer_code"),
                quantity=F("original_quantity"),
                order_date=F("order__execution_date"),
            )
        )
        report_name = "Orders"
        headers = ["Item No", "SO Number", "Customer Code", "Delivery Date", "Quantity"]
        rows = []
        for order_item in order_items:
            rows.append(
                [
                    order_item.item_no,
                    order_item.so_number,
                    order_item.customer_code,
                    order_item.order_date.strftime(FieldConstants.DATE_FORMAT),
                    order_item.quantity,
                ]
            )
        response = generate_excel_report(rows, report_name, headers)
        return response

    @action(methods=["delete"], detail=False)
    def delete(self, request):
        order_ids = request.query_params.get("order_ids", None)
        if order_ids:
            orders = order_ids.split(",")
            try:
                response = Order.objects.filter(id__in=orders).delete()
                if response:
                    return JsonResponse(
                        {"success": True, "message": f"Order(s) deleted successfully"},
                        status=HTTP_200_OK,
                    )
            except Exception as e:
                logger.error(e)
        else:
            return JsonResponse(
                {"success": False, "message": f"Please select order to delete."},
                status=HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True)
    def upload_attachments(self, request, *args, **kwargs):
        order_id = kwargs.get("pk", None)

        if order_id:
            try:
                order = Order.objects.prefetch_related("attachments").get(id=order_id)
            except Order.DoesNotExist:
                return JsonResponse({"error": "No Order Found"}, status=HTTP_400_BAD_REQUEST)

            except Exception as e:
                logger.exception(e)
                return JsonResponse(
                    {"error": "Error Uploading Attachment"}, status=HTTP_400_BAD_REQUEST
                )
            try:
                user = request.user
                attachments = request.FILES._getlist("attachments", None)
                attachment_type = request.data.get(
                    "attachment_type", OrderConstants.AttachmentType.ORDER
                )
                order_attachments = [
                    OrderAttachment(
                        order=order,
                        attachment=attachment,
                        attachment_type=attachment_type,
                        uploaded_by=user,
                    )
                    for attachment in attachments
                ]
                created = OrderAttachment.objects.bulk_create(order_attachments)
                return JsonResponse(
                    {"message": "Attachments Uploaded Successfully"}, status=HTTP_200_OK
                )
            except Exception as e:
                logger.exception(e)
                return JsonResponse({"error": "No Order Found"}, status=HTTP_400_BAD_REQUEST)


class OrderItemViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
):
    serializer_class = OrderItemSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("order__id",)

    def get_queryset(self):
        return OrderItem.objects.prefetch_related("order").all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BulkUpdateOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):

        order_update_serializer = BulkUpdateOrderSerializer(data=request.data, many=True)

        if order_update_serializer.is_valid():
            reference_no_list = []
            execution_date_list = []

            for order_detail in order_update_serializer.validated_data:
                reference_no_list.append(order_detail["reference_number"])
                execution_date_list.append(order_detail["execution_date"])

            orders = Order.objects.filter(
                Q(reference_number__in=reference_no_list)
                & Q(execution_date__in=execution_date_list)
            )
            updated_order_list = []

            for order_detail in order_update_serializer.validated_data:
                reference_number = order_detail.get("reference_number")
                execution_date = order_detail.get("execution_date")

                invoice_number = order_detail.get("invoice_number")
                payment_type = order_detail.get("payment_type")
                require_proof_of_delivery = order_detail.get("require_proof_of_delivery")
                order_value = order_detail.get("order_value")
                from_time = order_detail.get("from_time")
                to_time = order_detail.get("to_time")

                try:
                    order = orders.get(
                        Q(reference_number=reference_number) & Q(execution_date=execution_date)
                    )
                except Order.DoesNotExist as e:
                    logger.info(
                        f"Order with reference number {reference_number} does not exist so skipping the invoice number update for it."
                    )
                except Exception as e:
                    logger.exception(e)
                else:
                    order.invoice_number = invoice_number
                    if from_time:
                        order.delivery_window_start = from_time
                    if to_time:
                        order.delivery_window_end = to_time
                    if type(require_proof_of_delivery) is bool:
                        order.require_proof_of_delivery = require_proof_of_delivery
                    if payment_type:
                        order.payment_type = payment_type

                    order.order_value = order_value
                    updated_order_list.append(order)

            fields_to_be_updated = [
                "invoice_number",
                "require_proof_of_delivery",
                "payment_type",
                "order_value",
                "delivery_window_end",
                "delivery_window_start",
            ]

            updated_orders = Order.objects.bulk_update(updated_order_list, fields_to_be_updated)
            return JsonResponse(
                {
                    "message": "Orders will be created shortly.",
                    "data": order_update_serializer.data,
                    "success": True,
                },
                status=HTTP_200_OK,
                safe=False,
            )

        else:
            return JsonResponse(
                order_update_serializer.errors, status=HTTP_400_BAD_REQUEST, safe=False
            )


class OrderAttachmentViewSet(
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderAttachmentSerializer
    permission_classes = (IsAuthenticated,)
    queryset = OrderAttachment.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        response = self.perform_destroy(instance)
        if response:
            return JsonResponse(
                {"message": "Attachment Deleted Successfully"}, status=HTTP_204_NO_CONTENT
            )
        else:
            return JsonResponse({"message": "Attachment Not deleted"}, status=HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        file_path = instance.attachment.path
        try:
            os.remove(file_path)
        except Exception as e:
            logger.exception(e)
            return False
        else:
            instance.delete()
            return True


class OrderListView(ListAPIView):
    serializer_class = OrderListSerializer
    queryset = Order.objects.all()

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
