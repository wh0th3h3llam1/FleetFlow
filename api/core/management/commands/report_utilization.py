from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone

from dms.models import Driver, Trip, Vehicle, ReportUtilization
from dms.views.reports import daterange
from lib.constants import TripStatus, OrderConstants, VehicleStatus


class Command(BaseCommand):

	def add_arguments(self, parser):
		parser.add_argument('start_date', nargs='?', type=str)
		parser.add_argument('end_date', nargs='?', type=str)

	def handle(self, *args, **kwargs):
		start_date = kwargs.get('start_date')
		end_date = kwargs.get('end_date')
		last_record = ReportUtilization.objects.all().order_by('date').last()
		if start_date and end_date:
			start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
			end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
			if end_date > timezone.now().date():
				end_date = timezone.now().date()
		if not start_date or not end_date:
			if start_date:
				start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
			elif not start_date and last_record:
				start_date = last_record.date
			elif not start_date and not last_record:
				start_date = (timezone.now() - timedelta(days=15)).date()
			end_date = timezone.now().date() - timedelta(days=1)
		for date in daterange(start_date, end_date):
			trip_date = date
			trip_object_list = Trip.objects.prefetch_related('trip_orders').filter(trip_date=trip_date)
			trip_count = trip_object_list.count()
			report_object_data = trip_object_list.aggregate(
				total_order_count=Count('trip_orders'),
				successful_order_count=Count('trip_orders', filter=Q(
					trip_orders__status=OrderConstants.OrderStatus.SUCCESSFUL)),
				failed_order_count=Count('trip_orders', filter=Q(
					trip_orders__status=OrderConstants.OrderStatus.FAILED)),
				total_customer_count=Count('trip_orders__customer_name', filter=Q(
					trip_orders__status=OrderConstants.OrderStatus.SUCCESSFUL), distinct=True),
				total_drop_points_count=Count('trip_orders__customer_address', filter=Q(
					trip_orders__status=OrderConstants.OrderStatus.SUCCESSFUL), distinct=True),
				# average_drop_points_per_day_count=Avg('trip_orders__customer_address', filter=Q(
				# 	status=TripStatus.COMPLETED), distinct=True),
				average_order_count_per_trip_count=Count('trip_orders', filter=Q(
					status=TripStatus.COMPLETED), distinct=True),
				total_distance_count=Sum('actual_distance', filter=Q(
					status=TripStatus.COMPLETED)),
				average_distance_per_trip=Avg('actual_distance', filter=Q(status=TripStatus.COMPLETED)),
				total_traveling_time=Sum('travelling_time', filter=Q(
					status=TripStatus.COMPLETED)),
				average_traveling_time=Avg('travelling_time', filter=Q(status=TripStatus.COMPLETED)),
				total_handover_time=Sum('processing_time', filter=Q(
					status=TripStatus.COMPLETED)),
				average_handover_time=Avg('processing_time', filter=Q(status=TripStatus.COMPLETED)),
				total_break_time=Sum('break_time', filter=Q(
					status=TripStatus.COMPLETED)),
				average_break_time=Avg('break_time', filter=Q(status=TripStatus.COMPLETED)),
			)
			if trip_count and report_object_data.get('total_drop_points_count'):
				average_drop_points_per_trip_count = report_object_data.get(
					'total_drop_points_count')/trip_count
				report_object_data.update({
					'average_drop_points_per_trip_count':int(average_drop_points_per_trip_count)})

			utilized_vehicle_count = trip_object_list.values('vehicle').distinct().count()
			total_vehicle = Vehicle.objects.filter(~Q(status=VehicleStatus.DEACTIVATED)).count()
			idle_vehicle_count = total_vehicle - utilized_vehicle_count

			utilized_driver_count = trip_object_list.values('driver').distinct().count()
			total_driver = Driver.objects.filter(is_active=True).count()
			idle_driver_count = total_driver - utilized_driver_count
			report_object_data.update({
				'date':date,
				'utilized_vehicle_count':utilized_vehicle_count ,'idle_vehicle_count':idle_vehicle_count,
				'utilized_driver_count':utilized_driver_count, 'idle_driver_count':idle_driver_count})
			report_obj = ReportUtilization.objects.get_or_create(date=date, defaults=report_object_data)