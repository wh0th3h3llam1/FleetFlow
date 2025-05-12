import logging

from common.osrm import OSRMClient
from dateutil import tz

from django.conf import settings
from django.db.models import Q, Count, Sum
from rest_framework import serializers
from rest_framework.reverse import reverse_lazy

from common.constants import DriverStatus, OrderConstants, TripStatus, FieldConstants
from core.serializers import DynamicFieldsModelSerializer
from dms.models import Driver, Trip, Order

logger = logging.getLogger(__name__)

"""
drivers list (date based filter, search)
driver click => trip detail

operations/drivers => driver list (on_duty/off_duty)
operations/drivers/1 => trip detail

"""


class DriverListSerializer(DynamicFieldsModelSerializer):
    username = serializers.CharField(source="user.username")
    driver_name = serializers.CharField(source="user.full_name")
    contact_number = serializers.CharField(source="user.contact_number")
    profile_image = serializers.ImageField(source="user.profile_image")
    zone_name = serializers.SerializerMethodField()
    vehicle = serializers.CharField(read_only=True)
    is_working = serializers.BooleanField(source="working")
    status = serializers.CharField(source="get_status_display")
    trip = serializers.SerializerMethodField()
    driver_location = serializers.SerializerMethodField(read_only=True)
    project_name = serializers.SerializerMethodField(read_only=True)

    def get_project_name(self, instance):
        return instance.project.project_name if instance.project else None

    def get_trip(self, instance: Driver):
        driver_trip = None
        try:
            driver_trip = instance.current_trip
        except AttributeError as e:
            driver_trip = instance.upcoming_trip
        except Exception as e:
            logger.exception(e)

        if instance.working and not driver_trip:
            ## Handling past dated scheduled trips
            driver_trip = (
                instance.driver_trips.filter(
                    status__in=[TripStatus.SCHEDULED, TripStatus.ACTIVE, TripStatus.PAUSED]
                )
                .order_by("trip_date")
                .first()
            )

        if driver_trip:
            return reverse_lazy("dms:op-trip-detail", kwargs={"trip_id": driver_trip.id})
        return None

    def get_is_working(self, instance):
        return instance.working

    def get_zone_name(self, instance):
        return instance.zone.zone_name if instance.zone else None

    def get_driver_location(self, instance: Driver):
        driver_details = {"name": instance.user.full_name, "location": None, "timestamp": None}
        try:
            if instance.current_trip and instance.status == DriverStatus.ON_DUTY:
                trip = instance.current_trip
                driver_location = trip.last_driver_location

                if driver_location.coordinates:
                    loc = driver_location.coordinates
                    ts = driver_location.timestamp
                    location = [loc.x, loc.y]

                    driver_details["location"] = location
                    driver_details["timestamp"] = ts.strftime(FieldConstants.DATE_TIME_FORMAT)
                    return driver_details

        except AttributeError as ae:
            pass
            # logger.exception(ae)
        except Exception as e:
            logger.exception(e)

        return driver_details

    class Meta:
        model = Driver
        fields = (
            "username",
            "driver_name",
            "contact_number",
            "profile_image",
            "status",
            "vehicle",
            "is_working",
            "trip",
            "driver_location",
            "id",
            "zone_name",
            "project_name",
        )


