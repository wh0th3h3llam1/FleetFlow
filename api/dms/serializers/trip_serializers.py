import logging
import math
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Sum, Q
from django.utils import timezone

from rest_framework import serializers
from dateutil import tz

from common.constants import (
    OrderConstants,
    TripStatus,
    TripStatusLogs,
    DriverStatus,
    FieldConstants,
)
from common.osrm import OSRMClient
from core.serializers import DynamicFieldsModelSerializer
from dms.models import (
    Trip,
    Order,
    Driver,
    TripLog,
    TripMetrics,
    TripTemperatureLog,
    TripTemperatureFile,
)
from dms.serializers import OrderSerializer
from users.models import User

logger = logging.getLogger(__name__)


class TripLogSerializer(DynamicFieldsModelSerializer):

    def to_representation(self, instance: Trip):
        representation = super().to_representation(instance=instance)
        representation["added_by"] = instance.added_by.full_name
        return representation

    class Meta:
        model = TripLog
        fields = ("message", "added_by", "created")


class TripSerializer(DynamicFieldsModelSerializer):
    orders = serializers.SlugRelatedField(
        write_only=True, many=True, slug_field="id", queryset=Order.objects.all(), required=True
    )
    added_by = serializers.SlugRelatedField(slug_field="id", queryset=User.objects.all())
    driver = serializers.SlugRelatedField(
        slug_field="id", queryset=Driver.active_manager.all(), required=False
    )
    # vehicle = serializers.SlugRelatedField(slug_field='id', queryset=Vehicle.objects.all())
    trip_orders = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    project_id = serializers.SerializerMethodField()
    logs = TripLogSerializer(many=True, read_only=True)
    trip_statistics = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField(read_only=True)
    planned_trip_duration = serializers.SerializerMethodField(read_only=True)
    actual_trip_duration = serializers.SerializerMethodField(read_only=True)
    trip_route = serializers.SerializerMethodField(read_only=True)
    locations = serializers.SerializerMethodField(read_only=True)
    driver_location = serializers.SerializerMethodField(read_only=True)
    pod_attachments = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()

    def get_vehicle_info(self, instance: Trip):
        from dms.serializers import VehicleSerializer

        return VehicleSerializer(
            instance.vehicle,
            fields=(
                "vehicle_plate_no",
                "vehicle_make",
                "vehicle_model",
                "cbm_capacity",
                "tonnage_capacity",
                "storages",
            ),
        ).data

    def get_trip_statistics(self, instance: Trip):
        usage = instance.trip_orders.all().aggregate(
            total_quantity=Sum("order_items__original_quantity"),
            total_cbm=Sum("order_items__line_item_cbm"),
            total_weight=Sum("order_items__line_item_weight"),
            planned_processing_time=Sum("planned_processing_time"),
            actual_processing_time=Sum("processing_time"),
            total_cases=Sum("order_items__total_cases"),
        )
        try:
            volume_fill_ratio = round(usage["total_cbm"] * 100 / instance.vehicle.cbm_capacity, 2)
            weight_fill_ratio = round(
                usage["total_weight"] * 100 / (instance.vehicle.tonnage_capacity * 1000), 2
            )
        except Exception as e:
            logger.exception(e)

            volume_fill_ratio = "N/A"
            weight_fill_ratio = "N/A"

        trip_statistics = {
            "total_items": usage["total_quantity"],
            "volume_utilization": volume_fill_ratio,
            "tonnage_utilization": weight_fill_ratio,
            "partitions": instance.trip_order_partition(),
            "planned_processing_time": usage["planned_processing_time"],
            "actual_processing_time": usage["actual_processing_time"],
            "total_cases": usage["total_cases"],
        }
        total_timings = instance.processing_time + instance.break_time + instance.travelling_time
        processing_time_perc = 0
        travelling_time_perc = 0
        break_time_perc = 0
        if instance.processing_time:
            processing_time_perc = (instance.processing_time * 100) / total_timings
        if instance.break_time:
            break_time_perc = (instance.break_time * 100) / total_timings
        if instance.travelling_time:
            travelling_time_perc = (instance.travelling_time * 100) / total_timings
        trip_statistics.update(
            {
                "timings": {
                    "processing_time_perc": processing_time_perc,
                    "processing_time": instance.processing_time,
                    "break_time": instance.break_time,
                    "break_time_perc": break_time_perc,
                    "travelling_time": instance.travelling_time,
                    "travelling_time_perc": travelling_time_perc,
                }
            }
        )
        return trip_statistics

    def get_driver_location(self, instance: Trip):
        driver_details = {
            "name": instance.driver.user.full_name,
            "location": None,
            "timestamp": None,
        }
        if (
            instance.last_driver_location
            and instance.status in [TripStatus.ACTIVE, TripStatus.PAUSED]
            and instance.driver.status == DriverStatus.ON_DUTY
        ):
            try:
                driver_location = instance.last_driver_location
                loc = driver_location.coordinates
                ts = driver_location.timestamp
                location = [loc.x, loc.y]

                driver_details["location"] = location
                driver_details["timestamp"] = ts.strftime(FieldConstants.DATE_TIME_FORMAT)
                return driver_details

            except AttributeError as ae:
                logger.exception(ae)
            except TripMetrics.DoesNotExist as tmdne:
                logger.exception(tmdne)

        return driver_details

    def get_pod_attachments(self, obj: Trip):
        orders = Order.objects.prefetch_related("attachments").filter(
            Q(trip=obj) & Q(attachments__isnull=False)
        )
        pod_attachments = list()
        for order in orders:
            pod_attachments.append(order.attachments.filter(attachment_type="pod").last())
        return [
            {
                "url": (
                    self.context["request"].build_absolute_uri(order_attachment.attachment.url)
                    if order_attachment.attachment
                    else None
                ),
                "name": order_attachment.attachment.name.split("/")[-1],
            }
            for order_attachment in pod_attachments
        ]

    def get_order_count(self, obj: Trip):
        trip_orders = obj.trip_orders.all()
        successful = trip_orders.filter(status=OrderConstants.OrderStatus.SUCCESSFUL)
        partially_delivered = trip_orders.filter(status=OrderConstants.OrderStatus.PARTIAL)
        failed = trip_orders.filter(status=OrderConstants.OrderStatus.FAILED)
        cancelled = trip_orders.filter(status=OrderConstants.OrderStatus.CANCELLED)
        return {
            "total": trip_orders.count(),
            "successful": successful.count(),
            "partially_delivered": partially_delivered.count(),
            "failed": failed.count(),
            "cancelled": cancelled.count(),
        }

    def get_trip_orders(self, instance):
        return OrderSerializer(
            instance=instance.trip_orders.prefetch_related("project")
            .order_by("sequence_number")
            .all(),
            many=True,
            exclude=["projects", "logs"],
            context=self.context,
        ).data

    def get_planned_trip_duration(self, instance):
        if instance.planned_start_time and instance.planned_end_time:
            total_duration = instance.planned_end_time - instance.planned_start_time
            h = int(total_duration.total_seconds() // 3600)
            m = int(total_duration.total_seconds() % 3600 // 60)
            return "{} Hours {} Minutes".format(h, m)
        else:
            return "00:00"

    def get_actual_trip_duration(self, instance):
        if instance.trip_start and instance.trip_end:
            total_duration = instance.trip_end - instance.trip_start
            h = int(total_duration.total_seconds() // 3600)
            m = int(total_duration.total_seconds() % 3600 // 60)
            return "{} Hours {} Minutes".format(h, m)
        else:
            return "00:00"

    def get_trip_route(self, instance):
        trip_route = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {}, "geometry": dict()}],
        }
        orders = instance.trip_orders.all().order_by("sequence_number")
        if orders:
            project_base_coordinates = orders.first().project.base_coordinates
            coords = [[project_base_coordinates.x, project_base_coordinates.y]]
            for order in orders:
                try:
                    if order.order_type == OrderConstants.OrderType.DELIVERY and order.drop_point:
                        coords.append([order.drop_point.x, order.drop_point.y])
                    elif order.pickup_point:
                        coords.append([order.pickup_point.x, order.pickup_point.y])
                except Exception as e:
                    logger.exception(e)
            coords.append([project_base_coordinates.x, project_base_coordinates.y])
            try:
                client = OSRMClient()
                result = client.get_route(coords, driving_directions=True)
            except Exception as e:
                logger.exception(e)
            trip_route["features"][0]["geometry"] = result["driving_directions"]
            return trip_route

    def get_locations(self, instance):
        orders = instance.trip_orders.all().order_by("sequence_number")
        if orders:
            locations = []
            project = orders.first().project
            project_base_coordinates = project.base_coordinates
            for order in orders:
                coordinates = None
                address = None
                if order.order_type == OrderConstants.OrderType.DELIVERY and order.drop_point:
                    coordinates = [order.drop_point.x, order.drop_point.y]
                    address = order.drop_address
                elif order.pickup_point:
                    coordinates = [order.pickup_point.x, order.pickup_point.y]
                    address = order.pickup_address
                if coordinates:
                    est_time = order.etc
                    events_info = {
                        "assigned_on": (
                            order.assigned_on.astimezone(tz.gettz(settings.TIME_ZONE)).strftime(
                                FieldConstants.FULL_DATE_TIME_FORMAT
                            )
                            if order.assigned_on
                            else "N/A"
                        ),
                        "picked_up_on": (
                            order.picked_up_on.astimezone(tz.gettz(settings.TIME_ZONE)).strftime(
                                FieldConstants.FULL_DATE_TIME_FORMAT
                            )
                            if order.picked_up_on
                            else "N/A"
                        ),
                        "completed_on": (
                            order.completed_on.astimezone(tz.gettz(settings.TIME_ZONE)).strftime(
                                FieldConstants.FULL_DATE_TIME_FORMAT
                            )
                            if order.completed_on
                            else "N/A"
                        ),
                        "failed_on": (
                            order.failed_on.astimezone(tz.gettz(settings.TIME_ZONE)).strftime(
                                FieldConstants.FULL_DATE_TIME_FORMAT
                            )
                            if order.failed_on
                            else "N/A"
                        ),
                        "cancelled_on": (
                            order.cancelled_on.astimezone(tz.gettz(settings.TIME_ZONE)).strftime(
                                FieldConstants.FULL_DATE_TIME_FORMAT
                            )
                            if order.cancelled_on
                            else "N/A"
                        ),
                    }
                    locations.append(
                        {
                            "coordinates": coordinates,
                            "sequence_number": order.sequence_number,
                            "address": address,
                            "customer_name": order.customer_name,
                            "status": order.status,
                            "reference_number": order.reference_number,
                            "eta": est_time,
                            "events_info": events_info,
                        }
                    )
            return {
                "locations": locations,
                "warehouse": {
                    "coordinates": [project_base_coordinates.x, project_base_coordinates.y],
                    "address": project.base_address,
                },
            }
        return {}

    def get_project_name(self, instance):
        return (
            instance.trip_orders.prefetch_related("project")
            .values_list("project__project_name", flat=True)
            .distinct()
            .first()
        )

    def get_project_id(self, instance):
        return (
            instance.trip_orders.prefetch_related("project")
            .values_list("project__project_id", flat=True)
            .distinct()
            .first()
        )

    class Meta:
        model = Trip
        fields = (
            "reference_number",
            "status",
            "added_by",
            "planned_distance",
            "planned_start_time",
            "planned_end_time",
            "trip_start",
            "trip_end",
            "travelling_time",
            "driver",
            "project_name",
            "trip_orders",
            "id",
            "logs",
            "trip_date",
            "modified",
            "trip_id",
            "helper_name",
            "planned_trip_duration",
            "actual_trip_duration",
            "order_count",
            "orders",
            "trip_route",
            "locations",
            "project_id",
            "vehicle_info",
            "driver_location",
            "trip_statistics",
            "pod_attachments",
            "actual_distance",
            "trip_start_km",
            "trip_end_km",
        )
        read_only_fields = [
            "created",
            "modified",
            "id",
            "logs",
            "vehicle",
            "trip_route",
            "locations",
            "vehicle_info",
        ]

    def to_representation(self, instance: Trip):
        representation = super().to_representation(instance=instance)
        representation["driver"] = instance.driver.user.full_name
        representation["driver_id"] = instance.driver.id
        representation["driver_number"] = instance.driver.user.contact_number
        return representation

    def validate_status(self, status):
        if status not in [
            TripStatus.SCHEDULED,
            TripStatus.ACTIVE,
            TripStatus.COMPLETED,
            TripStatus.PAUSED,
        ]:
            raise serializers.ValidationError("%s is not valid choice." % status)
        if status == TripStatus.SCHEDULED:
            raise serializers.ValidationError("The operations is not valid.")
        if status == TripStatus.ACTIVE:
            self.instance.start_trip()
        if status == TripStatus.COMPLETED:
            self.instance.complete_trip()
        return status

    def validate_driver(self, driver):
        all_trips = driver.driver_trips.all()
        if self.instance:
            if self.instance.driver == driver:
                return driver
            all_trips = all_trips.exclude(id=self.instance.id)
        request_data = self.context.get("request").data
        if isinstance(request_data, list) and request_data:
            trip_date = request_data[0].get("trip_date")
        else:
            trip_date = request_data.get("trip_date")
        if all_trips.filter(status__in=[TripStatus.ACTIVE, TripStatus.PAUSED]) or all_trips.filter(
            status=TripStatus.SCHEDULED, trip_date=trip_date
        ):
            raise serializers.ValidationError("Selected Driver is not Available on this date")
        return driver

    def validate_orders(self, orders):
        request_data = self.context.get("request").data
        total_order_cbm = Decimal("0.0")
        try:
            if isinstance(request_data, list) and request_data:
                trip_date = request_data[0].get("trip_date")
                driver_id = request_data[0].get("driver")
            else:
                trip_date = request_data.get("trip_date")
                driver_id = request_data.get("driver")
            driver_info = Driver.objects.get(id=driver_id)
        except Exception as e:
            raise serializers.ValidationError("Driver Not Found")

        try:
            vehicle_cbm_capacity = driver_info.vehicle_assigned.cbm_capacity
        except Exception:
            raise serializers.ValidationError("Vehicle is not assigned to driver.")

        for order in orders:
            if order.execution_date and order.execution_date.__str__() != trip_date:
                raise serializers.ValidationError(
                    "Execution date of order %s is not same as trip date" % order.order_id
                )
            items_cbm_capacity = order.order_items.aggregate(order_cbm=Sum("line_item_cbm")).get(
                "order_cbm"
            )
            if items_cbm_capacity:
                total_order_cbm += items_cbm_capacity
        if total_order_cbm > vehicle_cbm_capacity:
            raise serializers.ValidationError("Vehicle CBM capacity exceeds ")
        return orders

    def get_trip_planned_distance_and_duration(self, orders):
        route_response = {
            "planned_distance_in_km": None,
            "planned_trip_start_time": None,
            "planned_trip_end_time": None,
        }
        prv_order_processing_time_min = 0
        trip_start_datetime = timezone.now()
        if orders:
            project_base_coordinates = orders[0].project.base_coordinates
            coords = [[project_base_coordinates.x, project_base_coordinates.y]]
            client = OSRMClient()
            for order in orders:
                try:
                    if order.order_type == OrderConstants.OrderType.DELIVERY and order.drop_point:
                        coords.append([order.drop_point.x, order.drop_point.y])
                    elif order.pickup_point:
                        coords.append([order.pickup_point.x, order.pickup_point.y])
                    prv_order_processing_time_min += order.planned_processing_time
                except Exception as e:
                    logger.exception(e)
            try:
                result = client.get_trip(
                    coords,
                    roundtrip=True,
                    source="first",
                    destination="last",
                    driving_directions=False,
                )

                trip_eta_min = (
                    math.ceil(result["trip_duration_in_min"]) + prv_order_processing_time_min
                )
                trip_end_datetime = trip_start_datetime + timedelta(minutes=trip_eta_min)
                route_response["planned_distance_in_km"] = result["trip_distance_in_km"]
                route_response["planned_trip_start_time"] = trip_start_datetime
                route_response["planned_trip_end_time"] = trip_end_datetime
            except Exception as e:
                logger.exception(e)

        return route_response

    def create(self, validated_data):
        orders = validated_data.pop("orders", None)
        try:
            trip_estimations = self.get_trip_planned_distance_and_duration(orders)
            validated_data["planned_distance"] = trip_estimations["planned_distance_in_km"]
            validated_data["planned_start_time"] = trip_estimations["planned_trip_start_time"]
            validated_data["planned_end_time"] = trip_estimations["planned_trip_end_time"]
        except Exception as e:
            logger.exception(e)
        validated_data["added_by"] = self.context.get("request").user
        if not validated_data.get("trip_date"):
            validated_data["trip_date"] = timezone.now().date()
        validated_data["vehicle"] = validated_data.get("driver").vehicle_assigned
        trip = super(TripSerializer, self).create(validated_data)
        rec_list = []
        with transaction.atomic():
            for index, rec in enumerate(orders, start=1):
                trip.add_order_to_trip(rec, sequence_number=index)
                rec_list.append(rec.reference_number)
            if rec_list:
                msg = ",".join(rec_list) + "-" + TripStatusLogs.add_orders
                trip.add_trip_log(msg)
        return trip

    def update(self, obj, validated_data):
        orders = validated_data.pop("orders", None)
        existing_trip_orders = obj.trip_orders.all()
        if orders:
            rec_list = []
            removed_orders = existing_trip_orders.exclude(id__in=[order.id for order in orders])
            with transaction.atomic():
                for index, rec in enumerate(orders, start=1):
                    obj.add_order_to_trip(rec, sequence_number=index)
                    if rec not in existing_trip_orders:
                        rec_list.append(rec.reference_number)
                if rec_list:
                    msg = ",".join(rec_list) + "-" + TripStatusLogs.add_orders
                    obj.add_trip_log(msg)
                if removed_orders:
                    removed_orders.update(
                        status=OrderConstants.OrderStatus.UNASSIGNED,
                        trip=None,
                        picked_up_on=None,
                        unassigned_on=timezone.now(),
                        assigned_on=None,
                        enroute_on=None,
                        failed_on=None,
                        completed_on=None,
                    )
                    rec_list = [order.reference_number for order in removed_orders]
                    if rec_list:
                        msg = ",".join(rec_list) + "-" + TripStatusLogs.remove_orders
                        obj.add_trip_log(msg)
            try:
                trip_estimations = self.get_trip_planned_distance_and_duration(orders)
                validated_data["planned_distance"] = trip_estimations["planned_distance_in_km"]
                validated_data["planned_start_time"] = trip_estimations["planned_trip_start_time"]
                validated_data["planned_end_time"] = trip_estimations["planned_trip_end_time"]
            except Exception as e:
                logger.exception(e)
        trip = super(TripSerializer, self).update(obj, validated_data)
        return trip


class TripTemperatureSerializer(serializers.ModelSerializer):

    timestamp = serializers.CharField(source="ts")

    class Meta:
        model = TripTemperatureLog
        fields = ("temperature", "timestamp")


class TripTemperatureFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripTemperatureFile
        fields = ("status", "file_name", "added_by", "uploaded_filename")
        read_only_fields = "processed"


class TripMetricsSerializer(DynamicFieldsModelSerializer):

    coordinates = serializers.SerializerMethodField()

    def get_coordinates(self, instance: TripMetrics):
        return [instance.coordinates.x, instance.coordinates.y]

    class Meta:
        model = TripMetrics
        fields = ("coordinates", "battery", "speed", "timestamp")


class TripMapRouteSerializer(serializers.ModelSerializer):

    driver_route = serializers.SerializerMethodField()
    route_timestamp = serializers.SerializerMethodField()
    trip_info = serializers.SerializerMethodField()

    def get_driver_route(self, instance: Trip):
        coordinates_list = TripMetricsSerializer(
            instance.trip_coordinates.all().order_by("timestamp"),
            fields=("coordinates",),
            many=True,
        ).data

        coords = [coordinates["coordinates"] for coordinates in coordinates_list]
        route = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "LineString",
                    },
                }
            ],
        }
        route["features"][0]["geometry"].update({"coordinates": coords})
        return route

    def get_route_timestamp(self, instance: Trip):
        timestamp_list = TripMetricsSerializer(
            instance.trip_coordinates.all().order_by("timestamp"), fields=("timestamp",), many=True
        ).data

        return [ts["timestamp"] for ts in timestamp_list]

    def get_trip_info(self, instance: Trip):
        return TripSerializer(instance=instance, fields=("trip_route", "locations")).data

    class Meta:
        model = Trip
        fields = ("id", "reference_number", "driver_route", "trip_info", "route_timestamp")
