import logging
import math
from datetime import date, datetime

from django.conf import settings
from django.db.models import Avg, Count, F, Q, Sum, IntegerField
from django.db.models.expressions import Value
from django.db.models.functions.comparison import Coalesce
from django.db.utils import IntegrityError

from common.constants import OrderConstants, TripStatus, VehicleStatus
from common.utils import daterange, get_days_hours_minutes
from dms.models import (
    Driver,
    Order,
    Trip,
    Vehicle,
    ReportUtilization,
    DriverStatistics,
    OrderStatistics,
    TripStatistics,
    VehicleStatistics,
    StatusKeyword,
    DriverExpense,
    OrderItem,
)

logger = logging.getLogger(__name__)


def generate_trip_stats(start_date, end_date):

    result = list()
    trips = Trip.objects.filter(status=TripStatus.COMPLETED)

    for i in daterange(start_date=start_date, end_date=end_date):

        try:
            t = trips.filter(trip_date=i)
            trip_count = t.count()
            if trip_count:

                trip_statistics = t.aggregate(
                    total_trip_duration=Sum(F("trip_end") - F("trip_start")),
                    total_distance=Sum("actual_distance"),
                    planned_travelling_time=Sum("planned_travelling_time"),
                    total_travelling_time=Sum("travelling_time"),
                    total_break_time=Sum("break_time"),
                    total_processing_time=Sum("processing_time"),
                    average_trip_duration=Avg(F("trip_end") - F("trip_start")),
                    average_travelling_time=Avg("travelling_time"),
                    average_break_time=Avg("break_time"),
                    average_processing_time=Avg("processing_time"),
                )

                trip_expenses = (
                    DriverExpense.objects.filter(trip__in=t)
                    .aggregate(
                        expense=Coalesce(Sum("amount"), Value(0), output_field=IntegerField())
                    )
                    .get("expense")
                )
                trip_orders = Order.objects.filter(trip__in=t)

                total_drop_points = trip_orders.values("customer_address").distinct().count()
                total_cases_dropped = sum(
                    list(trip_orders.values_list("order_items__delivered_cases", flat=True))
                )

                # To Calculate Driver Overtime and Total CBM Percentage
                total_overtime_minutes = 0
                total_per_util = list()
                total_trip_distance = 0
                for trip in t:
                    driver_overtime = 0
                    try:
                        driver = trip.driver
                        trip_start_time = trip.trip_start.time()
                        trip_end_time = trip.trip_end.time()

                        if driver.shift_start > trip_start_time:
                            driver_overtime += (
                                datetime.combine(date.today(), driver.shift_start)
                                - datetime.combine(date.today(), trip_start_time)
                            ).seconds // 60
                        if driver.shift_end < trip_end_time:
                            driver_overtime += (
                                datetime.combine(date.today(), trip_end_time)
                                - datetime.combine(date.today(), driver.shift_end)
                            ).seconds // 60

                    except Exception as e:
                        logger.exception(e)
                    total_overtime_minutes += driver_overtime

                    trip_cbm = trip.total_item_cbm()
                    try:
                        used_cbm_percentage = (trip_cbm * 100) / trip.vehicle.cbm_capacity
                    except:
                        used_cbm_percentage = 0
                    total_per_util.append(used_cbm_percentage)

                    if trip.actual_distance:
                        total_trip_distance += trip.actual_distance

                average_trip_distance = total_trip_distance / trip_count
                average_overtime = get_days_hours_minutes(
                    total_minutes=int(total_overtime_minutes / trip_count)
                )
                avg_fleet_capacity_util = (
                    (sum(total_per_util) / len(total_per_util)) if total_per_util else 0
                )

                try:
                    average_cases_per_drop = math.ceil(
                        trip_statistics.get("total_cases_dropped", 0)
                        / trip_statistics.get("total_drop_points", 0)
                    )
                except (ZeroDivisionError, TypeError):
                    average_cases_per_drop = 0

                trip_statistics.update(
                    {
                        "total_trip_duration": (trip_statistics.get("total_trip_duration")).seconds
                        // 60,
                        "average_trip_duration": (
                            trip_statistics.get("average_trip_duration")
                        ).seconds
                        // 60,
                        "average_cases_per_drop": average_cases_per_drop,
                        "total_distance": total_trip_distance,
                        "average_distance": average_trip_distance,
                        "total_trips": trip_count,
                        "average_overtime": average_overtime,
                        "avg_fleet_capacity_utilization": avg_fleet_capacity_util,
                        "total_expense": trip_expenses,
                        "average_expense": int(trip_expenses / trip_count),
                        "total_drop_points": total_drop_points,
                        "total_cases_dropped": total_cases_dropped,
                    }
                )
                result.append(
                    TripStatistics.objects.update_or_create(date=i, defaults=trip_statistics)
                )

        except IntegrityError as ie:
            logger.warning(f"IntegrityError for date {i} in generate_trip_stats")
            logger.exception(ie)
        except Exception as e:
            logger.warning(f"Error for date {i} in generate_trip_stats")
            logger.exception(e)

    created = 0
    updated = 0
    for _, v in result:
        if v:
            created += 1
        else:
            updated += 1

    return f"{created} created, {updated} updated"


