import logging

from django.db.utils import IntegrityError
from django.utils import timezone
from rest_framework import serializers

from common.constants import TagType, VehicleStatus, OrderConstants, VehicleFuelType, TripStatus
from core.serializers import DynamicFieldsModelSerializer
from dms.models import Vehicle, VehicleStorage, VehicleDocument, Tag
from dms.serializers import ProjectSerializer

logger = logging.getLogger(__name__)


class VehicleStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleStorage
        fields = ("storage_type",)


class VehicleDocumentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = VehicleDocument
        fields = ("id", "vehicle", "document_type", "document", "description", "added_by")


class VehicleSerializer(DynamicFieldsModelSerializer):
    vehicle_plate_no = serializers.CharField(max_length=20, required=True)
    available_storages = serializers.CharField(write_only=True, required=True)
    project = serializers.CharField(max_length=255)
    tonnage_capacity = serializers.CharField()
    cbm_capacity = serializers.CharField()
    fuel_type = serializers.CharField()
    storages = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    sensors = serializers.SerializerMethodField(read_only=True)
    sensor_info = serializers.CharField(write_only=True, required=False)
    vehicle_documents = VehicleDocumentSerializer(many=True, read_only=True)
    tags = serializers.CharField(write_only=True, required=False)
    assigned_tags = serializers.SerializerMethodField()

    def get_assigned_tags(self, instance):
        return [
            {"tag": vehicle_tag.tag.tag, "id": vehicle_tag.tag.id}
            for vehicle_tag in instance.vehicle_tags.all()
        ]

    def get_projects(self, instance):
        projects = ProjectSerializer(
            self.context.get("all_projects"),
            many=True,
            fields=("project_name", "project_id"),
            read_only=True,
        )

        return projects.data

    def validate_project(self, val):
        try:
            project = self.context.get("all_projects").get(project_id=val)
        except Exception as e:
            raise serializers.ValidationError(f"No project found with project id {val}") from e
        return project

    def validate_status(self, status):
        if status in [VehicleStatus.IDLE, VehicleStatus.DEACTIVATED]:
            return status
        raise serializers.ValidationError("You do not have permission to perform this action.")

    def validate_fuel_type(self, fuel_type):
        fuel_type_mapping = {
            "diesel": VehicleFuelType.DIESEL,
            "petrol": VehicleFuelType.PETROL,
            "other": VehicleFuelType.OTHER,
        }

        if fuel_type_mapping.get(fuel_type.lower().strip()):
            return fuel_type

        raise serializers.ValidationError("Invalid fuel type. Choices are Petrol,Diesel,Others")

    def validate_tonnage_capacity(self, tonnage_capacity):
        tonnage_capacity = float(tonnage_capacity)
        if tonnage_capacity <= 0.00 or tonnage_capacity > 99.99:
            raise serializers.ValidationError("Tonnage Capacity must be between 0.00 and 99.99 ")
        return round(tonnage_capacity, 2)

    def validate_cbm_capacity(self, cbm_capacity):
        cbm_capacity = float(cbm_capacity)
        if cbm_capacity <= 0.00 or cbm_capacity > 99.99:
            raise serializers.ValidationError("CBM Capacity must be between 0.00 and 99.99 ")
        return round(cbm_capacity, 2)

    def validate_available_storages(self, storages):
        storage_mapping = {
            "frozen": OrderConstants.StorageTypes.FROZEN,
            "chilled": OrderConstants.StorageTypes.CHILLED,
            "dry": OrderConstants.StorageTypes.DRY,
        }
        val = None
        try:
            val = [
                storage_mapping[storage.lower().strip()]
                for storage in storages.split(",")
                if storage.strip() != ""
            ]
        except KeyError as e:
            raise serializers.ValidationError(
                "Invalid storage types. Valid storage types are Frozen, Dry, Chilled."
            ) from e

        return val

    def validate_tags(self, tags):
        if not tags:
            self.vehicle_tags.all().delete()
            return ""

        vehicle_tags = [tag.strip() for tag in tags.split(",")]
        _ = [
            Tag.objects.get_or_create(tag=tag, tag_type=TagType.VEHICLE_TAG) for tag in vehicle_tags
        ]

        return ",".join(vehicle_tags)

    def validate(self, attrs):
        existing_vehicles = self.context.get("existing_vehicles")
        if existing_vehicles:
            vehicle_plate_no = attrs.get("vehicle_plate_no")
            if vehicle_plate_no in existing_vehicles:
                attrs["exists"] = True
            else:
                attrs["exists"] = False

        # vehicle project update validation.
        try:
            vehicle = Vehicle.objects.prefetch_related("vehicle_drivers").get(
                vehicle_plate_no=attrs.get("vehicle_plate_no")
            )
        except Vehicle.DoesNotExist:
            if not self.instance:
                return attrs
            vehicle = self.instance

        new_project = attrs.get("project")
        driver = vehicle.vehicle_drivers.last()
        if new_project != vehicle.project:
            trips = vehicle.vehicle_trips.all()

            for trip in trips:
                if trip.status in [TripStatus.ACTIVE, TripStatus.PAUSED]:
                    raise serializers.ValidationError(
                        f"Vehicle {vehicle.vehicle_plate_no} is assigned to an active trip."
                    )
                elif trip.status == TripStatus.SCHEDULED:
                    raise serializers.ValidationError(
                        f"Trip {trip.reference_number} is scheduled for Vehicle {vehicle.vehicle_plate_no}."
                    )

            if driver and driver.project != new_project:
                driver.vehicle_assigned = None
                driver.save()
        return attrs

    def validate_sensor_info(self, sensor_info):

        sensor_id_list = list()

        for sensor in sensor_info.split(","):
            sensor = sensor.strip()
            if sensor == "":
                sensor_id_list.append(None)
            else:
                sensor_id_list.append(sensor)
        return sensor_id_list

    def get_sensors(self, instance: Vehicle):
        sensor_id_list = VehicleStorage.objects.filter(vehicle=instance).values_list(
            "storage_type", "sensor_id"
        )

        sensor_mapping = {
            "Chilled": None,
            "Dry": None,
            "Frozen": None,
        }
        for sensor in sensor_id_list:
            try:
                if sensor[0] == OrderConstants.StorageTypes.CHILLED:
                    sensor_mapping["Chilled"] = sensor[1]

                elif sensor[0] == OrderConstants.StorageTypes.DRY:
                    sensor_mapping["Dry"] = sensor[1]

                elif sensor[0] == OrderConstants.StorageTypes.FROZEN:
                    sensor_mapping["Frozen"] = sensor[1]

            except IndexError as ie:
                logger.exception(ie)

        return sensor_mapping

    def get_storages(self, instance: Vehicle):
        return [storage.get_storage_type_display() for storage in instance.vehicle_storages.all()]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.project and representation.get("project"):
            representation["project"] = instance.project.project_id
            representation["project_name"] = instance.project.project_name
        if instance.added_by and representation.get("added_by"):
            representation["added_by"] = instance.added_by.full_name
        if instance.updated_by and representation.get("updated_by"):
            representation["updated_by"] = instance.updated_by.full_name
        return representation

    class Meta:
        model = Vehicle
        fields = (
            "vehicle_plate_no",
            "vehicle_image",
            "tonnage_capacity",
            "vehicle_make",
            "vehicle_model",
            "vehicle_year",
            "vehicle_cost",
            "mileage",
            "cbm_capacity",
            "fuel_type",
            "rc_number",
            "rc_expiry_date",
            "rc_image",
            "insurance_policy_number",
            "insurance_expiry_date",
            "insurance_type",
            "insurance_image",
            "permits",
            "added_by",
            "vehicle_documents",
            "status",
            "project",
            "deactivated_by",
            "deactivated_on",
            "projects",
            "storages",
            "id",
            "updated_by",
            "available_storages",
            "sensor_info",
            "sensors",
            "box_capacity",
            "tags",
            "assigned_tags",
        )
        read_only_fields = ["created", "modified", "id", "vehicle_documents"]

    def create(self, validated_data):
        exists = validated_data.pop("exists", None)
        if not exists:
            available_storages = validated_data.pop("available_storages", None)
            tags = validated_data.pop("tags", [])
            sensor_info = validated_data.pop("sensor_info", None)
            # tags = self.context.get("request").data.get('tags')
            validated_data["added_by"] = self.context.get("request").user
            vehicle = super(VehicleSerializer, self).create(validated_data)
            try:
                vehicle.add_vehicle_storage(available_storages, sensor_info)
            except IntegrityError as ie:
                logger.exception(ie)
                raise serializers.ValidationError(["Sensor ID Already exists"])

            if tags:
                tags = tags.split(",")
                vehicle.add_tags(tags)
            return vehicle
        else:
            vehicle = Vehicle.objects.get(vehicle_plate_no=validated_data.get("vehicle_plate_no"))
            return self.update(vehicle, validated_data)

    def update(self, instance, validated_data):
        try:
            available_storages = validated_data.pop("available_storages", None)
            sensor_info = validated_data.pop("sensor_info", None)
            if available_storages:
                instance.vehicle_storages.all().delete()
                instance.add_vehicle_storage(available_storages, sensor_info)
        except IntegrityError as ie:
            logger.exception(ie)
            raise serializers.ValidationError(["Sensor ID Already exists"])
        if (
            validated_data.get("status")
            and validated_data["status"] == VehicleStatus.DEACTIVATED
            and instance.status != VehicleStatus.DEACTIVATED
        ):
            validated_data["deactivated_by"] = self.context.get("request").user
            validated_data["deactivated_on"] = timezone.now()
        else:
            validated_data["deactivated_by"] = None
            validated_data["deactivated_on"] = None
        validated_data["updated_by"] = self.context.get("request").user
        tags = validated_data.pop("tags", [])
        vehicle = super(VehicleSerializer, self).update(instance, validated_data)
        if tags:
            tags = tags.split(",")
        vehicle.add_tags(tags)
        return vehicle
