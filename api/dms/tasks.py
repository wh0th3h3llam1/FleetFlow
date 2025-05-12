import json
import logging
import math
from datetime import timedelta, date
from secrets import token_urlsafe

from django.conf import settings
from django.utils import timezone

from api import celery_app
from common.constants import (
    OrderConstants,
    CustomerNotificationStatus,
    SensorReadingLogStatus,
    TripTemperatureFileStatus,
)

from common.utils import manage_start_end_date
from dms import helpers, models
from dms.reports.generate_statistics import (
    generate_order_stats,
    generate_driver_stats,
    generate_vehicle_stats,
    generate_trip_stats,
    report_utilization_report,
)
from dms.serializers import OrderSerializer

logger = logging.getLogger(__name__)


@celery_app.task
def send_notification(data):
    """Background for bulk upload"""
    data = json.loads(data)
    email_response = list()
    if isinstance(data, list) and data:
        for order_id in data:
            order = models.Order.objects.get(id=order_id)
            project = models.Project.objects.get(id=order.project.id)

            if (
                project.order_creation_notification
                and order.customer_notifications
                and order.status == OrderConstants.OrderStatus.UNASSIGNED
            ):

                if not order.customer_detail_link:
                    order.unassigned_on = timezone.now()
                    notification_object = models.OrderNotification.objects.create(
                        order=order,
                        notification_id=token_urlsafe(16),
                        status=CustomerNotificationStatus.SCHEDULED,
                    )
                    link = notification_object.get_location_update_url
                    order.customer_detail_link = link
                    order.save()

                data = {
                    "customer_name": order.customer_name,
                    "reference_no": order.reference_number,
                    "delivery_date": order.execution_date.strftime("%d-%m-%Y"),
                    "link": order.customer_detail_link,
                    "receiver_mail": order.contact_email,
                    "contact_number": order.contact_number,
                }
                if (
                    order.contact_email
                    and settings.EMAIL_NOTIFICATION
                    and order.customer_address.email_notification
                ):
                    email_notification(data)
    else:
        order_id = data
        order = models.Order.objects.get(id=order_id)
        project = models.Project.objects.get(id=order.project.id)

        if (
            project.order_creation_notification
            and order.customer_notifications
            and order.status == OrderConstants.OrderStatus.UNASSIGNED
        ):
            if not order.customer_detail_link:
                order.unassigned_on = timezone.now()
                notification_object = models.OrderNotification.objects.create(
                    order=order,
                    notification_id=token_urlsafe(16),
                    status=CustomerNotificationStatus.SCHEDULED,
                )
                link = notification_object.get_location_update_url
                order.customer_detail_link = link
                order.save()
            data = {
                "customer_name": order.customer_name,
                "reference_no": order.reference_number,
                "delivery_date": order.execution_date.strftime("%d-%m-%Y"),
                "link": order.customer_detail_link,
                "receiver_mail": order.contact_email,
                "contact_number": order.contact_number,
            }
            if (
                order.contact_email
                and settings.EMAIL_NOTIFICATION
                and order.customer_address.email_notification
            ):
                helpers.email_notification(data)

    return {
        "email_notification_count": len(email_response),
        "email_notification_list": email_response,
    }