def generate_order_stats(start_date, end_date):

    result = list()
    orders = (
        Order.objects.prefetch_related("order_items")
        .select_related("customer_address", "status_keyword")
        .exclude(status=OrderConstants.OrderStatus.UNASSIGNED)
    )

    for i in daterange(start_date=start_date, end_date=end_date):

        try:
            o = orders.filter(execution_date=i)
            order_count = o.count()

            if order_count:
                order_statistics = o.aggregate(
                    assigned_orders=Count(
                        "id", filter=Q(status=OrderConstants.OrderStatus.ASSIGNED), distinct=True
                    ),
                    picked_up_orders=Count(
                        "id", filter=Q(status=OrderConstants.OrderStatus.PICKED_UP), distinct=True
                    ),
                    successful_orders=Count(
                        "id", filter=Q(status=OrderConstants.OrderStatus.SUCCESSFUL), distinct=True
                    ),
                    partially_delivered_orders=Count(
                        "id", filter=Q(status=OrderConstants.OrderStatus.PARTIAL), distinct=True
                    ),
                    failed_orders=Count(
                        "id", filter=Q(status=OrderConstants.OrderStatus.FAILED), distinct=True
                    ),
                    cancelled_orders=Count(
                        "id", filter=Q(status=OrderConstants.OrderStatus.CANCELLED), distinct=True
                    ),
                    total_orders=Count("id", distinct=True),
                    same_day_delivery=Count(
                        "id",
                        filter=Q(
                            created__date=F("completed_on__date"),
                            status__in=(
                                OrderConstants.OrderStatus.SUCCESSFUL,
                                OrderConstants.OrderStatus.PARTIAL,
                            ),
                        ),
                    ),
                    delayed_delivery=Count(
                        "id",
                        filter=Q(
                            created__date__lt=F("completed_on__date"),
                            status=OrderConstants.OrderStatus.SUCCESSFUL,
                        ),
                    ),
                    total_drop_points=Count("customer_address"),
                    unique_drop_points=Count("customer_address", distinct=True),
                    total_planned_processing_time=Sum("planned_processing_time"),
                    total_processing_time=Sum("processing_time"),
                    average_processing_time=Avg("planned_processing_time"),
                )
                sk = StatusKeyword.objects.prefetch_related("status_keyword_orders").filter(
                    Q(keyword__iexact="failed") & Q(status_keyword_orders__in=o)
                )

                max_orders_returned = {"keyword_name": "", "count": 0}

                for k in sk:
                    failed_orders_count = k.status_keyword_orders.count()
                    if failed_orders_count >= max_orders_returned.get("count", 0):
                        max_orders_returned.update(
                            {"keyword_name": k.name, "count": failed_orders_count}
                        )

                order_items = OrderItem.objects.filter(order__in=o)

                order_items_data = order_items.aggregate(
                    frozen_items=Count(
                        "item", filter=Q(item__storage_type=OrderConstants.StorageTypes.FROZEN)
                    ),
                    chilled_items=Count(
                        "item", filter=Q(item__storage_type=OrderConstants.StorageTypes.CHILLED)
                    ),
                    dry_items=Count(
                        "item", filter=Q(item__storage_type=OrderConstants.StorageTypes.DRY)
                    ),
                    total_order_items=Sum("original_quantity"),
                    total_cases=Sum("total_cases", output_field=IntegerField()),
                    total_boxes=(
                        Sum("line_item_cbm", output_field=IntegerField()) / settings.BOX_UNIT
                    ),
                    total_weight=Sum("line_item_cbm", output_field=IntegerField()),
                    total_volume=Sum("line_item_weight", output_field=IntegerField()),
                    average_volume=Avg("line_item_cbm", output_field=IntegerField()),
                    average_weight=Avg("line_item_weight", output_field=IntegerField()),
                )

                order_statistics.update(
                    {"max_orders_returned": max_orders_returned.get("keyword_name")}
                )
                data = {**order_statistics, **order_items_data}
                result.append(OrderStatistics.objects.update_or_create(date=i, defaults=data))

        except IntegrityError as ie:
            logger.warning(f"IntegrityError for date {i} in generate_order_stats")
            logger.exception(ie)
        except Exception as e:
            logger.warning(f"Error for date {i} in generate_order_stats")
            logger.exception(e)

    created = 0
    updated = 0
    for _, v in result:
        if v:
            created += 1
        else:
            updated += 1

    return f"{created} created, {updated} updated"


