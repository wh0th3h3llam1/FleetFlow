import logging
import math
import os
import random
from datetime import timedelta, datetime

from django.conf import settings
from django.db import models
from django.db.models import Sum, Q, Count, F, Value, IntegerField, When, Case
from django.db.models.functions import Coalesce
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import pandas as pd

from common.constants import (
    DriverExpenseCategory,
    OrderConstants,
    TripStatus,
    VehicleStatus,
    FieldConstants,
)
from common.utils import daterange, manage_start_end_date
from dms.filters import VehicleReportFilter, DriverReportFilter, OrderReportFilter, TripReportFilter
from dms.models import Vehicle, Driver, Order, Trip
from dms.serializers import VehicleSerializer, DriverSerializer, OrderSerializer, TripSerializer


logger = logging.getLogger(__name__)


def date_str_format(date):
    return timezone.localtime(date).strftime(FieldConstants.DATE_TIME_FORMAT) if date else ""


def lat_long_str_format(point_field):
    return "{}, {}".format(round(point_field.y, 7), round(point_field.x, 7)) if point_field else ""


def create_excel_report(report_data, report_name, start_date, end_date, host, user):
    random_number = random.randrange(10000, 99999)
    file_name = f"{report_name}-{user.username}-{start_date}-To-{end_date}-{random_number}"
    folder_path = "{}/media/reports".format(os.getcwd())
    file_path = "{}/{}.xlsx".format(folder_path, file_name)

    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    try:
        dataframe = pd.DataFrame(report_data)
        dataframe.to_excel(file_path, header=False, index=False)
        file_url = "https://" + host + "/media/reports/{}.xlsx".format(file_name)
        return file_url
    except Exception as e:
        logger.exception(e)
    else:
        logger.info("Excel file sent. Removing file from server.")


