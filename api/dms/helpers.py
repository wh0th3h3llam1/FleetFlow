import json
import logging
import os
import random
from smtplib import SMTPAuthenticationError, SMTPConnectError
import string
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.mail import send_mail
from django.db.models import Case, When
from django.http import HttpResponse
from django.template.loader import get_template
from django.utils import timezone
import pandas as pd
import xlrd
import xlwt
from dateutil import parser


from common.constants import (
    VehicleDocumentType,
    DriverDocumentType,
    TripStatus,
    NotificationPriority,
    NotificationType,
    NotificationCategory,
    SensorReadingLogStatus,
    TripTemperatureFileStatus,
    OrderConstants,
)
from common.osrm import OSRMClient
from common.utils import round_up_in_multiple

logger = logging.getLogger(__name__)


def get_order_attachment_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"order-attachments/{instance.attachment_type}_{filename}"
    return file_path


def get_profile_image_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"users/profile-image/{instance.username}_{filename}"
    return file_path


def get_driver_license_image_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"drivers/license/{instance.user.username}_{filename}"
    return file_path


def get_driver_national_id_image_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"drivers/national-id/{instance.user.username}_{filename}"
    return file_path


def get_driver_visa_image_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"drivers/visa/{instance.user.username}_{filename}"
    return file_path


def get_driver_documents_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"drivers/documents/{instance.driver.user.full_name}_{filename}"
    return file_path


def get_vehicle_documents_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"vehicle/documents/{instance.vehicle.vehicle_plate_no}_{filename}"
    return file_path


def get_vehicle_image_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"vehicle/{instance.vehicle_plate_no}_{filename}"
    return file_path


def get_trip_temp_log_file_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    short_uuid = "".join(random.choices(string.ascii_lowercase, k=8))
    filename = f"{short_uuid}.{ext}"
    file_path = f"trip/temperature_logs/{datetime.now()}_{filename}"
    return file_path


