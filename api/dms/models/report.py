from django.db import models

from core.models import BaseModel


class ReportUtilization(BaseModel):
    date = models.DateField(unique=True)
    utilized_vehicle_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Utilized Vehicle Count"
    )
    utilized_driver_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Utilized Driver Count"
    )
    idle_driver_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Idle Driver Count"
    )
    idle_vehicle_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Idle Vehicle Count"
    )
    total_distance_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Total Distance Count"
    )
    average_distance_per_trip = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Average Distance Per Trip"
    )
    total_traveling_time = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Total Traveling Time"
    )
    average_traveling_time = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Average traveling time"
    )
    total_break_time = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Total break time"
    )
    average_break_time = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Average break time "
    )
    total_handover_time = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Total handover time"
    )
    average_handover_time = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Average handover time"
    )
    trip_count = models.PositiveIntegerField(blank=True, null=True, verbose_name="trip count")
    successful_order_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Successful Order count"
    )
    failed_order_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Failed Order count"
    )
    total_order_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="total order count"
    )
    total_drop_points_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="total drop points"
    )
    total_customer_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="total customer count"
    )
    average_drop_points_per_trip_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="average drop points per trip"
    )
    average_order_count_per_trip_count = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="average order count per trip"
    )

    def __str__(self):
        return "{}".format(self.date)