class VehicleReportsViewSet(viewsets.GenericViewSet):
    serializer_class = VehicleSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_class = VehicleReportFilter

    def get_queryset(self):
        return Vehicle.objects.prefetch_related("vehicle_trips", "vehicle_drivers").exclude(
            status=VehicleStatus.DEACTIVATED
        )

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def vehicle_utilization(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        vehicle_ids = request.query_params.get("vehicle")
        project_ids = request.query_params.get("project")
        vehicle_filter = {"project__project_id__in": self.request.user.projects_with_access}
        if project_ids:
            project = project_ids.split(",")
            vehicle_filter.update({"project__project_id__in": project})
        if vehicle_ids:
            vehicle_ids = vehicle_ids.split(",")
            vehicle_filter.update({"id__in": vehicle_ids})

        queryset = self.get_queryset().filter(**vehicle_filter)
        report_data = [
            ["Date", "Vehicle", "Vehicle Status(Used/Idle)", "Drivers", "Trips", "Box Capacity"]
        ]

        if start_date and end_date:
            for date in daterange(
                datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            ):
                if date < date.today():
                    report_date = date.strftime(FieldConstants.DATE_FORMAT)
                    vehicles = queryset.filter(vehicle_trips__trip_date=date).distinct()
                    idle_vehicles = queryset.exclude(id__in=vehicles)
                    for vehicle in vehicles:
                        trips = vehicle.vehicle_trips.filter(trip_date=date, vehicle=vehicle)
                        trip_ids = ",".join([trip.reference_number for trip in trips])
                        driver_distinct_trips = vehicle.vehicle_trips.distinct("driver")
                        drivers = ",".join(
                            [trip.driver.user.full_name for trip in driver_distinct_trips]
                        )
                        used_boxes_capacity = sum(
                            (float(trip.total_item_cbm()) / settings.BOX_UNIT) for trip in trips
                        )
                        box_capacity = f"{math.ceil(used_boxes_capacity)}/{vehicle.box_capacity}"
                        report_data.append(
                            [
                                report_date,
                                vehicle.vehicle_plate_no,
                                "Used",
                                drivers,
                                trip_ids,
                                box_capacity,
                            ]
                        )
                    for i_vehicle in idle_vehicles:
                        report_data.append(
                            [report_date, i_vehicle.vehicle_plate_no, "Idle", "N/A", "N/A", "N/A"]
                        )

            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "vehicle_utilization"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def vehicle_daily_km_rum(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        report_data = [
            [
                "Date",
                "Vehicle",
                "Project",
                "Start Time",
                "End Time",
                "Total Trips",
                "Total Distance",
                "Fuel Expenditure",
            ]
        ]
        queryset = queryset.filter(project__project_id__in=self.request.user.projects_with_access)
        if start_date and end_date:
            for date in daterange(
                datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            ):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                vehicles = queryset.filter(
                    vehicle_trips__trip_date=date, vehicle_trips__status=TripStatus.COMPLETED
                ).distinct()
                # If show Idle vehicles uncomment the lines
                # idle_vehicles = queryset.exclude(id__in=vehicles.values_list('id', flat=True), status='deactivated')
                for vehicle in vehicles:
                    trips = vehicle.vehicle_trips.filter(
                        trip_date=date, vehicle=vehicle, status=TripStatus.COMPLETED
                    )
                    start_time = ""
                    end_time = ""
                    duty_start = trips.order_by("trip_start").first().trip_start
                    duty_end = trips.order_by("-trip_end").first().trip_end
                    if duty_start:
                        start_time = timezone.localtime(duty_start).strftime(
                            FieldConstants.DATE_TIME_FORMAT
                        )
                    if duty_end:
                        end_time = timezone.localtime(duty_end).strftime(
                            FieldConstants.DATE_TIME_FORMAT
                        )
                    total_distance = trips.aggregate(total_distance=Sum("actual_distance")).get(
                        "total_distance"
                    )
                    if not total_distance:
                        total_distance = 0
                    fuel_expense_records = trips.aggregate(
                        fuel_expense=Sum(
                            "trip_expenses__amount",
                            filter=Q(
                                trip_expenses__expense_category=DriverExpenseCategory.FUEL_FILL_RECEIPT
                            ),
                        )
                    )
                    fuel_expense = fuel_expense_records.get("fuel_expense")
                    if not fuel_expense:
                        fuel_expense = 0
                    report_data.append(
                        [
                            report_date,
                            vehicle.vehicle_plate_no,
                            vehicle.project.project_name,
                            start_time,
                            end_time,
                            trips.count(),
                            total_distance,
                            fuel_expense,
                        ]
                    )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "vehicle_daily_kms"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def vehicle_total_mileage(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        vehicle_ids = request.query_params.get("vehicle")
        project_ids = request.query_params.get("project")
        vehicle_filter = {"project__project_id__in": self.request.user.projects_with_access}
        if project_ids:
            project = project_ids.split(",")
            vehicle_filter.update({"project__project_id": project})
        if vehicle_ids:
            vehicle_ids = vehicle_ids.split(",")
            vehicle_filter.update({"id__in": vehicle_ids})
        queryset = Vehicle.objects.filter(**vehicle_filter)
        report_data = [
            [
                "Vehicle Plate No",
                "Vehicle Brand",
                "Vehicle Year",
                "Partition Type",
                "Total Kms",
                "Vehicle location",
            ]
        ]
        if start_date and end_date:
            for vehicle in queryset:
                vehicle_brand = "{make} {model}".format(
                    make=vehicle.vehicle_make if vehicle.vehicle_make else "",
                    model=vehicle.vehicle_model if vehicle.vehicle_model else "",
                )
                vehicle_year = vehicle.vehicle_year if vehicle.vehicle_year else "N/A"
                partitions = vehicle.vehicle_storages.all().distinct("storage_type")
                compartment = "Single Compartment"
                partitions_list = ",".join(
                    [storage.get_storage_type_display() for storage in partitions]
                )
                if partitions.count() > 1:
                    compartment = "Multi Compartment"
                elif partitions.count() == 0:
                    compartment = "No Compartment"
                partition_types = "{compartment}-{partitions_list}".format(
                    compartment=compartment,
                    partitions_list=partitions_list if partitions_list else "N/A",
                )
                vehicle_trips = vehicle.vehicle_trips.filter(
                    trip_date__range=[start_date, end_date], status=TripStatus.COMPLETED
                )
                total_kms = vehicle_trips.aggregate(total_kms=Sum("actual_distance")).get(
                    "total_kms"
                )
                if not total_kms:
                    total_kms = 0
                report_data.append(
                    [
                        vehicle.vehicle_plate_no,
                        vehicle_brand,
                        vehicle_year,
                        partition_types,
                        total_kms,
                        vehicle.project.base_address,
                    ]
                )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "vehicle_total_mileage"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def vehicle_order_delivery(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        report_data = [
            [
                "Date",
                "Vehicle Number",
                "Project",
                "Driver Name",
                "No of Trips",
                "No of Orders",
                "Attempted",
                "Delivered",
                "Returned",
                "Paritally Delivered",
            ]
        ]
        queryset = queryset.filter(project__project_id__in=self.request.user.projects_with_access)
        if start_date and end_date:
            for date in daterange(
                datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            ):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                for vehicle in queryset:
                    trips = vehicle.vehicle_trips.filter(trip_date=date)
                    trip_orders_counts = trips.aggregate(
                        total_count=Count("trip_orders"),
                        completed=Count(
                            "trip_orders",
                            filter=Q(trip_orders__status=OrderConstants.OrderStatus.SUCCESSFUL),
                        ),
                        partial=Count(
                            "trip_orders",
                            filter=Q(trip_orders__status=OrderConstants.OrderStatus.PARTIAL),
                        ),
                        attempted=Count(
                            "trip_orders",
                            filter=Q(
                                trip_orders__status__in=[
                                    OrderConstants.OrderStatus.SUCCESSFUL,
                                    OrderConstants.OrderStatus.PARTIAL,
                                    OrderConstants.OrderStatus.FAILED,
                                ]
                            ),
                        ),
                        failed=Count(
                            "trip_orders",
                            filter=Q(trip_orders__status=OrderConstants.OrderStatus.FAILED),
                        ),
                    )
                    total_orders = trip_orders_counts.get("total_count")
                    completed_orders = trip_orders_counts.get("completed")
                    attempted_orders = trip_orders_counts.get("attempted")
                    failed_orders = trip_orders_counts.get("failed")
                    partial_orders = trip_orders_counts.get("partial")
                    if trips:
                        distinct_trips = trips.distinct("driver")
                        driver_list = [trip.driver.user.full_name for trip in distinct_trips]
                        driver_names = ",".join(driver_list)
                        report_data.append(
                            [
                                report_date,
                                vehicle.vehicle_plate_no,
                                vehicle.project.project_name,
                                driver_names,
                                trips.count(),
                                total_orders,
                                attempted_orders,
                                completed_orders,
                                failed_orders,
                                partial_orders,
                            ]
                        )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "driver_order_delivery"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def vehicle_trips(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        report_data = [
            [
                "Date",
                "Vehicle Number",
                "Project",
                "Driver Name",
                "No of Trips",
                "Completed",
                "Paused",
            ]
        ]
        queryset = queryset.filter(project__project_id__in=self.request.user.projects_with_access)
        if start_date and end_date:
            for date in daterange(
                datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            ):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                for vehicle in queryset:
                    trips = vehicle.vehicle_trips.filter(trip_date=date)
                    if trips:
                        distinct_trips = trips.distinct("driver")
                        driver_list = [trip.driver.user.full_name for trip in distinct_trips]
                        driver_names = ",".join(driver_list)
                        trip_status = trips.aggregate(
                            completed_trip=Count("id", filter=Q(status=TripStatus.COMPLETED)),
                            paused_trip=Count("id", filter=Q(status=TripStatus.PAUSED)),
                        )
                        completed_trip = trip_status.get("completed_trip")
                        paused_trip = trip_status.get("paused_trip")
                        report_data.append(
                            [
                                report_date,
                                vehicle.vehicle_plate_no,
                                vehicle.project.project_name,
                                driver_names,
                                trips.count(),
                                completed_trip,
                                paused_trip,
                            ]
                        )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "driver_trips"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)


class DriverReportsViewSet(viewsets.GenericViewSet):
    serializer_class = DriverSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_class = DriverReportFilter

    def get_queryset(self):
        return Driver.objects.all()

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def driver_attandance(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        report_data = [
            [
                "Date",
                "Driver Name",
                "Vehicle number",
                "Project",
                "Duty Hours",
                "Duty Start Time",
                "Duty End time",
                "No of Trips",
                "Overtime",
            ]
        ]
        queryset = queryset.filter(project__project_id__in=self.request.user.projects_with_access)
        if start_date and end_date:
            for date in daterange(
                datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            ):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                drivers = queryset.filter(attendance_logs__duty_start__date=date)
                for driver in drivers:
                    vehicle = (
                        driver.vehicle_assigned.vehicle_plate_no if driver.vehicle_assigned else ""
                    )
                    duty_hours = "{}-{}".format(
                        driver.shift_start.strftime(FieldConstants.TIME_FORMAT),
                        driver.shift_end.strftime(FieldConstants.TIME_FORMAT),
                    )
                    first_trip = (
                        driver.driver_trips.filter(trip_date=date).order_by("trip_start").first()
                    )
                    last_trip = (
                        driver.driver_trips.filter(trip_date=date).order_by("-trip_end").first()
                    )
                    total_trips = driver.driver_trips.filter(trip_date=date).count()
                    regular_working_hours = datetime.combine(
                        date.today(), driver.shift_end
                    ) - datetime.combine(date.today(), driver.shift_start)
                    overtime = "0"
                    curr_duty_start = (
                        driver.attendance_logs.filter(duty_start__date=date)
                        .order_by("duty_start")
                        .first()
                    )
                    curr_duty_end = (
                        driver.attendance_logs.filter(duty_start__date=date)
                        .order_by("-duty_end")
                        .first()
                    )
                    duty_start = curr_duty_start.duty_start
                    duty_end = curr_duty_end.duty_end
                    start_time = ""
                    end_time = ""
                    if duty_start:
                        start_time = timezone.localtime(duty_start).strftime("%H:%M")
                    if duty_end:
                        end_time = timezone.localtime(duty_end).strftime("%H:%M")
                    if first_trip and last_trip:
                        if first_trip.trip_start and last_trip.trip_end:
                            start_time = timezone.localtime(first_trip.trip_start).strftime("%H:%M")
                            current_working_hours = last_trip.trip_end - first_trip.trip_start
                            end_time = timezone.localtime(last_trip.trip_end).strftime("%H:%M")
                        elif first_trip.trip_start and not last_trip.trip_end:
                            start_time = timezone.localtime(first_trip.trip_start).strftime("%H:%M")
                            current_working_hours = datetime.combine(
                                date.today(), driver.shift_end
                            ) - first_trip.trip_start.replace(tzinfo=None)
                        else:
                            current_working_hours = timedelta(0)
                        if current_working_hours > regular_working_hours:
                            overtime_delta = current_working_hours - regular_working_hours
                            overtime = (datetime.min + overtime_delta).time().strftime("%H:%M")
                        else:
                            overtime = "0"

                    report_data.append(
                        [
                            report_date,
                            driver.user.full_name,
                            vehicle,
                            driver.project.project_name,
                            duty_hours,
                            start_time,
                            end_time,
                            str(total_trips),
                            overtime,
                        ]
                    )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "driver_attandance"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def driver_expense(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        expenses = request.query_params.get("expenses")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        report_data = [
            [
                "Date",
                "Driver Name",
                "Vehicle",
                "Project ID",
                "Expense Name",
                "Expense Category",
                "Amount",
                "Notes",
            ]
        ]
        queryset = queryset.filter(project__project_id__in=self.request.user.projects_with_access)
        if start_date and end_date:
            for date in daterange(
                datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            ):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                for driver in queryset:
                    expense_filter = {"trip__trip_date": date}
                    if expenses:
                        expens_categories = expenses.split(",")
                        expense_filter.update({"expense_category__in": expens_categories})
                    driver_expenses = driver.driver_expense.filter(**expense_filter)
                    for expense in driver_expenses:
                        report_data.append(
                            [
                                report_date,
                                driver.user.full_name,
                                expense.trip.vehicle.vehicle_plate_no,
                                driver.project.project_name,
                                expense.expense_name,
                                expense.get_expense_category_display(),
                                expense.amount,
                                expense.notes,
                            ]
                        )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "driver_expenses"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def driver_order_delivery(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        report_data = [
            [
                "Date",
                "Driver Name",
                "Vehicle Number",
                "Project",
                "Duty Start Time",
                "Duty End Time",
                "No of Trips",
                "No of Orders",
                "Attempted",
                "Delivered",
                "Returned",
                "Partially Delivered",
            ]
        ]
        queryset = queryset.filter(project__project_id__in=self.request.user.projects_with_access)
        if start_date and end_date:
            for date in daterange(
                datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            ):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                for driver in queryset:
                    trips = driver.driver_trips.filter(trip_date=date)
                    trip_orders_counts = trips.aggregate(
                        total_count=Count("trip_orders"),
                        completed=Count(
                            "trip_orders",
                            filter=Q(trip_orders__status=OrderConstants.OrderStatus.SUCCESSFUL),
                        ),
                        attempted=Count(
                            "trip_orders",
                            filter=Q(
                                trip_orders__status__in=[
                                    OrderConstants.OrderStatus.SUCCESSFUL,
                                    OrderConstants.OrderStatus.PARTIAL,
                                    OrderConstants.OrderStatus.FAILED,
                                ]
                            ),
                        ),
                        failed=Count(
                            "trip_orders",
                            filter=Q(trip_orders__status=OrderConstants.OrderStatus.FAILED),
                        ),
                        partial=Count(
                            "trip_orders",
                            filter=Q(trip_orders__status=OrderConstants.OrderStatus.PARTIAL),
                        ),
                    )
                    total_orders = trip_orders_counts.get("total_count")
                    completed_orders = trip_orders_counts.get("completed")
                    attempted_orders = trip_orders_counts.get("attempted")
                    failed_orders = trip_orders_counts.get("failed")
                    partial_orders = trip_orders_counts.get("partial")
                    if trips:
                        first_trip = trips.order_by("trip_start").first().trip_start
                        last_trip = trips.order_by("-trip_end").first().trip_end
                        vehicles = trips.values_list(
                            "vehicle__vehicle_plate_no", flat=True
                        ).distinct()
                        vehicle_names = ",".join(vehicles)
                        duty_start_time = ""
                        duty_end_time = ""
                        if first_trip:
                            duty_start_time = timezone.localtime(first_trip).strftime("%H:%M")
                        if last_trip:
                            duty_end_time = timezone.localtime(last_trip).strftime("%H:%M")

                        report_data.append(
                            [
                                report_date,
                                driver.user.full_name,
                                vehicle_names,
                                driver.project.project_name,
                                duty_start_time,
                                duty_end_time,
                                trips.count(),
                                total_orders,
                                attempted_orders,
                                completed_orders,
                                failed_orders,
                                partial_orders,
                            ]
                        )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "driver_order_delivery"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def driver_trips(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        report_data = [
            [
                "Date",
                "Driver Name",
                "Vehicle Number",
                "Project",
                "Duty Start Time",
                "Duty End Time",
                "No of Trips",
                "Completed",
                "Paused",
            ]
        ]
        queryset = queryset.filter(project__project_id__in=self.request.user.projects_with_access)
        if start_date and end_date:
            for date in daterange(
                datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d")
            ):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                for driver in queryset:
                    trips = driver.driver_trips.filter(trip_date=date)
                    if trips:
                        first_trip = trips.order_by("trip_start").first().trip_start
                        last_trip = trips.order_by("-trip_end").first().trip_end
                        vehicles = trips.values_list(
                            "vehicle__vehicle_plate_no", flat=True
                        ).distinct()
                        vehicle_names = ",".join(vehicles)
                        duty_start_time = ""
                        duty_end_time = ""
                        trip_status = trips.aggregate(
                            completed_trip=Count("id", filter=Q(status=TripStatus.COMPLETED)),
                            paused_trip=Count("id", filter=Q(status=TripStatus.PAUSED)),
                        )
                        completed_trip = trip_status.get("completed_trip")
                        paused_trip = trip_status.get("paused_trip")
                        if first_trip:
                            duty_start_time = timezone.localtime(first_trip).strftime("%H:%M")
                        if last_trip:
                            duty_end_time = timezone.localtime(last_trip).strftime("%H:%M")
                        report_data.append(
                            [
                                report_date,
                                driver.user.full_name,
                                vehicle_names,
                                driver.project.project_name,
                                duty_start_time,
                                duty_end_time,
                                trips.count(),
                                completed_trip,
                                paused_trip,
                            ]
                        )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "driver_trips"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)


class OrderReportsViewSet(viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_class = OrderReportFilter

    def get_queryset(self):
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        sd, ed = manage_start_end_date(start_date=start_date, end_date=end_date, duration=15)
        return Order.objects.filter(execution_date__range=(sd, ed))

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def orders(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        queryset = queryset.filter(project__project_id__in=self.request.user.projects_with_access)
        report_data = [
            [
                "Date",
                "Project",
                "Reference Number",
                "Invoice Number",
                "Order Type",
                "Status",
                "Order Value",
                "Payment Type",
                "Payment Collection",
                "COD Remarks",
                "Driver",
                "Customer Name",
                "Address",
                "Delivery Point",
                "Chilled Items",
                "Dry Items",
                "Frozen Items",
                "Service Type",
                "Order Remarks",
                "Reasons",
            ]
        ]

        order_status_mapping = {
            OrderConstants.OrderStatus.UNASSIGNED: "Unassigned",
            OrderConstants.OrderStatus.ASSIGNED: "Assigned",
            OrderConstants.OrderStatus.PICKED_UP: "Shipped",
            OrderConstants.OrderStatus.SUCCESSFUL: "Delivered",
            OrderConstants.OrderStatus.FAILED: "Returned",
            OrderConstants.OrderStatus.PARTIAL: "Partially Delivered",
            OrderConstants.OrderStatus.CANCELLED: "Cancelled",
        }
        order_status_whens = [
            When(status=k, then=Value(v)) for k, v in order_status_mapping.items()
        ]
        if start_date and end_date:
            start_date, end_date = manage_start_end_date(
                start_date=start_date, end_date=end_date, duration=15
            )
            for date in daterange(start_date, end_date):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                orders = queryset.filter(execution_date=date).annotate(
                    order_status=Case(*order_status_whens, output_field=models.CharField()),
                    project_name=F("project__project_name"),
                )
                for order in orders:
                    if order.delivery_point:
                        delivery_point = order.delivery_point
                    elif order.order_type == OrderConstants.OrderType.DELIVERY:
                        delivery_point = order.drop_point
                    else:
                        delivery_point = order.pickup_point

                    delivery_point = lat_long_str_format(delivery_point)
                    items = order.get_storage_wise_item_quantity(order)
                    chilled_items = items.get("chilled")
                    dry_items = items.get("dry")
                    frozen_items = items.get("frozen")
                    report_data.append(
                        [
                            report_date,
                            order.project_name,
                            order.reference_number,
                            order.invoice_number,
                            order.get_order_type_display(),
                            order.order_status,
                            order.order_value,
                            order.get_payment_type_display(),
                            order.payment_collected,
                            order.cod_remarks,
                            order.driver,
                            order.customer_name,
                            order.address(),
                            delivery_point,
                            chilled_items,
                            dry_items,
                            frozen_items,
                            order.get_service_type_display(),
                            order.order_remarks,
                            order.status_keyword.name if order.status_keyword else "N/A",
                        ]
                    )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "orders"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)


class TripReportsViewSet(viewsets.GenericViewSet):
    serializer_class = TripSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_class = TripReportFilter

    def get_queryset(self):
        return (
            Trip.objects.prefetch_related("trip_orders").select_related("driver", "vehicle").all()
        )

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def trips(self, request):
        user = request.user
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        report_data = [
            [
                "Date",
                "Trip Reference Number",
                "Status",
                "Total Distance",
                "Start Time",
                "End Time",
                "Total Travelling Time",
                "Total Break Time",
                "Driver",
                "Helper Name",
                "Vehicle Number",
                "Total Orders",
                "Delivered Orders",
                "Partially Delivered Orders",
                "Returned Orders",
                "Pending Orders",
                "Total Ordered Items",
                "Total Delivered Items",
                "Box Capacity",
                "Trip Start KM",
                "Trip End KM",
            ]
        ]
        queryset = queryset.filter(
            trip_orders__project__project_id__in=self.request.user.projects_with_access
        )
        if start_date and end_date:
            start_date, end_date = manage_start_end_date(
                start_date=start_date, end_date=end_date, duration=15
            )

            for date in daterange(start_date, end_date):
                report_date = date.strftime(FieldConstants.DATE_FORMAT)
                trips = queryset.filter(trip_date=date)
                for trip in trips:
                    helper_name = trip.helper_name or ""
                    actual_distance = trip.actual_distance or ""
                    actual_start_time = date_str_format(trip.trip_start)
                    actual_end_time = date_str_format(trip.trip_end)
                    trip_orders_count = trip.trip_order_count()

                    trip_orders_quantity = trip.trip_orders.aggregate(
                        total_ordered=Sum("order_items__original_quantity"),
                        total_delivered=Sum("order_items__delivered_quantity"),
                    )
                    total_orders = trip_orders_count.get("total")
                    pending_orders = trip_orders_count.get("assigned") + trip_orders_count.get(
                        "picked_up"
                    )
                    delivered_orders = trip_orders_count.get("successful")
                    partially_delivered_orders = trip_orders_count.get("partially_delivered")
                    returned_orders = trip_orders_count.get("failed")
                    ordered_items_sum = trip_orders_quantity.get("total_ordered", 0)
                    delivered_items_sum = trip_orders_quantity.get("total_delivered", 0)
                    ordered_items = ordered_items_sum if ordered_items_sum else ""
                    delivered_items = delivered_items_sum if delivered_items_sum else ""
                    used_boxes_capacity = float(trip.total_item_cbm()) / settings.BOX_UNIT
                    box_capacity = f"{math.ceil(used_boxes_capacity)}/{trip.vehicle.box_capacity}"
                    report_data.append(
                        [
                            report_date,
                            trip.reference_number,
                            trip.get_status_display(),
                            actual_distance,
                            actual_start_time,
                            actual_end_time,
                            trip.travelling_time,
                            trip.break_time,
                            trip.driver.user.full_name,
                            helper_name,
                            trip.vehicle.vehicle_plate_no,
                            total_orders,
                            delivered_orders,
                            partially_delivered_orders,
                            returned_orders,
                            pending_orders,
                            ordered_items,
                            delivered_items,
                            box_capacity,
                            trip.trip_start_km,
                            trip.trip_end_km,
                        ]
                    )
            if request.query_params.get("download") == "true":
                host = request.META["HTTP_HOST"]
                report_name = "trips"
                excel_file = create_excel_report(
                    report_data, report_name, start_date, end_date, host, user
                )
                return Response({"report": excel_file}, status=200)
            return Response({"report_data": report_data}, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def operation_scorecard(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        response_data = {}
        queryset = self.filter_queryset(self.get_queryset()).distinct()
        total_num_of_vehicles = Vehicle.objects.filter(~Q(status=VehicleStatus.DEACTIVATED)).count()

        if not start_date and not end_date:
            start_date = (timezone.now() - timedelta(days=7)).date()
            end_date = timezone.now().date() - timedelta(days=1)

        if start_date and end_date:
            queryset = queryset.filter(trip_date__range=(start_date, end_date))
            num_of_used_vehicles = queryset.values_list("vehicle", flat=True).distinct().count()
            all_cbm = []
            for trip in queryset:
                trip_cbm = trip.total_item_cbm()
                cbm_percentage = trip_cbm * 100 / trip.vehicle.cbm_capacity
                all_cbm.append(cbm_percentage)

            avg_fleet_capacity_utilization = (sum(all_cbm) / len(all_cbm)) if len(all_cbm) else 0
            avg_vehicle_utilization = (num_of_used_vehicles * 100) / total_num_of_vehicles

            order_details = Order.objects.filter(
                execution_date__range=(start_date, end_date), trip__in=queryset
            ).aggregate(
                same_day_delivery=Count(
                    "id",
                    filter=Q(
                        completed_on__date=F("execution_date"),
                        status=OrderConstants.OrderStatus.SUCCESSFUL,
                    ),
                    distinct=True,
                ),
                completed_orders=Count(
                    "id", filter=Q(status=OrderConstants.OrderStatus.SUCCESSFUL), distinct=True
                ),
                no_of_drops=Count(
                    "customer_address",
                    filter=Q(status=OrderConstants.OrderStatus.SUCCESSFUL),
                    distinct=True,
                ),
                no_of_cases=Coalesce(
                    Sum(
                        "order_items__delivered_cases",
                        filter=Q(status=OrderConstants.OrderStatus.SUCCESSFUL),
                    ),
                    Value(0),
                    output_field=IntegerField(),
                    distinct=True,
                ),
            )

            # 1) Fleet Utilization % (Average utilization of all vehicles used)
            response_data.update(
                {"avg_fleet_utilization": f"{math.ceil(avg_vehicle_utilization)} %"}
            )
            response_data.update(
                {"avg_fleet_capacity_utilization": f"{math.ceil(avg_fleet_capacity_utilization)} %"}
            )

            # 2) Total number of drops (customers) per truck
            drop_per_truck = 0
            if num_of_used_vehicles:
                drop_per_truck = order_details.get("no_of_drops") / num_of_used_vehicles
            response_data.update({"drop_per_truck": math.ceil(drop_per_truck)})

            # 3) Number of orders completed per day
            response_data.update({"delivered_orders": order_details.get("completed_orders")})

            # 4) Number of same day service customer drops completed
            response_data.update({"same_day_delivery": order_details.get("same_day_delivery")})

            # 5) Number of self collections completed
            # Removed As Of Now:

            # 6) Avg number of cases delivered per truck
            cases_per_truck = 0
            if num_of_used_vehicles and order_details.get("no_of_cases"):
                cases_per_truck = order_details.get("no_of_cases") / num_of_used_vehicles
            response_data.update({"cases_per_truck": math.ceil(cases_per_truck)})

            # 7) Avg number of cases per drop (customer)
            avg_cases_per_drop = 0
            if order_details.get("no_of_drops") and order_details.get("no_of_cases"):
                avg_cases_per_drop = order_details.get("no_of_cases") / order_details.get(
                    "no_of_drops"
                )
            response_data.update({"avg_cases_per_drop": math.ceil(avg_cases_per_drop)})

            # 8) Number of drops (customers) delivered
            response_data.update({"no_of_drops": order_details.get("no_of_drops")})

            # 9) Number of cases delivered
            response_data.update({"no_of_cases": math.ceil(order_details.get("no_of_cases"))})

            return Response(response_data, status=200)
        else:
            return Response({"error": "Start Date and End Date Required"}, status=400)
