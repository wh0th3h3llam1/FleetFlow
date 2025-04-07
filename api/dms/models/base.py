from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.text import slugify


from django_lifecycle import AFTER_CREATE, BEFORE_CREATE, BEFORE_UPDATE, hook
from django_lifecycle.conditions import WhenFieldHasChanged

from common.choices import PROJECT_STATUS_CHOICES
from common.constants import FieldConstants, ProjectStatus
from core.models import BaseModel
from users.models import User


class Project(BaseModel):
    project_id = models.CharField(max_length=255, verbose_name="Project ID", unique=True)
    project_name = models.CharField(max_length=255, verbose_name="Project Name")
    base_address = models.TextField(verbose_name="Base Address")
    base_coordinates = models.PointField(verbose_name="Coordinates")

    status = models.CharField(
        choices=PROJECT_STATUS_CHOICES,
        default=ProjectStatus.ACTIVE,
        verbose_name="Status",
        max_length=32,
    )

    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="added_projects"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_projects"
    )

    deactivated_by = models.ForeignKey(
        to=User,
        related_name="deactivated_projects",
        blank=True,
        null=True,
        verbose_name="Inactive By",
        on_delete=models.SET_NULL,
    )
    deactivated_on = models.DateTimeField(blank=True, null=True, verbose_name="Deactivated On")

    serviceable_area = models.MultiPolygonField(
        verbose_name="Project GeoFence", blank=True, null=True, geography=True
    )

    def __str__(self):
        return f"{self.project_name} - {self.base_address}"

    def deactivate_project(self, by: User):
        self.status = ProjectStatus.DEACTIVATED
        self.deactivated_on = timezone.now()
        self.save()

    def activate_project(self, by: User):
        self.status = ProjectStatus.ACTIVE
        self.save()


class ProjectUser(BaseModel):
    user = models.ForeignKey(
        to=User, related_name="user_projects", on_delete=models.CASCADE, verbose_name="User"
    )
    project = models.ForeignKey(
        to=Project, related_name="project_users", on_delete=models.CASCADE, verbose_name="Project"
    )
    assigned_by = models.ForeignKey(
        to=User,
        related_name="project_assigned_to",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.user.full_name} - {self.project.project_id}"

    class Meta:
        verbose_name_plural = "ProjectUsers"


class Zone(models.Model):
    zone_name = models.CharField(verbose_name="Zone Name", max_length=100, unique=True)
    geofence = models.GeometryField(verbose_name="Geofence")
    project = models.ForeignKey(
        to=Project, verbose_name="Project", related_name="project_zones", on_delete=models.CASCADE
    )
    zone_desc = models.CharField(
        verbose_name="Zone Description", max_length=100, blank=True, null=True
    )
    added_by = models.ForeignKey(
        to=User,
        verbose_name="Added By",
        on_delete=models.SET_NULL,
        related_name="zones_added",
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        to=User,
        verbose_name="Updated By",
        on_delete=models.SET_NULL,
        related_name="zones_updated",
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.zone_name}"