def get_chat_log_location(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"trip/{instance.trip.trip_id}_{filename}"
    return file_path


def get_driver_expense_attachment_path(instance, filename, **kwargs):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    file_path = f"driver/expenses/{instance.trip.trip_id}_{filename}"
    return file_path


def get_operations_drivers(projects):
    from dms.models import Driver

    return (
        Driver.objects.filter(project__project_id__in=projects)
        .prefetch_related("driver_trips", "driver_locations")
        .annotate(
            working=Case(
                When(
                    driver_trips__status__in=[
                        TripStatus.SCHEDULED,
                        TripStatus.ACTIVE,
                        TripStatus.PAUSED,
                    ],
                    then=True,
                ),
                default=False,
            )
        )
        .exclude(is_active=False)
        .distinct()
    )


def generate_excel_report(report_data, report_name, headers):
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f'attachment; filename="{report_name}.xls"'
    wb = xlwt.Workbook(encoding="utf-8")
    ws = wb.add_sheet(report_name)

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = headers

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    try:
        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()

        for row in report_data:
            row_num += 1
            for col_num in range(len(row)):
                try:
                    ws.write(row_num, col_num, row[col_num], font_style)
                except Exception as e:
                    logger.exception(e)

        wb.save(response)
        return response

    except Exception as e:
        logger.exception(e)
    else:
        logger.info("Excel file sent. Removing file from server.")


# Retrieve files list from trip/temperature_log folder
def get_trip_temperature_files():
    from dms.models import TripTemperatureFile

    return list(
        TripTemperatureFile.objects.filter(processed=False).values_list(
            "file_name", "uploaded_filename", "added_by"
        )
    )


def get_sensor_metadata_readings(file_name):

    df = pd.read_excel(f"{settings.MEDIA_ROOT}{file_name}")
    data_found = False
    sensor_id = None
    found_at = None

    for i in range(len(df.index)):
        row_value = df.loc[i].values

        # Get Sensor ID
        if not sensor_id and row_value[0] == "Serial Number":
            sensor_id = row_value[1]

        # Get Temperature Reading location
        if all(row_value[:3] == ["No.", "Time", "Temperature°C"]):
            data_found = True
            found_at = i
            break

    sensor_readings = df.iloc[i + 1 :, :3].values

    sensor_temperature_data = list()
    for reading in sensor_readings:
        no, sensor_datetime, temperature = reading[0], reading[1], reading[2]
        if isinstance(sensor_datetime, float):
            sensor_datetime = xlrd.xldate_as_datetime(sensor_datetime, 0)
        elif isinstance(sensor_datetime, datetime):
            pass
        else:
            sensor_datetime = parser.parse(sensor_datetime)
        sensor_temperature_data.append(
            {
                "no": no,
                "sensor_datetime": sensor_datetime,
                "temperature": temperature,
            }
        )

    return {
        "data_found": data_found,
        "found_at": found_at,
        "sensor_id": sensor_id,
        "sensor_temperature_data": sensor_temperature_data,
    }


# Get Vehicle Info from sensor_id
def get_vehicle_trip_info(sensor_id, file_name):
    from dms.models import VehicleStorage, SensorReadingLog, TripTemperatureFile

    # Get Vehicle
    flag = True
    vs = None
    status = SensorReadingLogStatus.FAILED
    reason = ""
    try:
        # Vehicle / Storage Type
        vs = VehicleStorage.objects.filter(sensor_id=sensor_id).last()

        status = SensorReadingLogStatus.SUCCESSFUL
        flag = False

    except VehicleStorage.DoesNotExist as vsdne:
        reason = f"No Vehicle Found for sensor id {sensor_id}"
        logger.exception(vsdne)

    except AttributeError as ae:
        reason = f"No Vehicle found for sensor id {sensor_id}"
        logger.exception(ae)

    except VehicleStorage.MultipleObjectsReturned as vsmor:
        reason = f"Multiple Vehicles found for sensor id {sensor_id}"
        logger.exception(vsmor)

    except Exception as e:
        reason = f"Error Occured: {str(e)}"
        logger.exception(e)

    if flag:
        srl = SensorReadingLog.objects.create(
            file_name=file_name, status=status, reason=reason, sensor=vs
        )
        trip_temp_file_obj = TripTemperatureFile.objects.get(file_name=file_name)
        trip_temp_file_obj.processed = True
        trip_temp_file_obj.status = TripTemperatureFileStatus.FAILED
        trip_temp_file_obj.save()

    return vs, flag


# Add data in TripTemperatureLog
def add_trip_temp_log(kwargs):
    from dms.models import TripTemperatureLog, VehicleStorage, SensorReadingLog, TripTemperatureFile

    vs = kwargs.get("vs")
    sensor_temperature_data = kwargs.get("sensor_temperature_data")
    file_name = kwargs.get("file_name")

    status = SensorReadingLogStatus.FAILED
    try:
        trip_temp_list = list()

        trip_temp_file_obj = TripTemperatureFile.objects.get(file_name=file_name)
        trip_temp_file_obj.processed = True

        sensor_start_date = sensor_temperature_data[0].get("sensor_datetime").date()
        data = TripTemperatureLog.objects.filter(
            sensor=vs,
            timestamp__date=sensor_start_date,
        )
        if data:
            data.delete()

        for item in sensor_temperature_data:
            try:
                trip_temp_list.append(
                    TripTemperatureLog(
                        sensor=vs,
                        timestamp=item.get("sensor_datetime"),
                        temperature=item.get("temperature"),
                    )
                )
            except parser.ParserError as pe:
                logger.exception(pe)
        else:
            reason = "No Temperature data found"
            trip_temp_file_obj.status = TripTemperatureFileStatus.FAILED

        if trip_temp_list != list():
            ttl = TripTemperatureLog.objects.bulk_create(trip_temp_list)
            status = SensorReadingLogStatus.SUCCESSFUL
            reason = "Log Created Successfully"

            trip_temp_file_obj.status = TripTemperatureFileStatus.SUCCESSFUL
            delete_sensor_file(file_name)

    except Exception as e:
        reason = f"Error Occured: {e}"
        trip_temp_file_obj.status = TripTemperatureFileStatus.FAILED
    finally:
        trip_temp_file_obj.save()
        try:
            sensor_obj = VehicleStorage.objects.get(sensor_id=kwargs["sensor_id"])
        except Exception as e:
            logger.exception(e)
        srl = SensorReadingLog.objects.create(
            file_name=file_name, status=status, reason=reason, sensor=None
        )
    return status


# Delete file once its successfully processed.
def delete_sensor_file(file_name):
    try:
        os.remove(f"{settings.MEDIA_ROOT}{file_name}")
        return True
    except Exception as e:
        logger.exception(e)
    return False


def calculate_route(coordinates):
    client = OSRMClient()
    result = client.get_route(coordinates, driving_directions=False)
    return result


def generate_zone_feature_collections(zones):
    zone_section = {"type": "FeatureCollection", "features": []}
    for i in zones:
        zone_section["features"].append(
            {
                "type": "Feature",
                "properties": {
                    "id": i.id,
                    "zone_name": i.zone_name,
                },
                "geometry": json.loads(GEOSGeometry(i.geofence).geojson),
            }
        )
    return zone_section


def file_failed_notification(file_name, added_user):
    from dms.models import UserNotification, Notification
    from users.models import User

    notification = Notification.objects.create(
        title=f"Processing Failed",
        message=f"File Processing failed for {file_name}",
        priority=NotificationPriority.MEDIUM,
        notification_type=NotificationType.ERROR,
        notification_category=NotificationCategory.REPORT,
        expiration_time=timezone.now() + timedelta(days=1),
    )
    added_by = User.objects.get(id=added_user)
    UserNotification.objects.create(user=added_by, notification=notification)


def migrate_documents():
    from dms.models import VehicleDocument, Vehicle, DriverDocument, Driver

    driver_documents = list()
    vehicle_documents = list()
    delete_documents = list()
    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()

    for driver in drivers:
        license_image = driver.license_image if driver.license_image else None
        national_id_image = driver.national_id_image if driver.national_id_image else None
        visa_image = driver.visa_image if driver.visa_image else None

        if license_image:
            driver_documents.append(
                DriverDocument(
                    driver=driver,
                    document_type=DriverDocumentType.LICENSE_PHOTO,
                    document=license_image,
                )
            )
            delete_documents.append(license_image.url)
        if national_id_image:
            driver_documents.append(
                DriverDocument(
                    driver=driver,
                    document_type=DriverDocumentType.NATIONAL_ID_CARD,
                    document=national_id_image,
                )
            )
            delete_documents.append(national_id_image.url)
        if visa_image:
            driver_documents.append(
                DriverDocument(
                    driver=driver, document_type=DriverDocumentType.VISA, document=visa_image
                )
            )
            delete_documents.append(visa_image.url)

    for vehicle in vehicles:
        vehicle_image = vehicle.vehicle_image if vehicle.vehicle_image else None
        rc_image = vehicle.rc_image if vehicle.rc_image else None
        insurance_image = vehicle.insurance_image if vehicle.insurance_image else None

        if vehicle_image:
            vehicle_documents.append(
                VehicleDocument(
                    vehicle=vehicle,
                    document_type=VehicleDocumentType.VEHICLE_PHOTO,
                    document=vehicle_image,
                )
            )
            delete_documents.append(vehicle_image.url)

        if rc_image:
            vehicle_documents.append(
                VehicleDocument(
                    vehicle=vehicle,
                    document_type=VehicleDocumentType.VEHICLE_RC_PHOTO,
                    document=rc_image,
                )
            )
            delete_documents.append(rc_image.url)

        if insurance_image:
            vehicle_documents.append(
                VehicleDocument(
                    vehicle=vehicle,
                    document_type=VehicleDocumentType.INSURANCE_CERTIFICATE,
                    document=insurance_image,
                )
            )
            delete_documents.append(insurance_image.url)

    DriverDocument.objects.bulk_create(driver_documents)
    VehicleDocument.objects.bulk_create(vehicle_documents)
    if delete_documents:
        for file_name in delete_documents:
            try:
                if os.path.exists(f"{settings.BASE_DIR}{file_name}"):
                    os.remove(f"{settings.BASE_DIR}{file_name}")
            except Exception as e:
                logger.exception(e)


def has_overlap(a_start, a_end, b_start, b_end):
    latest_start = max(a_start, b_start)
    earliest_end = min(a_end, b_end)
    return latest_start <= earliest_end


def get_vehicle_partition(data: dict):

    vehicle_cbm_capacity = data.get("vehicle_cbm_capacity", Decimal("0.00"))

    if not int(vehicle_cbm_capacity):
        return {"frozen": Decimal("0.00"), "chilled": Decimal("0.00"), "dry": Decimal("0.00")}

    frozen_items_cbm = data.get("frozen_items_cbm", Decimal("0.00"))
    chilled_items_cbm = data.get("chilled_items_cbm", Decimal("0.00"))
    dry_items_cbm = data.get("dry_items_cbm", Decimal("0.00"))

    dry_items_percentage = Decimal("0.00")
    chilled_items_percentage = Decimal("0.00")
    frozen_items_percentage = Decimal("0.00")

    try:
        if frozen_items_cbm:
            frozen_items_percentage = (Decimal(frozen_items_cbm) * 100) / Decimal(
                vehicle_cbm_capacity
            )
        if chilled_items_cbm:
            chilled_items_percentage = (Decimal(chilled_items_cbm) * 100) / Decimal(
                vehicle_cbm_capacity
            )
        if dry_items_cbm:
            dry_items_percentage = (Decimal(dry_items_cbm) * 100) / Decimal(vehicle_cbm_capacity)
    except TypeError as te:
        logger.exception(te)

    total_percentage = dry_items_percentage + chilled_items_percentage + frozen_items_percentage

    if total_percentage > 100:
        total_cbm = frozen_items_cbm + chilled_items_cbm + dry_items_cbm
        unused_percentage = 0
        frozen_percentage = (frozen_items_cbm * 100) / total_cbm
        chilled_percentage = (chilled_items_cbm * 100) / total_cbm
        dry_percentage = (dry_items_cbm * 100) / total_cbm
        return {
            "dry": Decimal(dry_percentage),
            "chilled": Decimal(chilled_percentage),
            "frozen": Decimal(frozen_percentage),
            "used": round(total_percentage, 2),
            "unused": round(unused_percentage, 2),
        }

    unused_percentage = 100 - total_percentage

    remaining_percentage = unused_percentage / 3

    if frozen_items_percentage:
        frozen_items_percentage += remaining_percentage
        frozen_items_percentage = round_up_in_multiple(frozen_items_percentage)

    if chilled_items_percentage:
        chilled_items_percentage += remaining_percentage
        chilled_items_percentage = round_up_in_multiple(chilled_items_percentage)

    total_frozen_chilled_percentage = frozen_items_percentage + chilled_items_percentage

    dry_items_percentage = 100 - total_frozen_chilled_percentage

    return {
        "dry": Decimal(dry_items_percentage),
        "chilled": Decimal(chilled_items_percentage),
        "frozen": Decimal(frozen_items_percentage),
        "used": round(total_percentage, 2),
        "unused": round(unused_percentage, 2),
    }


def update_order_details(obj, status):
    if status == OrderConstants.OrderStatus.UNASSIGNED:
        obj.unassigned_on = timezone.now()
        obj.assigned_on = None
        obj.picked_up_on = None
        obj.completed_on = None
        obj.failed_on = None
        obj.cancelled_on = None
        obj.driver_remarks = None
        obj.trip = None
        obj.status_keyword = None
        obj.est_pickup_time = None
        obj.est_drop_time = None
        obj.attempt_number = 0
        obj.sequence_number = 0
        obj.processing_time = 0
        obj.is_pod_uploaded = False
        obj.cancellation_remarks = None
        obj.cod_remarks = None
    elif status == OrderConstants.OrderStatus.ASSIGNED:
        obj.assigned_on = timezone.now()
        obj.picked_up_on = None
        obj.completed_on = None
        obj.failed_on = None
        obj.cancelled_on = None
        obj.driver_remarks = None
        obj.status_keyword = None
        obj.est_pickup_time = None
        obj.est_drop_time = None
        obj.attempt_number = 0
        obj.processing_time = 0
        obj.is_pod_uploaded = False
        obj.cancellation_remarks = None
        obj.cod_remarks = None
    elif status == OrderConstants.OrderStatus.PICKED_UP:
        obj.picked_up_on = timezone.now()
        obj.failed_on = None
        obj.cancelled_on = None
        obj.driver_remarks = None
        obj.completed_on = None
        obj.status_keyword = None
        obj.attempt_number = 0
        obj.processing_time = 0
        obj.is_pod_uploaded = False
        obj.cancellation_remarks = None
        obj.cod_remarks = None
    elif status == OrderConstants.OrderStatus.SUCCESSFUL:
        obj.failed_on = None
        obj.cancelled_on = None
        obj.completed_on = timezone.now()
        obj.cancellation_remarks = None
    elif status == OrderConstants.OrderStatus.PARTIAL:
        obj.failed_on = None
        obj.cancelled_on = None
        obj.completed_on = timezone.now()
        obj.cancellation_remarks = None
    elif status == OrderConstants.OrderStatus.FAILED:
        obj.failed_on = timezone.now()
        obj.cancelled_on = None
        obj.cancellation_remarks = None
    elif status == OrderConstants.OrderStatus.CANCELLED:
        obj.assigned_on = None
        obj.picked_up_on = None
        obj.completed_on = None
        obj.failed_on = None
        obj.cancelled_on = timezone.now()
        obj.driver_remarks = None
        obj.cancellation_remarks = None
        obj.cod_remarks = None
        obj.driver_remarks = None
        obj.status_keyword = None
        obj.attempt_number = 0
        obj.processing_time = 0
        obj.is_pod_uploaded = False
        obj.driver_remarks = None
        obj.trip = None
        obj.status_keyword = None
        obj.est_pickup_time = None
        obj.est_drop_time = None
        obj.attempt_number = 0
        obj.sequence_number = 0
        obj.processing_time = 0

    return obj


def email_notification(data):
    """Email Sending Helper Function"""
    email_list = data.get("receiver_mail", "")
    customer_name = data.get("customer_name", "")
    reference_no = data.get("reference_no", "")
    delivery_date = data.get("delivery_date", "")
    link = data.get("link")

    subject = f"FleetFlow: Update on your order {reference_no}"
    message = (
        f"Your delivery from {customer_name} under order number {reference_no} will be "
        f"delivered on {delivery_date}. To avoid delays, kindly confirm your delivery location "
        "by clicking on the below link:"
    )
    context = {
        "customer_name": customer_name,
        "message": message,
        "reference_no": reference_no,
        "delivery_schedule": delivery_date,
        "order_url": link,
    }

    try:
        text = get_template("email.txt")
        html = get_template("email.html")

        text_content = text.render(context)
        html_content = html.render(context)
    except Exception as err:
        return f"Failure! error while rendering templates:{err}".format(err=err)

    try:
        send_mail(
            subject=subject,
            message=text_content,
            html_message=html_content,
            recipient_list=[email_list],
            from_email=settings.EMAIL_HOST_USER,
            fail_silently=False,
        )
    except SMTPAuthenticationError as smtpautherr:
        return f"The username and password provided is incorrect: {smtpautherr}".format(
            smtpautherr=smtpautherr
        )
    except SMTPConnectError as smtpconnerr:
        return f"There is an issue with SMTP server, please try after some time.: {smtpconnerr}".format(
            smtpconnerr=smtpconnerr
        )
    except Exception as err:
        return f"Failure! error while sending:{err}".format(err=err)
