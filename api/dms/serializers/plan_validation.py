import datetime
import json

from django.db.models import Sum, Min, Max
from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers
from shapely import geometry

from common.constants import FieldConstants
from core.serializers import DynamicFieldsModelSerializer
from dms.helpers import has_overlap
from dms.models import Order, Zone, Driver


class OrderValidationSerializer(DynamicFieldsModelSerializer):
    address = serializers.CharField(read_only=True)
    no_of_items = serializers.SerializerMethodField()
    coordinates = PointField(read_only=True)
    delivery_window_start = serializers.TimeField(format="%H:%M", read_only=True)
    delivery_window_end = serializers.TimeField(format="%H:%M", read_only=True)
    warnings = serializers.SerializerMethodField()
    customer_code = serializers.SerializerMethodField(read_only=True)

    def get_customer_code(self, instance: Order):
        return instance.customer_address.customer_code

    def get_warnings(self, instance: Order):
        zone_details = self.context.get("zone_details")
        disabled_time_windows = self.context.get("disabled_time_windows", False)
        time_window_constraint = not disabled_time_windows
        warnings = []
        if zone_details:
            order_point = geometry.Point(instance.coordinates)
            order_zone = None
            for _, zone_detail in zone_details.items():
                geofence = geometry.shape(zone_detail["geofence"])
                if geofence.contains(order_point):
                    order_zone = zone_detail
                    break
            if not order_zone:
                warnings.append("Order coordinates outside planned zones.")
            elif order_zone.get("drivers", False):
                if time_window_constraint:
                    delivery_windows = self.delivery_windows(instance=instance)
                    zone_shift_start = datetime.datetime.strptime(
                        order_zone["zone_shift_start"], FieldConstants.DATE_TIME_FORMAT
                    )
                    zone_shift_end = datetime.datetime.strptime(
                        order_zone["zone_shift_end"], FieldConstants.DATE_TIME_FORMAT
                    )
                    order_window_start, order_window_end = (
                        delivery_windows["from_time"],
                        delivery_windows["to_time"],
                    )

                    if not has_overlap(
                        zone_shift_start, zone_shift_end, order_window_start, order_window_end
                    ):
                        warnings.append("Order delivery window outside the drivers shift hours.")
            else:
                warnings.append("No Drivers are available for the zone.")

        zone_constraint = self.context.get("zone_constraint", False)
        drivers = self.context.get("drivers", False)
        if time_window_constraint and not zone_constraint:
            if drivers:
                delivery_windows = self.delivery_windows(instance=instance)
                driver_shift = drivers.aggregate(
                    min_shift=Min("shift_start"), max_shift=Max("shift_end")
                )
                driver_shift_start = datetime.datetime.combine(
                    instance.execution_date, driver_shift.get("min_shift")
                )
                driver_shift_end = datetime.datetime.combine(
                    instance.execution_date, driver_shift.get("max_shift")
                )
                order_window_start, order_window_end = (
                    delivery_windows["from_time"],
                    delivery_windows["to_time"],
                )

                if not has_overlap(
                    driver_shift_start, driver_shift_end, order_window_start, order_window_end
                ):
                    warnings.append("Order delivery window outside the drivers shift hours.")
            else:
                warnings.append("No Drivers are available for the project.")
        return warnings

    def get_no_of_items(self, instance: Order):
        return instance.total_quantity

    def delivery_windows(self, instance: Order):
        execution_date = instance.execution_date
        delivery_window_start = datetime.datetime.combine(
            instance.execution_date, instance.delivery_window_start
        )
        if instance.delivery_window_start > instance.delivery_window_end:
            end_date = execution_date + datetime.timedelta(days=1)
            delivery_window_end = datetime.datetime.combine(end_date, instance.delivery_window_end)
        else:
            delivery_window_start = datetime.datetime.combine(
                execution_date, instance.delivery_window_start
            )
            delivery_window_end = datetime.datetime.combine(
                execution_date, instance.delivery_window_end
            )
        return {"from_time": delivery_window_start, "to_time": delivery_window_end}

    class Meta:
        model = Order
        fields = (
            "reference_number",
            "execution_date",
            "customer_code",
            "customer_name",
            "contact_person",
            "processing_time",
            "address",
            "contact_number",
            "coordinates",
            "planned_processing_time",
            "no_of_items",
            "warnings",
            "delivery_window_start",
            "delivery_window_end",
        )


