import logging

from django.utils import timezone
from rest_framework import serializers

from common.constants import FieldConstants, ServiceType, VehicleStatus
from core.serializers import DynamicFieldsModelSerializer
from dms.models import Driver, DriverDocument
from dms.serializers import ZoneSerializer

logger = logging.getLogger(__name__)


class DriverDocumentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = DriverDocument
        fields = ("id", "driver", "document_type", "document", "description", "added_by")

    def create(self, validated_data):
        driver_document = super(DriverDocumentSerializer, self).create(validated_data)
        return driver_document


class DriverSerializer(DynamicFieldsModelSerializer):
    zone_assigned = ZoneSerializer(read_only=True, exclude=("zone_desc",))
    username = serializers.CharField(max_length=150, source="user.username")
    contact_number = serializers.CharField(
        max_length=FieldConstants.PHONE_NUMBER_LENGTH, source="user.contact_number"
    )
    profile_image = serializers.FileField(source="user.profile_image", read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    vehicle_assigned = serializers.CharField(required=False)
    zone = serializers.CharField(required=False)
    projects = serializers.SerializerMethodField()
    vehicles = serializers.SerializerMethodField()
    zones = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()
    project = serializers.CharField(max_length=255)
    service_type = serializers.CharField(required=False)

    driver_documents = DriverDocumentSerializer(many=True, read_only=True)

    tags = serializers.CharField(write_only=True, required=False)
    assigned_tags = serializers.SerializerMethodField()

    def get_assigned_tags(self, instance):
        return [
            {"tag": driver_tag.tag.tag, "id": driver_tag.tag.id}
            for driver_tag in instance.driver_tags.all()
        ]

    def get_vehicle_info(self, instance: Driver):
        from dms.serializers import VehicleSerializer

        return VehicleSerializer(
            instance.vehicle_assigned,
            fields=(
                "vehicle_plate_no",
                "vehicle_make",
                "vehicle_model",
                "cbm_capacity",
                "tonnage_capacity",
                "storages",
            ),
        ).data

    def get_vehicles(self, obj):
        from dms.serializers import VehicleSerializer

        vehicles = self.context.get("all_vehicles").filter(project=obj.project)
        return VehicleSerializer(vehicles, fields=("id", "vehicle_plate_no"), many=True).data

    def get_zones(self, obj):
        zones = self.context.get("all_zones").filter(project=obj.project)
        return ZoneSerializer(zones, fields=("id", "zone_name", "project"), many=True).data

    def get_projects(self, obj: Driver):
        from dms.serializers import ProjectSerializer

        projects = ProjectSerializer(
            self.context.get("all_projects"),
            many=True,
            fields=("project_name", "project_id"),
            read_only=True,
        )
        return projects.data

    class Meta:
        model = Driver
        fields = (
            "id",
            "license_number",
            "license_expiry",
            "license_image",
            "salary",
            "health_card_number",
            "health_card_expiry",
            "nationality",
            "national_id_expiry",
            "national_id_image",
            "visa_number",
            "visa_expiry",
            "visa_image",
            "shift_start",
            "shift_end",
            "vehicle_assigned",
            "project",
            "projects",
            "service_type",
            "status",
            "zone_assigned",
            "zone",
            "zones",
            "vehicles",
            "profile_image",
            "username",
            "contact_number",
            "first_name",
            "last_name",
            "is_active",
            "driver_documents",
            "vehicle_info",
            "tags",
            "assigned_tags",
        )
        read_only_fields = ["created", "modified", "id", "status", "driver_documents"]

    def validate_project(self, val):
        try:
            project = self.context.get("all_projects").get(project_id=val)
        except Exception as e:
            raise serializers.ValidationError(f"No project found with project id {val}")
        return project

    def validate_vehicle_assigned(self, vehicle):
        if vehicle:
            try:
                vehicle = self.context.get("all_vehicles").get(vehicle_plate_no=vehicle)
            except Exception as e:
                raise serializers.ValidationError(f"Vehicle {vehicle} not found")
        if vehicle.status == VehicleStatus.DEACTIVATED:
            raise serializers.ValidationError(f"Cannot Assign Deactivated Vehicle {vehicle}")
        return vehicle

    def validate_zone(self, zone):
        if zone:
            try:
                zone = self.context.get("all_zones").get(zone_name=zone)
            except Exception as e:
                raise serializers.ValidationError(f"Zone {zone} not found")
        return zone

    def validate_service_type(self, service_type):
        service_type_mapping = {
            "b2b": ServiceType.B2B,
            "b2c": ServiceType.B2C,
        }
        service = None
        try:
            service = service_type_mapping[service_type.lower()]
        except KeyError as e:
            raise serializers.ValidationError(
                "Invalid Service Type. Valid service types are B2B/B2C."
            )
        else:
            return service

    def validate(self, attrs):
        zone = attrs.get("zone", None)
        vehicle_assigned = attrs.get("vehicle_assigned", None)

        if self.instance:
            if self.instance.project != attrs.get("project"):
                if not zone:
                    attrs["zone"] = None
                if not vehicle_assigned:
                    attrs["vehicle_assigned"] = None
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.project:
            representation["project"] = instance.project.project_id
        if instance.vehicle_assigned:
            representation["vehicle"] = instance.vehicle_assigned.vehicle_plate_no
        if instance.added_by:
            representation["added_by"] = instance.added_by.full_name
        if instance.updated_by:
            representation["updated_by"] = instance.updated_by.full_name
        return representation

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        validated_data["added_by"] = self.context.get("request").user
        driver = super(DriverSerializer, self).create(validated_data)
        if tags:
            tags = tags.split(",")
            driver.add_tags(tags)

        return driver

    def update(self, instance: Driver, validated_data: dict):
        tags = validated_data.pop("tags", [])
        if not validated_data.get("is_active"):
            validated_data["deactivated_by"] = self.context.get("request").user
            validated_data["deactivated_on"] = timezone.now()
        else:
            validated_data["deactivated_by"] = None
            validated_data["deactivated_on"] = None

        validated_data["updated_by"] = self.context.get("request").user
        driver = super().update(instance, validated_data)

        if tags:
            tags = tags.split(",")
        driver.add_tags(tags)
        return driver
