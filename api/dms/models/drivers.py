from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from common.choices import (
    DRIVER_DOCUMENT_TYPE_CHOICES,
    SERVICE_TYPE_CHOICES,
    DRIVER_STATUS_CHOICES,
)
from common.constants import DriverStatus, ServiceType, FieldConstants
from common.helpers import no_past_date
from core.models import BaseModel
from dms.managers import DriverManager
from dms.models import Project, Zone, StatusKeyword, Tag
from users.models import User


class Driver(BaseModel):

    DRIVER_PREFIX = "DRIVER"

    IMAGE_FORMATS = ["pdf", "png", "jpg", "jpeg"]

    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name="driver",
    )
    license_number = models.CharField(max_length=20, verbose_name="License Number")
    license_expiry = models.DateField(verbose_name="License Expiry Date")
    license_image = models.FileField(
        upload_to=get_driver_license_image_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=IMAGE_FORMATS)],
        help_text=f"Supported Formats : {IMAGE_FORMATS}",
    )
    nationality = models.CharField(max_length=25, verbose_name="Nationality", blank=True, null=True)
    national_id_expiry = models.DateField(max_length=25, verbose_name="National ID Expiry date")
    national_id_image = models.FileField(
        upload_to=get_driver_national_id_image_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=IMAGE_FORMATS)],
        help_text=f"Supported Formats : {IMAGE_FORMATS}",
    )

    visa_number = models.CharField(max_length=25, verbose_name="Visa Number", blank=True, null=True)
    visa_expiry = models.DateField(
        max_length=25, verbose_name="visa Expiry date", blank=True, null=True
    )
    visa_image = models.FileField(
        upload_to=get_driver_visa_image_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=IMAGE_FORMATS)],
        help_text=f"Supported Formats : {IMAGE_FORMATS}",
    )

    shift_start = models.TimeField(verbose_name="Shift Start Time", default="07:00")
    shift_end = models.TimeField(verbose_name="Shift End Time", default="18:00")
    added_by = models.ForeignKey(
        to=User, related_name="drivers_added", on_delete=models.SET_NULL, blank=True, null=True
    )
    updated_by = models.ForeignKey(
        to=User,
        related_name="updated_drivers",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    status = models.CharField(
        choices=DRIVER_STATUS_CHOICES,
        default=DriverStatus.OFF_DUTY,
        verbose_name="Status",
        max_length=32,
    )
    last_seen_on = models.DateTimeField(verbose_name="Last Message", blank=True, null=True)

    vehicle_assigned = models.ForeignKey(
        to=Vehicle,
        related_name="vehicle_drivers",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    project = models.ForeignKey(
        to=Project,
        related_name="project_drivers",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    service_type = models.CharField(
        choices=SERVICE_TYPE_CHOICES,
        verbose_name="Service Type",
        default=ServiceType.B2B,
        max_length=5,
    )
    salary = models.IntegerField(blank=True, null=True)
    health_card_number = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Health Card Number"
    )
    health_card_expiry = models.DateField(
        validators=[
            no_past_date,
        ],
        verbose_name="Health Card Expiry Date",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    deactivated_by = models.ForeignKey(
        to=User,
        related_name="deactivated_drivers",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    deactivated_on = models.DateTimeField(blank=True, null=True, verbose_name="Deactivated On")

    zone = models.ForeignKey(
        Zone, on_delete=models.SET_NULL, blank=True, null=True, related_name="zone_drivers"
    )

    objects = models.Manager()
    active_manager = DriverManager()

    def deactivate(self, by: User):
        self.status = DriverStatus.DEACTIVATED
        self.deactivated_on = timezone.now()
        self.deactivated_by = by
        self.save()

    @property
    def shift_start_time(self):
        return self.shift_start.strftime(FieldConstants.TIME_FORMAT) if self.shift_start else ""

    @property
    def shift_end_time(self):
        return self.shift_end.strftime(FieldConstants.TIME_FORMAT) if self.shift_end else ""

    @property
    def national_id_expiry_date(self):
        return (
            self.national_id_expiry.strftime(FieldConstants.DATE_FORMAT)
            if self.national_id_expiry
            else ""
        )

    @property
    def visa_expiry_date(self):
        return self.visa_expiry.strftime(FieldConstants.DATE_FORMAT) if self.visa_expiry else ""

    @property
    def health_card_expiry_date(self):
        return (
            self.health_card_expiry.strftime(FieldConstants.DATE_FORMAT)
            if self.health_card_expiry
            else ""
        )

    @property
    def license_expiry_date(self):
        return (
            self.license_expiry.strftime(FieldConstants.DATE_FORMAT) if self.license_expiry else ""
        )

    @property
    def zone_name(self):
        return self.zone.zone_name if self.zone else ""

    @property
    def vehicle(self):
        return self.vehicle_assigned.vehicle_plate_no if self.vehicle_assigned else None

    @property
    def current_trip(self):
        driver_trip = self.driver_trips.filter(
            status__in=[TripStatus.ACTIVE, TripStatus.PAUSED], trip_end__isnull=True, driver=self
        ).last()
        if driver_trip:
            return driver_trip
        else:
            raise AttributeError

    @property
    def future_trips(self):
        return self.driver_trips.filter(status=TripStatus.SCHEDULED).order_by("trip_date")

    @property
    def last_driver_trip(self):
        return (
            self.driver_trips.filter(status=TripStatus.COMPLETED)
            .exclude(trip_end=None)
            .order_by("-trip_date")
            .first()
        )

    @property
    def upcoming_trip(self):
        if self.last_driver_trip:
            driver_trip = self.future_trips.filter(id=self.last_driver_trip.id).last()
            if driver_trip:
                return driver_trip
        return self.future_trips.first()

    def add_attendance_log(self, status):
        attandance_obj = DriverAttendanceLog.objects.filter(
            driver=self, duty_start__date=timezone.now().date()
        )
        if status == DriverStatus.ON_DUTY and not attandance_obj:
            attandance_obj = DriverAttendanceLog.objects.create(
                driver=self, duty_start=timezone.now()
            )
        elif status == DriverStatus.OFF_DUTY and attandance_obj:
            attandance_obj = attandance_obj.latest("duty_start")
            attandance_obj.duty_end = timezone.now()
            attandance_obj.save()
        else:
            attandance_obj = False
        return attandance_obj

    def __str__(self):
        return f'{self.user.full_name} - {self.project.project_name if self.project else ""}'


class DriverAttendanceLog(BaseModel):
    driver = models.ForeignKey(
        Driver, related_name="attendance_logs", on_delete=models.CASCADE, verbose_name="Driver"
    )
    duty_start = models.DateTimeField(verbose_name="Duty start")
    duty_end = models.DateTimeField(verbose_name="Duty end", blank=True, null=True)


class DriverStatusLog(BaseModel):

    driver = models.ForeignKey(
        Driver, related_name="status_logs", verbose_name="Status Logs", on_delete=models.CASCADE
    )
    status_keyword = models.ForeignKey(
        StatusKeyword,
        related_name="status_drivers",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Status Keyword",
    )
    message = models.CharField(max_length=255, verbose_name="Message")

    def __str__(self):
        return f"{self.message} - {self.created.strftime(FieldConstants.DATE_TIME_FORMAT)}"


class DriverDocument(BaseModel):
    FILE_FORMATS = ["pdf", "png", "jpg", "jpeg"]

    driver = models.ForeignKey(
        Driver, related_name="driver_documents", on_delete=models.CASCADE, verbose_name="Driver"
    )
    document_type = models.CharField(
        choices=DRIVER_DOCUMENT_TYPE_CHOICES,
        verbose_name="Document Type",
        blank=True,
        null=True,
        max_length=30,
    )
    description = models.TextField(blank=True, null=True)
    document = models.FileField(
        upload_to=get_driver_documents_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=FILE_FORMATS)],
        help_text="Supported Formats : {}".format(FILE_FORMATS),
    )
    added_by = models.ForeignKey(
        to=User,
        related_name="driver_doc_added_by",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Driver Documents"

    def __str__(self):
        return f"{self.document_type} - {self.driver.user.full_name}"


class DriverTag(BaseModel):  # through table
    driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, related_name="driver_tags", verbose_name="Driver"
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="tags_driver", verbose_name="Tags"
    )

    def __str__(self):
        return f"{self.driver.__str__()} - {self.tag.__str__()}"