class ZoneValidationSerializer(DynamicFieldsModelSerializer):
    zone_details = serializers.SerializerMethodField()

    def get_zone_details(self, instance: Zone):
        order_count = 0
        total_order_weight = 0
        total_order_cbm = 0

        orders = self.context.get("orders")
        if orders:
            geofence = geometry.shape(json.loads(instance.geofence.geojson))
            for order in orders:
                order_point = geometry.Point(order.coordinates)
                if geofence.contains(order_point):
                    order_count += 1
                    total_order_weight += order.total_weight
                    total_order_cbm += order.total_cbm

        details = {"order_count": order_count, "geofence": json.loads(instance.geofence.geojson)}

        shift_timings = []
        start_date = self.context.get("date")
        zone_drivers = instance.zone_drivers.select_related("vehicle_assigned", "user").filter(
            vehicle_assigned__isnull=False, is_active=True
        )

        if zone_drivers:
            stats = zone_drivers.aggregate(
                total_weight=Sum("vehicle_assigned__tonnage_capacity") * 1000,
                total_volume=Sum("vehicle_assigned__cbm_capacity"),
            )
            warnings = []
            if stats["total_weight"] < total_order_weight:
                warnings.append("Insufficient weight based capacity.")
            if stats["total_volume"] < total_order_cbm:
                warnings.append("Insufficient volume based capacity.")
            details.update({"driver_count": zone_drivers.count(), "warnings": warnings})

            for zone_driver in zone_drivers:
                shift_start = datetime.datetime.combine(start_date, zone_driver.shift_start)
                if zone_driver.shift_start > zone_driver.shift_end:
                    end_date = start_date + datetime.timedelta(days=1)
                    shift_end = datetime.datetime.combine(end_date, zone_driver.shift_end)
                else:
                    shift_end = datetime.datetime.combine(start_date, zone_driver.shift_end)
                shift_timings.extend([shift_start, shift_end])
            shift_timings.sort()
            details.update(
                {
                    "zone_shift_start": shift_timings[0].strftime(FieldConstants.DATE_TIME_FORMAT),
                    "zone_shift_end": shift_timings[-1].strftime(FieldConstants.DATE_TIME_FORMAT),
                }
            )
        return details

    class Meta:
        model = Zone
        fields = ("zone_name", "zone_details")


class DriverValidationSerializer(DynamicFieldsModelSerializer):
    vehicle = serializers.CharField(read_only=True)
    driver_name = serializers.CharField(source="user.full_name", read_only=True)
    zone = serializers.SlugRelatedField(slug_field="zone_name", read_only=True)
    warnings = serializers.SerializerMethodField()
    shift_start = serializers.TimeField(format="%H:%M", read_only=True)
    shift_end = serializers.TimeField(format="%H:%M", read_only=True)
    contact_number = serializers.IntegerField(source="user.contact_number", read_only=True)

    def get_warnings(self, instance: Driver):
        warnings = []
        if not instance.vehicle_assigned:
            warnings.append("No vehicle assigned.")
        if self.context.get("zone_constraint") and not instance.zone:
            warnings.append("No zone assigned.")
        template_timings = self.context.get("template_timings")
        if template_timings:
            driver_shift_start = instance.shift_start
            driver_shift_end = instance.shift_end
            loading_start_time = template_timings["loading_start_time"]
            loading_end_time = template_timings["loading_end_time"]
            offloading_start_time = template_timings["offloading_start_time"]
            offloading_end_time = template_timings["offloading_end_time"]

            if not loading_start_time < driver_shift_start < loading_end_time:
                warnings.append("Planning Template Window not aligned with Driver Shift")
            elif not offloading_start_time < driver_shift_end < offloading_end_time:
                warnings.append("Planning Template Window not aligned with Driver Shift")

        return warnings

    class Meta:
        model = Driver
        fields = (
            "driver_name",
            "warnings",
            "vehicle",
            "shift_start",
            "shift_end",
            "zone",
            "contact_number",
        )
