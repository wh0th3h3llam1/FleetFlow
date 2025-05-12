from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from django_filters.rest_framework import DjangoFilterBackend

from common.constants import FieldConstants
from common.utils import manage_start_end_date, json_to_excel, get_days_hours_minutes
from dms.models import report
from dms.serializers import OrderSerializer


class ReportsViewSet(GenericViewSet):

    permission_classes = IsAuthenticated
    filter_backends = (DjangoFilterBackend,)
    serializer_class = OrderSerializer

    def get_queryset(self):

        if self.action == "drivers":
            queryset = report.DriverStatistics.objects.all()
        elif self.action == "orders":
            queryset = report.OrderStatistics.objects.all()
        elif self.action == "trips":
            queryset = report.TripStatistics.objects.all()
        else:
            queryset = report.VehicleStatistics.objects.all()
        return queryset

    @action(methods=["get"], detail=False, permission_classes=(IsAuthenticated,))
    def trips(self, request, *args, **kwargs):

        s_d = request.query_params.get("start_date", None)
        e_d = request.query_params.get("end_date", None)

        start_date, end_date = manage_start_end_date(s_d, e_d, duration=15)

        trip_report = list()

        headers = [
            "Date",
            "Total Trips",
            "Total Distance",
            "Total Trip Duration",
            "Planned Travelling Time",
            "Total Travelling Time",
            "Total Break Time",
            "Total Processing Time",
            "Total Expense",
            "Total Drop Points",
            "Total Cases Dropped",
            "Average Cases per Drop",
            "Average Distance",
            "Average Trip Duration",
            "Average Travelling Time",
            "Average Break Time",
            "Average Processing Time",
            "Average Expense",
            "Average Overtime",
            "Average Fleet Capacity Utilization",
        ]

        queryset = self.get_queryset()

        trips = queryset.filter(date__range=(start_date, end_date))
        for trip in trips:
            trip: report.TripStatistics = trip
            trip_report.append(
                [
                    trip.date.strftime(FieldConstants.DATE_FORMAT),
                    trip.total_trips,
                    trip.total_distance,
                    get_days_hours_minutes(trip.total_trip_duration),
                    get_days_hours_minutes(trip.planned_travelling_time),
                    get_days_hours_minutes(trip.total_travelling_time),
                    get_days_hours_minutes(trip.total_break_time),
                    get_days_hours_minutes(trip.total_processing_time),
                    trip.total_expense,
                    trip.total_drop_points,
                    trip.total_cases_dropped,
                    trip.average_cases_per_drop,
                    trip.average_distance,
                    get_days_hours_minutes(trip.average_trip_duration),
                    get_days_hours_minutes(trip.average_travelling_time),
                    get_days_hours_minutes(trip.average_break_time),
                    get_days_hours_minutes(trip.average_processing_time),
                    trip.average_expense,
                    trip.average_overtime,
                    trip.avg_fleet_capacity_utilization,
                ]
            )

        sheet = json_to_excel(headers=headers, data=trip_report, name="Trip Report")
        return sheet

    @action(methods=["get"], detail=False, permission_classes=(IsAuthenticated,))
    def orders(self, request, *args, **kwargs):

        s_d = request.query_params.get("start_date", None)
        e_d = request.query_params.get("end_date", None)

        start_date, end_date = manage_start_end_date(s_d, e_d, duration=15)

        order_report = list()

        headers = [
            "Date",
            "Total Orders",
            "Successful Orders",
            "Partially Delivered Orders",
            "Failed Orders",
            "Same Day Delivery",
            "Delayed Delivery",
            "Max Orders Returned Due To",
            "Frozen Items",
            "Chilled Items",
            "Dry Items",
            "Total Drop Points",
            "Unique Drop Points",
            "Total Order Items",
            "Total Cases",
            "Total Boxes",
            "Total Weight",
            "Total Volume",
            "Total Planned Processing Time",
            "Total Processing Time",
            "Average Weight",
            "Average Volume",
            "Average Processing Time",
        ]

        queryset = self.get_queryset()

        orders = queryset.filter(date__range=(start_date, end_date))

        for order in orders:
            order: report.OrderStatistics = order
            order_report.append(
                [
                    order.date.strftime(FieldConstants.DATE_FORMAT),
                    order.total_orders,
                    order.successful_orders,
                    order.partially_delivered_orders,
                    order.failed_orders,
                    order.same_day_delivery,
                    order.delayed_delivery,
                    order.max_orders_returned,
                    order.frozen_items,
                    order.chilled_items,
                    order.dry_items,
                    order.total_drop_points,
                    order.unique_drop_points,
                    order.total_order_items,
                    order.total_cases,
                    order.total_boxes,
                    order.total_weight,
                    order.total_volume,
                    order.total_planned_processing_time,
                    order.total_processing_time,
                    order.average_weight,
                    order.average_volume,
                    order.average_processing_time,
                ]
            )

        sheet = json_to_excel(headers=headers, data=order_report, name="Order Report")
        return sheet

    @action(methods=["get"], detail=False, permission_classes=(IsAuthenticated,))
    def drivers(self, request, *args, **kwargs):

        s_d = request.query_params.get("start_date", None)
        e_d = request.query_params.get("end_date", None)

        start_date, end_date = manage_start_end_date(s_d, e_d, duration=15)

        driver_report = list()

        headers = [
            "Date",
            "Total Drivers",
            "Utilized Drivers",
            "Idle Drivers",
            "Total Kms Driven",
            "Total Break Time",
            "Average Kms Driven",
            "Average Break Time",
        ]

        queryset = self.get_queryset()

        drivers = queryset.filter(date__range=(start_date, end_date))

        for driver in drivers:
            driver_report.append(
                [
                    driver.date.strftime(FieldConstants.DATE_FORMAT),
                    driver.total_drivers,
                    driver.utilized_drivers,
                    driver.idle_drivers,
                    driver.total_kms_driven,
                    driver.total_break_time,
                    driver.average_kms_driven,
                    driver.average_break_time,
                ]
            )

        sheet = json_to_excel(headers=headers, data=driver_report, name="Driver Report")
        return sheet

    @action(methods=["get"], detail=False, permission_classes=(IsAuthenticated,))
    def vehicles(self, request, *args, **kwargs):

        s_d = request.query_params.get("start_date", None)
        e_d = request.query_params.get("end_date", None)

        start_date, end_date = manage_start_end_date(s_d, e_d, duration=15)

        vehicle_report = list()

        headers = [
            "Date",
            "Total Vehicles",
            "Utilized Vehicles",
            "Idle Vehicles",
            "Boxes Delivered",
            "Average Cases Per Drop",
            "Total Tonnage Capacity",
            "Total CBM Capacity",
            "Total Box Capacity",
        ]

        queryset = self.get_queryset()

        vehicles = queryset.filter(date__range=(start_date, end_date))

        for vehicle in vehicles:
            vehicle_report.append(
                [
                    vehicle.date.strftime(FieldConstants.DATE_FORMAT),
                    vehicle.total_vehicles,
                    vehicle.utilized_vehicles,
                    vehicle.idle_vehicles,
                    vehicle.boxes_delivered,
                    vehicle.average_cases_per_drop,
                    vehicle.total_tonnage_capacity,
                    vehicle.total_cbm_capacity,
                    vehicle.total_box_capacity,
                ]
            )

        sheet = json_to_excel(headers=headers, data=vehicle_report, name="Vehicle Report")
        return sheet
