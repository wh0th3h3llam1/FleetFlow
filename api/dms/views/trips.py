import logging
import os
from copy import deepcopy

from django.conf import settings
from django.db.models import Case, When, BooleanField, Q, F, Sum, Count, Value
from django.db.models.functions import Concat
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import pandas as pd
import pytz

from common.constants import OrderConstants, TripTemperatureFileStatus, FieldConstants
from common.mixins import CreateListMixin
from dms.filters import TripFilter
from dms.models import (
    Trip,
    Order,
    TripChatLog,
    Driver,
    TripTemperatureLog,
    OrderItem,
    TripTemperatureFile,
    VehicleStorage,
)
from dms.serializers import (
    TripSerializer,
    OrderSerializer,
    TripTemperatureSerializer,
    TripLoadSheetSerializer,
    TripMapRouteSerializer,
    TripChatLogSerializer,
)


logger = logging.getLogger(__name__)


class TripOrdersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ("project__project_id", "execution_date")

    def get_queryset(self):
        return Order.objects.filter(status="unassigned")

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        read_only_fields = None
        exclude = None
        fields = None
        if self.action == "list":
            fields = [
                "id",
                "reference_number",
                "customer_name",
                "order_type",
                "execution_date",
                "status",
                "total_kg",
                "total_cbm",
                "address",
            ]

        if fields:
            kwargs["fields"] = fields

        if exclude:
            kwargs["exclude"] = exclude

        if read_only_fields:
            kwargs["read_only_fields"] = read_only_fields

        return self.serializer_class(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TripViewSet(
    CreateListMixin,
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = TripSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = TripFilter
    search_fields = ("reference_number", "driver__user__first_name", "vehicle__vehicle_plate_no")
    lookup_field = "trip_id"

    def get_queryset(self):
        return (
            Trip.objects.prefetch_related("trip_coordinates", "trip_orders")
            .select_related("driver", "vehicle")
            .filter(driver__project__project_id__in=self.request.user.projects_with_access)
        )

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        kwargs["context"] = self.get_serializer_context()
        read_only_fields = None
        exclude = None

        if self.action == "create":
            exclude = [
                "status",
                "trip_start",
                "added_by",
                "planned_distance",
                "planned_start_time",
                "planned_end_time",
                "travelling_time",
                "trip_end",
                "added_by",
                "vehicle",
            ]

        if self.action == "update" or self.action == "partial_update":
            exclude = [
                "trip_start",
                "added_by",
                "planned_distance",
                "planned_start_time",
                "planned_end_time",
                "travelling_time",
                "trip_end",
                "added_by",
                "vehicle",
            ]

        if self.action == "list":
            exclude = [
                "trip_start",
                "added_by",
                "planned_distance",
                "planned_start_time",
                "planned_end_time",
                "travelling_time",
                "trip_end",
                "added_by",
                "orders",
                "trip_orders",
                "logs",
                "trip_route",
                "location",
                "modified",
                "added_by",
                "project_name",
                "trip_orders",
                "helper_name",
                "planned_trip_duration",
                "actual_trip_duration",
                "order_count",
                "orders",
                "project_id",
                "driver_location",
                "trip_statistics",
                "locations",
                "vehicle_make",
                "actual_distance",
                "trip_start_km",
                "trip_end_km",
            ]

        if exclude:
            kwargs["exclude"] = exclude

        if read_only_fields:
            kwargs["read_only_fields"] = read_only_fields

        return self.serializer_class(*args, **kwargs)

    def get_object(self):
        url_kwargs = self.kwargs[self.lookup_field]
        pk = Trip.get_trip_pk(url_kwargs)
        self.lookup_field = "id"
        self.kwargs[self.lookup_field] = pk
        return super(TripViewSet, self).get_object()

    @action(methods=["get"], detail=True)
    def generate_trip_sheet(self, request, *args, **kwargs):
        trip_id = kwargs.get("trip_id")

        trip = Trip.objects.get(id=trip_id)
        orders = trip.trip_orders.all().order_by("sequence_number")

        context = {
            "current_trip": trip,
            "orders": orders,
            "vehicle": trip.vehicle,
        }

        pdf_template_name = "html_to_pdf_2.html"
        pdf_template = render_to_string(f"dms/{pdf_template_name}", context)

        file_name = settings.BASE_DIR + "/temp/trip_sheet.html"

        if os.path.exists(file_name):
            os.remove(file_name)

        with open(file_name, "w+") as f:
            f.write(pdf_template)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="trip_sheet.pdf"'

        return response

    @action(methods=["get"], detail=False)
    def trip_load_sheet(self, request):
        data = list()
        projects = self.request.user.projects_with_access
        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)
        if start_date and end_date:
            trips = (
                Trip.objects.select_related("vehicle", "driver")
                .prefetch_related("trip_orders")
                .filter(
                    trip_date__range=[start_date, end_date],
                    vehicle__project__project_id__in=projects,
                )
            )
            for trip in trips:
                data.append(
                    {
                        "vehicle": trip.vehicle.vehicle_plate_no,
                        "driver": trip.driver.user.full_name,
                        "sales_order": ",".join(
                            [order.reference_number for order in trip.trip_orders.all()]
                        ),
                    }
                )
            return JsonResponse(data, safe=False, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {
                    "message": "Please provide start date and end date",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], detail=True)
    def load_sheet(self, request, trip_id):
        # Frozen / Chilled / Dry / Order Info
        orders = (
            Order.objects.prefetch_related("order_items")
            .select_related("trip__vehicle", "trip__driver__user", "customer_address")
            .filter(trip__id=trip_id)
            .annotate(
                vehicle_number=F("trip__vehicle__vehicle_plate_no"),
                driver_name=Concat(
                    F("trip__driver__user__first_name"),
                    Value(" "),
                    F("trip__driver__user__last_name"),
                ),
                total_items=Sum("order_items__original_quantity"),
                dry_items=Sum(
                    "order_items__original_quantity",
                    filter=Q(order_items__item__storage_type=OrderConstants.StorageTypes.DRY),
                ),
                frozen_items=Sum(
                    "order_items__original_quantity",
                    filter=Q(order_items__item__storage_type=OrderConstants.StorageTypes.FROZEN),
                ),
                chilled_items=Sum(
                    "order_items__original_quantity",
                    filter=Q(order_items__item__storage_type=OrderConstants.StorageTypes.CHILLED),
                ),
            )
        )
        return Response(
            data=TripLoadSheetSerializer(orders, many=True).data, status=status.HTTP_200_OK
        )

    @action(methods=["get"], detail=True)
    def trip_sheet(self, request, trip_id):
        # Order / Item Details
        trips = Trip.objects.prefetch_related("trip_orders").filter(id=trip_id)
        trip = trips.first()
        total_customers = trips.aggregate(
            total_drop_points_count=Count("trip_orders__customer_address", distinct=True)
        ).get("total_drop_points_count", 0)

        trip_serializer_fields = ("reference_number", "driver", "vehicle_info", "trip_date")

        trip_details = TripSerializer(trip, fields=trip_serializer_fields).data

        partitions = trip.trip_order_partition()

        order_serializer_fields = (
            "sequence_number",
            "reference_number",
            "order_items",
            "execution_date",
            "order_type",
            "order_remarks",
            "order_value",
            "payment_type",
            "items",
            "pickup_address",
            "drop_address",
            "no_of_items",
            "pickup_point",
            "invoice_number",
            "payment_type",
            "processing_time",
            "customer_name",
            "contact_person",
            "contact_number",
        )

        orders = OrderSerializer(
            instance=trip.trip_orders.all().order_by("sequence_number"),
            many=True,
            fields=order_serializer_fields,
        ).data

        order_items = (
            OrderItem.objects.filter(order__trip=trip)
            .annotate(
                item_no=F("item__item_no"),
                invoice_number=F("order__invoice_number"),
                item_description=F("item__item_description"),
                storage_type=F("item__storage_type"),
                total_quantity=Sum("original_quantity"),
            )
            .order_by("storage_type")
        )

        trip_total_quantity = 0
        for item in order_items:
            trip_total_quantity += item.total_quantity

        sku_items = []
        storage_type_mapping = {
            OrderConstants.StorageTypes.DRY: "Dry",
            OrderConstants.StorageTypes.FROZEN: "Frozen",
            OrderConstants.StorageTypes.CHILLED: "Chilled",
        }
        for item in order_items:
            sku_items.append(
                {
                    "item_no": item.item_no,
                    "invoice_number": item.invoice_number,
                    "item_description": item.item_description,
                    "storage_type": storage_type_mapping.get(item.storage_type),
                    "total_quantity": item.total_quantity,
                }
            )
        data = {
            "trip_details": trip_details,
            "total_customers": total_customers,
            "partitions": partitions,
            "orders": orders,
            "trip_total_quantity": trip_total_quantity,
            "order_items": sku_items,
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=True)
    def temperature_log(self, request, trip_id):

        try:
            trip = Trip.objects.select_related("vehicle").get(id=trip_id)
            vehicle = trip.vehicle
            storages = VehicleStorage.objects.filter(vehicle=vehicle)
            queryset = (
                TripTemperatureLog.objects.select_related("sensor")
                .filter(Q(timestamp__range=[trip.trip_start, trip.trip_end]))
                .annotate(storage_type=F("sensor__storage_type"))
                .order_by("timestamp")
            )

            if not queryset:
                return JsonResponse(
                    {"message": f"No Temperature Data found for Trip {trip_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Trip.DoesNotExist as tdne:
            logger.exception(tdne)
            return JsonResponse(
                {"message": f"No Trip found with id {trip_id}"}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.exception(e)
            return JsonResponse({"message": "Error Occured"}, status=status.HTTP_400_BAD_REQUEST)

        time_range_frequency = "1min"

        timeline = pd.date_range(trip.trip_start, trip.trip_end, freq=time_range_frequency, tz=None)
        timeline = timeline.tz_convert(pytz.timezone(settings.TIME_ZONE))
        timeline = [time.strftime(FieldConstants.FULL_TIME_FORMAT) for time in timeline]

        dry = queryset.filter(storage_type=OrderConstants.StorageTypes.DRY)
        chilled = queryset.filter(storage_type=OrderConstants.StorageTypes.CHILLED)
        frozen = queryset.filter(storage_type=OrderConstants.StorageTypes.FROZEN)

        data = {
            "timeline": timeline,
            "dry": TripTemperatureSerializer(dry, many=True).data,
            "chilled": TripTemperatureSerializer(chilled, many=True).data,
            "frozen": TripTemperatureSerializer(frozen, many=True).data,
        }
        return JsonResponse(data=data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def bulk_upload_temperature_sheet(self, request):
        files = request.FILES._getlist("files", None)
        user = request.user
        temp_file_obj = [
            TripTemperatureFile(
                uploaded_filename=file.name,
                file_name=file,
                status=TripTemperatureFileStatus.NOT_PROCESSED,
                processed=False,
                added_by=user,
            )
            for file in files
        ]

        try:
            if temp_file_obj:
                TripTemperatureFile.objects.bulk_create(temp_file_obj)
                return JsonResponse(
                    {"message": "Files Uploaded Successfully"}, status=status.HTTP_200_OK
                )
            else:
                return JsonResponse(
                    {"message": "No Files for upload"}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.exception(e)
            return JsonResponse(
                {"error": f"Error Occured: {e}"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["get"], detail=True)
    def map_route(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        trip_id = kwargs.get("trip_id", None)

        if trip_id:
            try:
                trip = queryset.get(id=trip_id)
            except Trip.DoesNotExist as tdne:
                logger.exception(tdne)
                return JsonResponse(
                    {"message": f"No Trip found with id {trip_id}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = TripMapRouteSerializer(instance=trip)

            return JsonResponse({"data": serializer.data}, status=status.HTTP_200_OK)

        return JsonResponse({"message": "No Trip id provided"}, status=status.HTTP_400_BAD_REQUEST)


class TripChatLogViewSet(ListCreateAPIView):
    serializer_class = TripChatLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        driver = None
        try:
            driver = Driver.objects.get(id=self.kwargs.get("driver_id"))
        except Exception as e:
            logger.exception(e)

        if driver:
            return (
                TripChatLog.objects.filter(driver=driver)
                .annotate(
                    send_by_driver=Case(
                        When(Q(sender__username=driver.user.username), then=True),
                        output_field=BooleanField(),
                        default=False,
                    )
                )
                .order_by("-created")
            )
        return TripChatLog.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        trip = None
        driver = Driver.objects.get(id=self.kwargs.get("driver_id"))
        try:
            trip = driver.current_trip
        except AttributeError as e:
            trip = driver.upcoming_trip
        except Exception as e:
            logger.exception(e)
        if trip:
            context["trip"] = trip
        context["driver"] = driver
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer_data = deepcopy(serializer.data)
        serializer_data["send_by_driver"] = False
        headers = self.get_success_headers(serializer.data)
        return Response(serializer_data, status=status.HTTP_201_CREATED, headers=headers)
