from datetime import timedelta

from django.db import models
from django.db.models import Case, When, F, Q, Count
from django.http import JsonResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.constants import DriverStatus, TripStatus, OrderConstants
from dms.helpers import get_operations_drivers
from dms.models import Trip, Order, TripMetrics
from dms.serializers import (
    DriverListSerializer,
    TripDetailSerializer,
    OperationOrderDetailSerializer,
)


class DriverListView(ListAPIView):
    serializer_class = DriverListSerializer
    permissions_classes = (IsAuthenticated,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ("project__project_id",)
    search_fields = ("status", "id", "user__username", "user__first_name", "user__last_name")

    def get_queryset(self):
        projects = self.request.query_params.get("projects")
        if projects:
            projects = projects.split(",")
        else:
            projects = self.request.user.projects_with_access
        drivers = get_operations_drivers(projects=projects)

        return drivers

    def get_serializer_context(self):
        context = super().get_serializer_context()
        fifteen_mins_ago = timezone.now() - timedelta(minutes=15)
        context["all_driver_locations"] = TripMetrics.objects.filter(
            timestamp__gte=fifteen_mins_ago
        )
        return context


class TripDetailView(RetrieveAPIView):
    serializer_class = TripDetailSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    lookup_url_kwarg = "trip_id"

    def get_queryset(self):
        return Trip.objects.prefetch_related("trip_orders", "driver__project").filter(
            status__in=[TripStatus.SCHEDULED, TripStatus.ACTIVE, TripStatus.PAUSED],
            driver__project__project_id__in=self.request.user.projects_with_access,
        )

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        orders = (
            Order.objects.select_related("trip__driver__user")
            .prefetch_related("order_items")
            .filter(trip=args[0], project__project_id__in=self.request.user.projects_with_access)
            .annotate(
                reason=Case(
                    When(Q(status_keyword__isnull=False), then=F("status_keyword__name")),
                    default=None,
                    output_field=models.CharField(),
                ),
                driver_name=Case(
                    When(Q(trip__isnull=False), then=F("trip__driver__user__first_name")),
                    default=None,
                    output_field=models.CharField(),
                ),
            )
            .order_by("sequence_number")
        )
        context["trip_orders"] = orders
        kwargs.setdefault("context", context)
        return serializer_class(*args, **kwargs)


class OperationOverview(APIView):
    permission_classes = [IsAuthenticated]
    filterset_fields = ("execution_date", "project_id")

    def get(self, request, *args, **kwargs):
        project_id_list = request.user.projects_with_access
        trips = (
            Trip.objects.select_related("driver__project")
            .filter(
                Q(status__in=[TripStatus.SCHEDULED, TripStatus.ACTIVE, TripStatus.PAUSED])
                | Q(trip_date=timezone.now().date())
            )
            .filter(driver__project__project_id__in=project_id_list)
        )
        orders = (
            Order.objects.select_related("trip__driver__user")
            .prefetch_related("order_items")
            .filter(
                Q(trip__in=trips)
                | Q(
                    Q(execution_date=timezone.now().date())
                    & Q(project__project_id__in=project_id_list)
                )
            )
            .annotate(
                reason=Case(
                    When(Q(status_keyword__isnull=False), then=F("status_keyword__name")),
                    default=None,
                    output_field=models.CharField(),
                ),
                driver_name=Case(
                    When(Q(trip__isnull=False), then=F("trip__driver__user__first_name")),
                    default=None,
                    output_field=models.CharField(),
                ),
            )
            .order_by("sequence_number")
        )
        drivers = get_operations_drivers(projects=project_id_list)
        successful_statuses = [
            OrderConstants.OrderStatus.SUCCESSFUL,
            OrderConstants.OrderStatus.PARTIAL,
        ]

        data = {
            "orders": OperationOrderDetailSerializer(orders, many=True).data,
            **drivers.aggregate(
                idle_drivers=Count(
                    "id", filter=(Q(working=False) & Q(status=DriverStatus.ON_DUTY))
                ),
                offline_drivers_with_trip=Count(
                    "id", filter=(Q(working=True) & Q(status=DriverStatus.OFF_DUTY))
                ),
                total_drivers=Count("id"),
                offline_drivers=Count(
                    "id", filter=(Q(working=False, status=DriverStatus.OFF_DUTY))
                ),
            ),
            **orders.aggregate(
                unassigned_orders_count=Count(
                    "id", filter=Q(status=OrderConstants.OrderStatus.UNASSIGNED)
                ),
                successful_orders_count=Count("id", filter=Q(status__in=successful_statuses)),
                failed_orders_count=Count("id", filter=Q(status=OrderConstants.OrderStatus.FAILED)),
                unattempted_orders_count=Count(
                    "id",
                    filter=~Q(
                        status__in=[
                            OrderConstants.OrderStatus.UNASSIGNED,
                            OrderConstants.OrderStatus.FAILED,
                            *successful_statuses,
                        ]
                    ),
                ),
            ),
        }
        return JsonResponse(data, status=status.HTTP_200_OK)