def generate_driver_stats(start_date, end_date):

    result = list()
    drivers = Driver.objects.prefetch_related("driver_trips")

    for i in daterange(start_date=start_date, end_date=end_date):

        try:
            d = drivers.filter(driver_trips__trip_date=i)
            driver_count = d.count()

            if driver_count:

                driver_statistics = d.aggregate(
                    utilized_drivers=Count("id"),
                )

                for driver in d:
                    data = driver.driver_trips.aggregate(
                        total_kms_driven=Sum("actual_distance", output_field=IntegerField()),
                        total_break_time=Sum("break_time", output_field=IntegerField()),
                        average_kms_driven=Avg("actual_distance", output_field=IntegerField()),
                        average_break_time=Avg("break_time", output_field=IntegerField()),
                    )

                    driver_statistics.update(**data)

                total_drivers = drivers.exclude(is_active=False).count()
                idle_drivers = total_drivers - driver_count

                driver_statistics.update(
                    {
                        "total_drivers": total_drivers,
                        "idle_drivers": idle_drivers,
                    }
                )

                result.append(
                    DriverStatistics.objects.update_or_create(date=i, defaults=driver_statistics)
                )

        except IntegrityError as ie:
            logger.warning(f"IntegrityError for date {i} in generate_driver_stats")
            logger.exception(ie)
        except Exception as e:
            logger.warning(f"Error for date {i} in generate_driver_stats")
            logger.exception(e)

    created = 0
    updated = 0
    for _, v in result:
        if v:
            created += 1
        else:
            updated += 1

    return f"{created} created, {updated} updated"


