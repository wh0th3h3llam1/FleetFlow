from django.contrib.gis.db import models
from django.utils import timezone

from common.choices import PROJECT_STATUS_CHOICES, STATUS_CATEGORY_CHOICES
from common.constants import ProjectStatus
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
    user = models.ForeignKey(to=User, related_name="projects", on_delete=models.CASCADE)
    project = models.ForeignKey(to=Project, related_name="users", on_delete=models.CASCADE)
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
        verbose_name = "Project User"
        verbose_name_plural = "Project Users"
        constraints = [
            models.UniqueConstraint(fields=("user", "project"), name="user_project_unique")
        ]


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


class StatusKeyword(BaseModel):
    status_category = models.CharField(
        verbose_name="Category", max_length=15, choices=STATUS_CATEGORY_CHOICES
    )
    # synonym for the status
    name = models.CharField(verbose_name="Status", max_length=50, unique=True)
    # original status keyword
    keyword = models.CharField(verbose_name="Keyword", max_length=100)
    description = models.CharField(
        verbose_name="Description", max_length=100, blank=True, null=True
    )
    added_by = models.ForeignKey(
        to=User, related_name="status_keywords", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        verbose_name = "Status Keyword"
        verbose_name_plural = "Status Keywords"

    def __str__(self):
        return "{} - {}".format(self.name, self.status_category)