@celery_app.task
def upload_sensor_details():
    files_list = helpers.get_trip_temperature_files()
    successful_list = []
    failed_list = []
    for file_name, uploaded_filename, added_by in files_list:
        data = helpers.get_sensor_metadata_readings(file_name)

        if data["data_found"]:
            try:
                sensor_id = data.get("sensor_id", None).strip()
            except AttributeError as ae:
                reason = f"No Sensor ID Found in {file_name}"
                logger.exception(ae)

                trip_temp_file_obj = models.TripTemperatureFile.objects.get(file_name=file_name)
                trip_temp_file_obj.processed = True
                trip_temp_file_obj.status = TripTemperatureFileStatus.FAILED
                trip_temp_file_obj.save()
                srl = models.SensorReadingLog.objects.create(
                    file_name=file_name,
                    status=SensorReadingLogStatus.FAILED,
                    reason=reason,
                    sensor=None,
                )
                failed_list.append(uploaded_filename)
                continue

            try:
                # Get Vehicle Info from sensor_id
                vs, flag = helpers.get_vehicle_trip_info(sensor_id, file_name)
            except Exception as e:
                logger.exception(e)
                trip_temp_file_obj = models.TripTemperatureFile.objects.get(file_name=file_name)
                trip_temp_file_obj.processed = True
                trip_temp_file_obj.status = TripTemperatureFileStatus.FAILED
                trip_temp_file_obj.save()
                srl = models.SensorReadingLog.objects.create(
                    file_name=file_name, status=SensorReadingLogStatus.FAILED, reason=e, sensor=None
                )
                failed_list.append(uploaded_filename)
                continue

            sensor_temperature_data = data["sensor_temperature_data"]
            if not flag and sensor_temperature_data:
                # Add data in TripTemperatureLog
                kwargs = {
                    "vs": vs,
                    "sensor_id": sensor_id,
                    "sensor_temperature_data": sensor_temperature_data,
                    "file_name": file_name,
                }
                try:
                    trip_temp_log_status = helpers.add_trip_temp_log(kwargs)
                except Exception as e:
                    logger.exception(e)
                    trip_temp_file_obj = models.TripTemperatureFile.objects.get(file_name=file_name)
                    trip_temp_file_obj.processed = True
                    trip_temp_file_obj.status = TripTemperatureFileStatus.FAILED
                    trip_temp_file_obj.save()
                    srl = models.SensorReadingLog.objects.create(
                        file_name=file_name,
                        status=SensorReadingLogStatus.FAILED,
                        reason=e,
                        sensor=None,
                    )
                    failed_list.append(uploaded_filename)
                    continue
                if trip_temp_log_status == SensorReadingLogStatus.SUCCESSFUL:
                    successful_list.append(uploaded_filename)
                    continue

        failed_list.append(uploaded_filename)
        helpers.file_failed_notification(uploaded_filename, added_by)

    return {
        "total_files": len(files_list),
        "successful_file_count": len(successful_list),
        "successful_files_list": ",".join(successful_list),
        "failed_file_count": len(failed_list),
        "failed_files_list": ",".join(failed_list),
    }


@celery_app.task
def calculate_eta():
    """Background task to update estimated time of order for trip"""

    from dms.models import Trip
    from common.constants import TripStatus, OrderConstants

    list_of_trips = list()
    list_of_orders = list()
    minutes_filter = timezone.now() - timedelta(minutes=15)
    trip_list = (
        Trip.objects.prefetch_related("trip_coordinates", "trip_orders")
        .filter(status__in=[TripStatus.ACTIVE, TripStatus.PAUSED])
        .filter(
            last_driver_location__timestamp__gte=minutes_filter, last_driver_location__isnull=False
        )
        .order_by("-last_driver_location")
    )

    for trip in trip_list:
        list_of_trips.append(trip.reference_number)
        order_list = trip.trip_orders.filter(
            status__in=[OrderConstants.OrderStatus.PICKED_UP, OrderConstants.OrderStatus.PARTIAL]
        ).order_by("sequence_number")
        prv_order_processing_time_min = 0
        order_eta_min = 0
        driver_location = trip.last_driver_location
        driver_current_time = driver_location.timestamp
        driver_current_coordinates = driver_location.coordinates
        coordinates = [[driver_current_coordinates.x, driver_current_coordinates.y]]
        for order in order_list:
            list_of_orders.append(order.reference_number)

            if order.order_type == OrderConstants.OrderType.DELIVERY and order.drop_point:
                coordinates.append([order.drop_point.x, order.drop_point.y])
            elif order.pickup_point:
                coordinates.append([order.pickup_point.x, order.pickup_point.y])

            result = helpers.calculate_route(coordinates)
            prv_order_processing_time_min += order.processing_time
            order_eta_min += math.ceil(result["duration_in_min"]) + prv_order_processing_time_min
            order_eta = driver_current_time + timedelta(minutes=order_eta_min)
            logger.info(order_eta)

            if order.order_type == OrderConstants.OrderType.DELIVERY:
                order.est_drop_time = order_eta
            else:
                order.est_pickup_time = order_eta
            order.save()

    return {
        "trips_updated": len(list_of_trips),
        "order_eta_updated": len(list_of_orders),
        "trips": ",".join(list_of_trips),
        "orders": ",".join(list_of_orders),
    }