def generate_vehicle_stats(start_date, end_date):

    result = list()
    vehicles = Vehicle.objects.prefetch_related("vehicle_trips")

    for i in daterange(start_date=start_date, end_date=end_date):
        try:

            v = vehicles.filter(vehicle_trips__trip_date=i)
            vehicle_count = v.count()

            if vehicle_count:

                vehicle_statistics = v.aggregate(
                    utilized_vehicles=Count("id"),
                    total_tonnage_capacity=Sum("tonnage_capacity"),
                    total_cbm_capacity=Sum("cbm_capacity"),
                    total_box_capacity=Sum("box_capacity"),
                )

                total_vehicles = Vehicle.objects.exclude(
                    status__in=[VehicleStatus.DEACTIVATED]
                ).count()
                vehicle_statistics.update(
                    {
                        "total_vehicles": total_vehicles,
                        "idle_vehicles": total_vehicles
                        - vehicle_statistics.get("utilized_vehicles", 0),
                    }
                )

                result.append(
                    VehicleStatistics.objects.update_or_create(date=i, defaults=vehicle_statistics)
                )

        except IntegrityError as ie:
            logger.warning(f"IntegrityError for date {i} in generate_vehicle_stats")
            logger.exception(ie)
        except Exception as e:
            logger.warning(f"Error for date {i} in generate_vehicle_stats")
            logger.exception(e)

    created = 0
    updated = 0
    for _, v in result:
        if v:
            created += 1
        else:
            updated += 1

    return f"{created} created, {updated} updated"


def report_utilization_report(start_date, end_date):

    result = list()
    trips = (
        Trip.objects.prefetch_related("trip_orders")
        .select_related("driver", "vehicle")
        .filter(trip_date__range=(start_date, end_date), status=TripStatus.COMPLETED)
    )

    for i in daterange(start_date, end_date):

        try:
            t = trips.filter(trip_date=i)

            trip_count = t.count()

            if trip_count:
                report_utilization = t.aggregate(
                    total_vehicle_count=Count("vehicle"),
                    utilized_vehicle_count=Count("vehicle", distinct=True),
                    total_driver_count=Count("driver"),
                    utilized_driver_count=Count("driver", distinct=True),
                    total_distance_count=Sum("actual_distance"),
                    average_distance_per_trip=Avg("actual_distance"),
                    total_traveling_time=Sum("travelling_time"),
                    average_traveling_time=Avg("travelling_time"),
                    total_break_time=Sum("break_time"),
                    average_break_time=Avg("break_time"),
                    total_handover_time=Sum("processing_time"),
                    average_handover_time=Avg("processing_time"),
                    trip_count=Count("id"),
                    successful_order_count=Count(
                        "trip_orders",
                        filter=Q(trip_orders__status=OrderConstants.OrderStatus.SUCCESSFUL),
                    ),
                    failed_order_count=Count(
                        "trip_orders",
                        filter=Q(trip_orders__status=OrderConstants.OrderStatus.FAILED),
                    ),
                    total_order_count=Count("trip_orders"),
                    total_drop_points_count=Count("trip_orders__customer_address", distinct=True),
                    total_customer_count=Count("trip_orders__customer_address"),
                )
                total_vehicles = report_utilization.pop("total_vehicle_count", 0)
                total_drivers = report_utilization.pop("total_driver_count", 0)

                idle_vehicle_count = total_vehicles - report_utilization.get(
                    "utilized_vehicle_count"
                )
                idle_driver_count = total_drivers - report_utilization.get("utilized_driver_count")

                average_drop_points_per_trip_count = (
                    report_utilization.get("total_drop_points_count", 0) / trip_count
                )
                average_order_count_per_trip_count = (
                    report_utilization.get("total_order_count", 0) / trip_count
                )

                report_utilization.update(
                    {
                        "idle_vehicle_count": idle_vehicle_count,
                        "idle_driver_count": idle_driver_count,
                        "average_drop_points_per_trip_count": average_drop_points_per_trip_count,
                        "average_order_count_per_trip_count": average_order_count_per_trip_count,
                    }
                )

                result.append(
                    ReportUtilization.objects.update_or_create(date=i, defaults=report_utilization)
                )
        except IntegrityError as ie:
            logger.warning(f"IntegrityError for date {i} in report_utilization_report")
            logger.exception(ie)
        except Exception as e:
            logger.warning(f"Error for date {i} in report_utilization_report")
            logger.exception(e)

    created = 0
    updated = 0
    for _, v in result:
        if v:
            created += 1
        else:
            updated += 1

    return f"{created} created, {updated} updated"