class TripStatistics(BaseModel):
    date = models.DateField(unique=True)

    total_trips = models.PositiveIntegerField(verbose_name="Total Trips", blank=True, null=True)

    total_distance = models.PositiveIntegerField(
        verbose_name="Total Distance Covered", blank=True, null=True
    )
    total_trip_duration = models.PositiveIntegerField(
        verbose_name="Total Trip Duration", blank=True, null=True
    )

    planned_travelling_time = models.PositiveIntegerField(
        verbose_name="Planned Travelling Time", blank=True, null=True
    )
    total_travelling_time = models.PositiveIntegerField(
        verbose_name="Total Travelling Time", blank=True, null=True
    )
    total_break_time = models.PositiveIntegerField(
        verbose_name="Total Break Time", blank=True, null=True
    )
    total_processing_time = models.PositiveIntegerField(
        verbose_name="Total Processing Time", blank=True, null=True
    )
    total_expense = models.PositiveIntegerField(verbose_name="Total Expense", blank=True, null=True)

    total_drop_points = models.PositiveIntegerField(
        verbose_name="Total Drop Points", blank=True, null=True
    )
    total_cases_dropped = models.PositiveIntegerField(
        verbose_name="Total Cases Dropped", blank=True, null=True
    )
    average_cases_per_drop = models.PositiveIntegerField(
        verbose_name="Average Cases per Drop", blank=True, null=True
    )

    average_distance = models.PositiveIntegerField(
        verbose_name="Average Distance", blank=True, null=True
    )
    average_trip_duration = models.PositiveIntegerField(
        verbose_name="Average Trip Duration", blank=True, null=True
    )
    average_travelling_time = models.PositiveIntegerField(
        verbose_name="Average Travelling Time", blank=True, null=True
    )
    average_break_time = models.PositiveIntegerField(
        verbose_name="Average Break Time", blank=True, null=True
    )
    average_processing_time = models.PositiveIntegerField(
        verbose_name="Average Processing Time", blank=True, null=True
    )
    average_expense = models.PositiveIntegerField(
        verbose_name="Average Expense", blank=True, null=True
    )

    average_overtime = models.CharField(
        verbose_name="Average Overtime", blank=True, null=True, max_length=50
    )
    avg_fleet_capacity_utilization = models.PositiveIntegerField(
        verbose_name="Average Fleet Capacity Utilization", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = "Trip Statistics"

    def __str__(self) -> str:
        return f"{self.date}"


class OrderStatistics(BaseModel):
    date = models.DateField(unique=True)

    total_orders = models.PositiveIntegerField(verbose_name="Total Orders", blank=True, null=True)
    assigned_orders = models.PositiveIntegerField(
        verbose_name="Assigned Orders", blank=True, null=True
    )
    picked_up_orders = models.PositiveIntegerField(
        verbose_name="Picked Up Orders", blank=True, null=True
    )
    successful_orders = models.PositiveIntegerField(
        verbose_name="Successful Orders", blank=True, null=True
    )
    partially_delivered_orders = models.PositiveIntegerField(
        verbose_name="Partially Delivered Orders", blank=True, null=True
    )
    failed_orders = models.PositiveIntegerField(verbose_name="Failed Orders", blank=True, null=True)
    cancelled_orders = models.PositiveIntegerField(
        verbose_name="Cancelled Orders", blank=True, null=True
    )

    frozen_items = models.PositiveIntegerField(verbose_name="Frozen Items", blank=True, null=True)
    chilled_items = models.PositiveIntegerField(verbose_name="Chilled Items", blank=True, null=True)
    dry_items = models.PositiveIntegerField(verbose_name="Dry Items", blank=True, null=True)

    same_day_delivery = models.PositiveIntegerField(
        verbose_name="Same Day Delivery", blank=True, null=True
    )
    delayed_delivery = models.PositiveIntegerField(
        verbose_name="Delayed Delivery", blank=True, null=True
    )

    max_orders_returned = models.CharField(
        verbose_name="Max Orders Returned Due To", blank=True, null=True, max_length=100
    )

    total_drop_points = models.PositiveIntegerField(
        verbose_name="Total Drop Points", blank=True, null=True
    )
    unique_drop_points = models.PositiveIntegerField(
        verbose_name="Unique Drop Points", blank=True, null=True
    )

    total_order_items = models.PositiveIntegerField(
        verbose_name="Total Order Items", blank=True, null=True
    )
    total_cases = models.PositiveIntegerField(verbose_name="Total Cases", blank=True, null=True)
    total_boxes = models.PositiveIntegerField(verbose_name="Total Boxes", blank=True, null=True)

    total_weight = models.PositiveIntegerField(verbose_name="Total Weight", blank=True, null=True)
    total_volume = models.PositiveIntegerField(verbose_name="Total Volume", blank=True, null=True)

    total_planned_processing_time = models.PositiveIntegerField(
        verbose_name="Total Planned Processing Time", blank=True, null=True
    )
    total_processing_time = models.PositiveIntegerField(
        verbose_name="Total Processing Time", blank=True, null=True
    )

    average_weight = models.PositiveIntegerField(
        verbose_name="Average Weight", blank=True, null=True
    )
    average_volume = models.PositiveIntegerField(
        verbose_name="Average Volume", blank=True, null=True
    )
    average_processing_time = models.PositiveIntegerField(
        verbose_name="Average Planned Processing Time", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = "Order Statistics"

    def __str__(self) -> str:
        return f"{self.date}"


class DriverStatistics(BaseModel):
    date = models.DateField(unique=True)

    total_drivers = models.PositiveIntegerField(verbose_name="Total Drivers", blank=True, null=True)
    utilized_drivers = models.PositiveIntegerField(
        verbose_name="Utilized Drivers", blank=True, null=True
    )
    idle_drivers = models.PositiveIntegerField(verbose_name="Idle Drivers", blank=True, null=True)

    total_kms_driven = models.PositiveIntegerField(
        verbose_name="Total Kms Driven", blank=True, null=True
    )
    total_break_time = models.PositiveIntegerField(
        verbose_name="Total Break Time", blank=True, null=True
    )
    average_kms_driven = models.PositiveIntegerField(
        verbose_name="Average Kms Driven", blank=True, null=True
    )
    average_break_time = models.PositiveIntegerField(
        verbose_name="Average Break Time", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = "Driver Statistics"

    def __str__(self) -> str:
        return f"{self.date}"


class VehicleStatistics(BaseModel):
    date = models.DateField(unique=True)

    total_vehicles = models.PositiveIntegerField(
        verbose_name="Total Vehicles", blank=True, null=True
    )
    utilized_vehicles = models.PositiveIntegerField(
        verbose_name="Utilized Vehicles", blank=True, null=True
    )
    idle_vehicles = models.PositiveIntegerField(verbose_name="Idle Vehicles", blank=True, null=True)

    boxes_delivered = models.PositiveIntegerField(
        verbose_name="Boxes Delivered", blank=True, null=True
    )
    average_cases_per_drop = models.PositiveIntegerField(
        verbose_name="Average Cases Per Drop", blank=True, null=True
    )

    total_tonnage_capacity = models.PositiveIntegerField(
        verbose_name="Total Tonnage Capacity", blank=True, null=True
    )
    total_cbm_capacity = models.PositiveIntegerField(
        verbose_name="Total CBM Capacity", blank=True, null=True
    )
    total_box_capacity = models.PositiveIntegerField(
        verbose_name="Total Box Capacity", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = "Vehicle Statistics"

    def __str__(self) -> str:
        return f"{self.date}"
