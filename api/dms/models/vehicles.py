from common.helpers import no_past_date
from django.core.validators import FileExtensionValidator
from django.db import models

from common.constants import VehicleFuelType, VehicleStatus, FieldConstants
from common.choices import (
    VEHICLE_FUEL_TYPES,
    VEHICLE_STATUS_CHOICES,
    STORAGE_TYPE_CHOICES,
    VEHICLE_DOCUMENT_TYPE_CHOICES,
)
from core.models import BaseModel
from dms.helpers import get_vehicle_image_path, get_vehicle_documents_path
from dms.models import Project
from users.models import User


class Vehicle(BaseModel):
    VEHICLE_PREFIX = "VEHICLE"

    IMAGE_FORMATS = ["pdf", "png", "jpg", "jpeg"]

    vehicle_plate_no = models.CharField(
        verbose_name="License Plate Number", max_length=20, unique=True
    )
    vehicle_image = models.FileField(
        upload_to=get_vehicle_image_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=IMAGE_FORMATS)],
        help_text="Supported Formats : {}".format(IMAGE_FORMATS),
    )
    tonnage_capacity = models.DecimalField(
        verbose_name="Tonnage Capacity", decimal_places=2, max_digits=4
    )
    cbm_capacity = models.DecimalField(verbose_name="CBM Capacity", decimal_places=2, max_digits=4)
    box_capacity = models.PositiveSmallIntegerField(
        verbose_name="Boxes Capacity", blank=True, null=True
    )

    fuel_type = models.CharField(
        choices=VEHICLE_FUEL_TYPES,
        verbose_name="Fuel Type",
        max_length=20,
        default=VehicleFuelType.DIESEL,
    )
    rc_number = models.CharField(max_length=50, verbose_name="RC Number")
    rc_expiry_date = models.DateField(validators=[no_past_date])
    rc_image = models.FileField(
        upload_to=get_vehicle_image_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=IMAGE_FORMATS)],
        help_text="Supported Formats : {}".format(IMAGE_FORMATS),
    )

    insurance_policy_number = models.CharField(
        verbose_name="Insurance Policy Number", default="", max_length=50
    )
    insurance_expiry_date = models.DateField(
        validators=[
            no_past_date,
        ],
        blank=True,
        null=True,
    )
    insurance_type = models.CharField(
        verbose_name="Insurance Type", blank=True, null=True, max_length=30
    )
    insurance_image = models.FileField(
        upload_to=get_vehicle_image_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=IMAGE_FORMATS)],
        help_text="Supported Formats : {}".format(IMAGE_FORMATS),
    )

    permits = models.CharField(max_length=100, verbose_name="Permits", null=True)
    vehicle_make = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Vehicle Make"
    )
    vehicle_model = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Vehicle Model"
    )
    vehicle_year = models.PositiveSmallIntegerField(
        verbose_name="Vehicle Make Year", blank=True, null=True
    )
    vehicle_cost = models.IntegerField(verbose_name="Vehicle Cost", blank=True, null=True)
    mileage = models.IntegerField(verbose_name="Vehicle Mileage", blank=True, null=True)

    added_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name="added_vehicles",
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        to=User,
        on_delete=models.SET_NULL,
        related_name="updated_vehicles",
        blank=True,
        null=True,
    )
    status = models.CharField(
        choices=VEHICLE_STATUS_CHOICES,
        default=VehicleStatus.IDLE,
        max_length=20,
    )

    project = models.ForeignKey(
        to=Project,
        on_delete=models.SET_NULL,
        related_name="project_vehicles",
        blank=True,
        null=True,
    )

    deactivated_by = models.ForeignKey(
        to=User,
        related_name="deactivated_vehicles",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    deactivated_on = models.DateTimeField(blank=True, null=True, verbose_name="Deactivated On")

    def __str__(self) -> str:
        return f"{self.vehicle_plate_no}"

    @property
    def vehicle_id(self) -> str:
        return f"{self.VEHICLE_PREFIX}{str(self.id).zfill(2)}"

    @property
    def rc_expiry(self):
        return (
            self.rc_expiry_date.strftime(FieldConstants.DATE_FORMAT) if self.rc_expiry_date else ""
        )

    @property
    def insurance_expiry(self):
        return (
            self.insurance_expiry_date.strftime(FieldConstants.DATE_FORMAT)
            if self.insurance_expiry_date
            else ""
        )

    def add_vehicle_storage(self, available_storages):
        for storage in available_storages:
            VehicleStorage.objects.get_or_create(vehicle=self, storage_type=storage)


class VehicleDocument(BaseModel):
    FILE_FORMATS = ["pdf", "png", "jpg", "jpeg"]

    vehicle = models.ForeignKey(
        Vehicle, related_name="vehicle_documents", on_delete=models.CASCADE, verbose_name="Vehicle"
    )
    document_type = models.CharField(
        choices=VEHICLE_DOCUMENT_TYPE_CHOICES,
        verbose_name="Document Type",
        blank=True,
        null=True,
        max_length=30,
    )
    document = models.FileField(
        upload_to=get_vehicle_documents_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=FILE_FORMATS)],
        help_text="Supported Formats : {}".format(FILE_FORMATS),
    )
    description = models.TextField(blank=True, null=True)
    added_by = models.ForeignKey(
        to=User,
        related_name="vehicle_doc_added_by",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = "Vehicle Documents"

    def __str__(self):
        return f"{self.document_type} - {self.vehicle}"


class VehicleStorage(BaseModel):
    vehicle = models.ForeignKey(Vehicle, related_name="vehicle_storages", on_delete=models.CASCADE)
    storage_type = models.CharField(choices=STORAGE_TYPE_CHOICES, max_length=20)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("vehicle", "storage_type"), name="vehicle_storage_type_unique"
            )
        ]

    def __str__(self) -> str:
        return f"{self.vehicle} - {self.storage_type} - {self.sensor_id}"