@celery_app.task
def generate_daily_report(start_date: date = None, end_date: date = None):

    starting_date, ending_date = manage_start_end_date(
        start_date=start_date, end_date=end_date, duration=15
    )

    data = {
        "report_utilization": str(),
        "orders": str(),
        "drivers": str(),
        "vehicles": str(),
        "trips": str(),
    }
    data.update({"report_utilization": report_utilization_report(starting_date, ending_date)})

    data.update({"orders": generate_order_stats(starting_date, ending_date)})

    data.update({"drivers": generate_driver_stats(starting_date, ending_date)})

    data.update({"trips": generate_trip_stats(starting_date, ending_date)})

    data.update({"vehicles": generate_vehicle_stats(starting_date, ending_date)})

    return data


@celery_app.task
def orders_bulk_create(payload_id: int):
    from common.constants import NotificationPriority, NotificationType, NotificationCategory

    try:
        bulk_upload_file = models.OrderUploadFile.objects.get(id=payload_id)
    except models.OrderUploadFile.DoesNotExist as e:
        logger.exception(e)
    else:
        order_data = OrderSerializer(
            data=list(bulk_upload_file.payload.values()),
            many=True,
            exclude=[
                "customer_name",
                "contact_person",
                "contact_email",
                "contact_number",
                "pickup_address",
                "drop_address",
            ],
            context={
                "user": bulk_upload_file.uploaded_by,
                "all_items": models.ItemMaster.objects.all(),
                "all_projects": models.Project.objects.all(),
                "all_customer_addresses": models.CustomerAddress.objects.prefetch_related(
                    "time_slots"
                ),
            },
        )
        if order_data.is_valid(raise_exception=False):
            orders = order_data.save()
            order_list = []
            for order_instance in orders:
                order_list.append(order_instance.id)
            # bulk_upload_notification.apply_async(args=[json.dumps(order_list)])
            send_notification.apply_async(args=[json.dumps(order_list)])
            bulk_upload_file.is_completed = True
            bulk_upload_file.save()

            # User Notification Generated
            notification = models.Notification.objects.create(
                title="Uploaded order file processed successfully",
                message=f"Uploaded order file processed successfully and {len(orders)} orders created.",
                priority=NotificationPriority.HIGH,
                notification_type=NotificationType.INFO,
                notification_category=NotificationCategory.ORDER,
                expiration_time=timezone.now() + timedelta(days=1),
            )
            models.UserNotification.objects.create(
                user=bulk_upload_file.uploaded_by, notification=notification
            )
            return {
                "msg": f"Uploaded order file processed successfully and {len(orders)} orders created."
            }
        else:
            # User Notification Generated
            notification = models.Notification.objects.create(
                title="Unable to process the uploaded order file",
                message=f"Unable to process the uploaded order file payload for id:{bulk_upload_file.id}",
                priority=NotificationPriority.HIGH,
                notification_type=NotificationType.ERROR,
                notification_category=NotificationCategory.ORDER,
                expiration_time=timezone.now() + timedelta(days=1),
            )
            models.UserNotification.objects.create(
                user=bulk_upload_file.uploaded_by, notification=notification
            )

            return {"msg": f"Unable to process the payload for id:{bulk_upload_file.id}"}
