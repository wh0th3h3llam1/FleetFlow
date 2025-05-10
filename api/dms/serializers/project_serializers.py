import json
import os
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, fromstr, MultiPolygon, Polygon
from django.utils import timezone

from rest_framework import serializers

from drf_extra_fields.geo_fields import PointField

from common.constants import ProjectStatus, SystemRoles
from common.mixins import SerializerCreateUpdateOnlyMixin
from core.serializers import DynamicFieldsModelSerializer
from dms.utils import generate_zone_feature_collections
from dms.models import Project, ProjectUser, StatusKeyword, Zone
from users.models import User


class ProjectSerializer(SerializerCreateUpdateOnlyMixin, DynamicFieldsModelSerializer):
    base_coordinates = PointField()

    added_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    updated_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Project
        fields = [
            "id",
            "project_name",
            "project_id",
            "base_address",
            "status",
            "base_coordinates",
            "serviceable_area",
            "added_by",
            "updated_by",
        ]
        read_only_fields = ["created", "modified"]
        create_only_fields = ("added_by",)

    def _get_default_serviceable_area(self):
        san_jose = os.path.join(settings.BASE_DIR, "common/City_Limits.geojson")
        if os.path.exists(san_jose):
            with open(san_jose, "r+", encoding="utf-8") as f:
                geojson = f.read()
                area = GEOSGeometry(json.loads(geojson))
            return area

    def validate_serviceable_area(self, area):
        if not area:
            return self._get_default_serviceable_area()
        else:
            if isinstance(area, Polygon):
                area = MultiPolygon(fromstr(str(area)))
        return area

    def create(self, validated_data):
        user = self.context.get("request").user
        if not validated_data.get("serviceable_area"):
            validated_data["serviceable_area"] = self._get_default_serviceable_area()
        project = super().create(validated_data)
        ProjectUser.objects.get_or_create(user=user, project=project, assigned_by=user)
        sys_admins = User.objects.filter(role__role_name=SystemRoles.SYS_ADMIN)
        for admin in sys_admins:
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

    def validate_project(self, proj):
        try:
            project = self.context.get("all_projects").get(project_id=proj)
        except Exception as exc:
            raise serializers.ValidationError(f"No project found with ID {proj}") from exc
        return project

    class Meta:
        model = Zone
        fields = ("zone_name", "geofence", "project", "zone_desc", "id", "remaining_zones")
        geo_field = "geofence"


class StatusKeywordSerializer(SerializerCreateUpdateOnlyMixin, serializers.ModelSerializer):

    added_by = serializers.CreateOnlyDefault(default=serializers.CurrentUserDefault())

    class Meta:
        model = StatusKeyword
        fields = ("id", "status_category", "name", "keyword", "description", "added_by")
        create_only_fields = ("added_by",)
