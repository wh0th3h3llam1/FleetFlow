import os

from django.conf import settings
from django.contrib.gis import geos
from django.contrib.gis.geos import GEOSGeometry, fromstr
from django.utils import timezone
from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers

from common.constants import ProjectStatus, SystemRoles
from core.serializers import DynamicFieldsModelSerializer
from dms.models import Project, Zone, PlanningTemplate, ProjectUser, Tag


class PlanningTemplateSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = PlanningTemplate
        fields = [
            "id",
            "template_name",
            "loading_start_time",
            "loading_end_time",
            "offloading_start_time",
            "offloading_end_time",
            "offloading_time",
            "loading_time",
            "round_trip",
            "zone_constraint",
            "tag_validations",
            "configuration",
            "planning_time",
            "result_ttl",
            "traffic_jams",
            "toll_roads",
            "disable_compatibility",
            "fill_ratio",
            "created",
            "modified",
            "combine_processing_time",
            "performer_transport_restriction",
            "hardlink",
            "precedence",
            "storage_restriction",
            "disable_time_windows",
            "disable_performer_transport_shift",
            "warehouse_gate_count",
            "measurement_constraint",
        ]
        read_only_fields = [
            "created",
            "modified",
            "combine_processing_time",
            "performer_transport_restriction",
            "hardlink",
            "precedence",
            "storage_restriction",
            "disable_performer_transport_shift",
            "warehouse_gate_count",
            "measurement_constraint",
            "planning_time",
        ]


class ProjectSerializer(DynamicFieldsModelSerializer):
    base_coordinates = PointField()
    planning_template = serializers.CharField(max_length=255)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_name",
            "planning_template",
            "project_id",
            "base_address",
            "status",
            "order_creation_notification",
            "order_picked_up_notification",
            "order_completed_notification",
            "order_failed_notification",
            "update_customer_location",
            "base_coordinates",
            "planning_template",
            "serviceable_area",
        ]
        read_only_fields = ["created", "modified"]

    def validate_planning_template(self, val):
        try:
            planning_template = PlanningTemplate.objects.get(template_name=val)

        except Exception as e:
            raise serializers.ValidationError(f"No Template found with {val}")
        return planning_template

    def get_default_serviceable_area(self):
        uae_path = os.path.join(settings.BASE_DIR, "dms/fixtures/uae.json")
        if os.path.exists(uae_path):
            area = GEOSGeometry(open(uae_path).read())
            return area

    def validate_serviceable_area(self, area):
        if not area:
            return self.get_default_serviceable_area()
        else:
            if isinstance(area, geos.Polygon):
                area = geos.MultiPolygon(fromstr(str(area)))
        return area

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get("added_by") and instance.added_by:
            representation["added_by"] = instance.added_by.full_name
        if representation.get("updated_by") and instance.updated_by:
            representation["updated_by"] = instance.updated_by.full_name
        representation["planning_template"] = (
            instance.planning_template.template_name if instance.planning_template else ""
        )
        return representation

    def create(self, validated_data):
        user = self.context.get("request").user
        validated_data["added_by"] = user
        if not validated_data.get("serviceable_area"):
            validated_data["serviceable_area"] = self.get_default_serviceable_area()
        project = super().create(validated_data)
        ProjectUser.objects.get_or_create(user=user, project=project, assigned_by=user)
        SYS_ADMINS = User.objects.filter(role__role_name=SystemRoles.SYS_ADMIN)
        for admin in SYS_ADMINS:
            ProjectUser.objects.get_or_create(user=admin, project=project, assigned_by=admin)

        return project

    def update(self, instance, validated_data):
        if (
            validated_data.get("status")
            and validated_data["status"] == ProjectStatus.DEACTIVATED
            and instance.status != ProjectStatus.DEACTIVATED
        ):
            validated_data["deactivated_by"] = self.context.get("request").user
            validated_data["deactivated_on"] = timezone.now()
        else:
            validated_data["deactivated_by"] = None
            validated_data["deactivated_on"] = None
        validated_data["updated_by"] = self.context.get("request").user
        return super().update(instance, validated_data)


class ZoneSerializer(DynamicFieldsModelSerializer):
    project = serializers.CharField(max_length=255)
    remaining_zones = serializers.SerializerMethodField()

    def get_remaining_zones(self, zone):
        remaining_zones = (
            self.context.get("all_zones").filter(project=zone.project).exclude(id=zone.id)
        )
        zone_section = generate_zone_feature_collections(remaining_zones)
        return {"zones": zone_section}

    def validate_project(self, val):
        try:
            project = self.context.get("all_projects").get(project_id=val)
        except Exception as e:
            raise serializers.ValidationError(f"No project found with project id {val}")
        return project

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["project"] = instance.project.project_id
        return representation

    class Meta:
        model = Zone
        geo_field = "geofence"
        fields = ("zone_name", "geofence", "project", "zone_desc", "id", "remaining_zones")


class StatusKeywordSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.added_by:
            representation["added_by"] = instance.added_by.full_name
        return representation

    class Meta:
        model = StatusKeyword
        fields = ("id", "status_category", "name", "keyword", "description", "added_by")
        read_only_fields = ("id", "added_by")

    def create(self, validated_data):
        user = self.context.get("request").user
        validated_data["added_by"] = user
        return super().create(validated_data=validated_data)


class UserNotificationSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="notification.title")
    message = serializers.CharField(source="notification.message")
    priority = serializers.CharField(source="notification.priority")
    notification_category = serializers.CharField(source="notification.notification_category")
    notification_type = serializers.CharField(source="notification.notification_type")

    class Meta:
        model = UserNotification
        fields = (
            "id",
            "title",
            "is_read",
            "read_on",
            "priority",
            "notification_category",
            "notification_type",
            "message",
            "created",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "tag", "description", "tag_type")