class TripDetailSerializer(DynamicFieldsModelSerializer):
    orders = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    trip_route = serializers.SerializerMethodField(read_only=True)
    partitions = serializers.SerializerMethodField(read_only=True)

    def get_partitions(self, instance: Trip):
        return instance.trip_order_partition()

    def get_order_count(self, instance: Trip):
        trip_orders = self.context.get("trip_orders")
        if trip_orders:
            total_orders_count = trip_orders.count()
            successful_statuses = [
                OrderConstants.OrderStatus.SUCCESSFUL,
                OrderConstants.OrderStatus.PARTIAL,
            ]
            return trip_orders.aggregate(
                successful=Count("id", filter=Q(status=OrderConstants.OrderStatus.SUCCESSFUL)),
                partially_delivered=Count(
                    "id", filter=Q(status=OrderConstants.OrderStatus.PARTIAL)
                ),
                failed=Count("id", filter=Q(status=OrderConstants.OrderStatus.FAILED)),
                unattempted=Count(
                    "id",
                    filter=~Q(status__in=[OrderConstants.OrderStatus.FAILED, *successful_statuses]),
                ),
                total=Count("id"),
            )
        return None

    def get_orders(self, instance: Trip):
        trip_orders = OperationOrderDetailSerializer(
            self.context.get("trip_orders"),
            fields=(
                "id",
                "reference_number",
                "invoice_number",
                "customer_name",
                "address",
                "status",
                "status_keyword",
                "order_type",
                "driver_name",
                "project_name",
                "updated_on",
                "contact_person",
                "contact_number",
                "id",
                "total_kg",
                "total_cbm",
                "no_of_items",
            ),
            many=True,
        ).data
        return trip_orders

    def get_trip_route(self, instance):
        trip_route = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "properties": {}, "geometry": dict()}],
        }
        orders = self.context.get("trip_orders")
        # orders = instance.trip_orders.all().order_by('sequence_number')
        order_details = []
        if orders:
            project = instance.driver.project
            project_base_coordinates = orders.first().project.base_coordinates
            coords = [[project_base_coordinates.x, project_base_coordinates.y]]
            for order in orders:
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
                order_details.append(
                    {
                        "reference_number": order.reference_number,
                        "invoice_number": order.invoice_number,
                        "address": order.address(),
                        "customer_name": order.customer_name,
                        "sequence_number": order.sequence_number,
                        "status": order.status,
                        "eta": order.etc,
                        "delivery_window": order.delivery_window,
                        "coordinates": [order.coordinates.x, order.coordinates.y],
                        "events_info": events_info,
                    }
                )
                try:
                    coords.append([order.coordinates.x, order.coordinates.y])
                except Exception as e:
                    logger.exception(e)

            coords.append([project_base_coordinates.x, project_base_coordinates.y])
            try:
                client = OSRMClient()
                result = client.get_route(coords, driving_directions=True)
            except Exception as e:
                logger.exception(e)
            else:
                trip_route["features"][0]["geometry"] = result["driving_directions"]
            warehouse_details = {
                "address": project.base_address,
                "coordinates": [project.base_coordinates.x, project.base_coordinates.y],
            }
            return {
                "trip_route": trip_route,
                "order_details": order_details,
                "warehouse_details": warehouse_details,
            }

    class Meta:
        model = Trip
        fields = (
            "reference_number",
            "orders",
            "order_count",
            "trip_date",
            "planned_start_time",
            "planned_end_time",
            "trip_start",
            "trip_end",
            "trip_route",
            "partitions",
            "status",
            "helper_name",
        )


class OperationOrderDetailSerializer(DynamicFieldsModelSerializer):
    no_of_items = serializers.SerializerMethodField()
    status_keyword = serializers.CharField(source="reason", read_only=True)
    driver_name = serializers.CharField(read_only=True)
    project_name = serializers.CharField(source="project.project_name", read_only=True)
    updated_on = serializers.DateTimeField(read_only=True)
    total_cbm = serializers.SerializerMethodField()
    total_kg = serializers.SerializerMethodField()
    trip_name = serializers.SerializerMethodField()

    def get_total_cbm(self, obj):
        return obj.order_items.all().aggregate(total_cbm=Sum("line_item_cbm")).get("total_cbm")

    def get_total_kg(self, obj):
        return obj.order_items.all().aggregate(total_kg=Sum("line_item_weight")).get("total_kg")

    def get_no_of_items(self, obj):
        return (
            obj.order_items.all()
            .aggregate(total_quantity=Sum("original_quantity"))
            .get("total_quantity")
        )

    def get_trip_name(self, obj):
        return obj.trip.reference_number if obj.trip else None

    class Meta:
        model = Order
        fields = (
            "reference_number",
            "invoice_number",
            "trip_name",
            "customer_name",
            "contact_person",
            "no_of_items",
            "contact_number",
            "project_name",
            "status",
            "status_keyword",
            "etc",
            "address",
            "order_type",
            "driver_name",
            "updated_on",
            "id",
            "total_kg",
            "total_cbm",
            "order_type",
        )
