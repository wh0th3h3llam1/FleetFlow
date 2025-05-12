import math
from calendar import monthrange

from django.db.models import Sum, F, Avg, Value
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK

from common.constants import FieldConstants
from common.utils import daterange, manage_start_end_date
from dms.models import TripStatistics, VehicleStatistics, OrderStatistics, DriverStatistics


class Dashboard(viewsets.GenericViewSet):

    @action(methods=["get"], detail=False)
    def orders(self, request, *args, **kwargs):
        month_str = self.request.query_params.get("month")
        year_str = self.request.query_params.get("year")
        if month_str and year_str:
            month_int = int(month_str)
            year_int = int(year_str)
        else:
            month_int = timezone.now().date().month
            year_int = timezone.now().date().year
            if timezone.now().date().day < 10 and month_int == 1:
                month_int = 12
            elif timezone.now().date().day < 10:
                month_int = month_int - 1
        report_objects = OrderStatistics.objects.filter(
            date__month=month_int, date__year=year_int
        ).order_by("date")
        start_date = timezone.now().date().replace(day=1, month=month_int, year=year_int)
        end_date = start_date.replace(day=monthrange(year_int, start_date.month)[1])
        report_data = {}
        for date in daterange(start_date, end_date):
            report_date = date.strftime("%Y-%m-%d")
            obj = report_objects.filter(date=date).first()
            report_data.update(
                {
                    report_date: {
                        "total": obj.total_orders if obj else 0,
                        "successful": obj.successful_orders if obj else 0,
                        "failed": obj.failed_orders if obj else 0,
                        "partially_delivered": obj.partially_delivered_orders if obj else 0,
                    }
                }
            )
        return JsonResponse({"order_graph": report_data}, status=HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def fleet_utlization(self, request, *args, **kwargs):
        s_d = request.query_params.get("start_date", None)
        e_d = request.query_params.get("end_date", None)

        start_date, end_date = manage_start_end_date(s_d, e_d, duration=7)

        vehicles = VehicleStatistics.objects.filter(date__range=(start_date, end_date))
        drivers = DriverStatistics.objects.filter(date__range=(start_date, end_date))
        orders = OrderStatistics.objects.filter(date__range=(start_date, end_date))

        fleet_utilization_data = dict()

        for i in daterange(start_date, end_date):
            o = orders.filter(date=i)
            v = vehicles.filter(date=i)
            d = drivers.filter(date=i)
            unique_drop_points = o.first().unique_drop_points if o else 0
            utilized_vehicle_count = v.first().utilized_vehicles if v else 0
            utilized_driver_count = d.first().utilized_drivers if d else 0

            fleet_utilization_data.update(
                {
                    f"{i.strftime(FieldConstants.DATE_FORMAT)}": {
                        "drop_points_per_day": unique_drop_points,
                        "utilized_vehicle_count": utilized_vehicle_count,
                        "utilized_driver_count": utilized_driver_count,
                    }
                }
            )
        return JsonResponse(fleet_utilization_data, status=HTTP_200_OK)

    @action(methods=["get"], detail=False, permission_classes=(IsAuthenticated,))
    def scorecard(self, request):

        s_d = request.query_params.get("start_date", None)
        e_d = request.query_params.get("end_date", None)

        start_date, end_date = manage_start_end_date(s_d, e_d, duration=7)

        trips = TripStatistics.objects.filter(date__range=(start_date, end_date))
        vehicles = VehicleStatistics.objects.filter(date__range=(start_date, end_date))
        orders = OrderStatistics.objects.filter(date__range=(start_date, end_date))

        trip_data = trips.aggregate(
            avg_fleet_capacity_utilization=Coalesce(
                Avg("avg_fleet_capacity_utilization", output_field=IntegerField()), Value(0)
            )
        )

        vehicle_data = vehicles.aggregate(
            utilized_vehicles=Coalesce(Sum("utilized_vehicles"), Value(0)),
            avg_fleet_utilization=Coalesce(
                Avg(
                    (F("utilized_vehicles") * 100) / F("total_vehicles"),
                    output_field=IntegerField(),
                ),
                Value(0),
            ),
        )

        order_data = orders.aggregate(
            total_orders=Coalesce(Sum("total_orders"), Value(0)),
            successful_orders=Coalesce(Sum("successful_orders"), Value(0)),
            partially_delivered_orders=Coalesce(Sum("partially_delivered_orders"), Value(0)),
            same_day_delivery=Coalesce(Sum("same_day_delivery"), Value(0)),
            no_of_drops=Coalesce(Sum("unique_drop_points"), Value(0)),
            no_of_cases=Coalesce(Sum("total_cases"), Value(0)),
        )

        no_of_drops = order_data.get("no_of_drops", 0)
        no_of_cases = order_data.get("no_of_cases", 0)
        utilized_vehicles = vehicle_data.pop("utilized_vehicles", 0)

        cases_per_truck = math.ceil((no_of_cases / utilized_vehicles) if utilized_vehicles else 0)
        drop_per_truck = math.ceil((no_of_drops / utilized_vehicles) if utilized_vehicles else 0)
        average_cases_per_drop = math.ceil((no_of_cases / no_of_drops) if no_of_drops else 0)

        extras = {
            "cases_per_truck": cases_per_truck,
            "drops_per_truck": drop_per_truck,
            "average_cases_per_drop": average_cases_per_drop,
        }

        data = {**trip_data, **order_data, **vehicle_data, **extras}

        try:
            avg_fleet_utilization = math.ceil(data.get("avg_fleet_utilization", 0))
            avg_fleet_capacity_utilization = math.ceil(
                data.get("avg_fleet_capacity_utilization", 0)
            )

        except TypeError:
            avg_fleet_utilization = 0
            avg_fleet_capacity_utilization = 0

        delivered_orders = data.get("successful_orders", 0) + data.get(
            "partially_delivered_orders", 0
        )

        scorecard = {
            "avg_fleet_utilization": f"{avg_fleet_utilization} %",
            "avg_fleet_capacity_utilization": f"{avg_fleet_capacity_utilization} %",
            "delivered_orders": delivered_orders,
            "same_day_delivery": data.get("same_day_delivery", 0),
            "total_no_of_cases": data.get("no_of_cases", 0),
            "total_no_of_drops": data.get("no_of_drops", 0),
            "avg_cases_per_truck": data.get("cases_per_truck", 0),
            "drops_per_truck": data.get("drops_per_truck", 0),
            "avg_cases_per_drop": data.get("average_cases_per_drop", 0),
        }
        return JsonResponse(scorecard, status=HTTP_200_OK)
