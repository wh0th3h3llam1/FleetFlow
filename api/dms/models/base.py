from django.contrib.gis.db import models
from django.utils import timezone

from common.choices import (
    NOTIFICATION_CATEGORY_CHOICES,
    NOTIFICATION_PRIORITY_CHOICES,
    NOTIFICATION_TYPE_CHOICES,
    PROJECT_STATUS_CHOICES,
    STATUS_CATEGORY_CHOICES,
    TAG_TYPE_CHOICES,
)
from common.constants import NotificationPriority, NotificationType, ProjectStatus
from core.models import BaseModel
from users.models import User


class PlanningTemplate(BaseModel):
    template_name = models.CharField(max_length=100, verbose_name="Template Name", unique=True)

    # Warehouse Timing
    loading_start_time = models.TimeField(verbose_name="Loading Start Time", default="06:00")
    loading_end_time = models.TimeField(verbose_name="Loading End Time", default="09:00")

    offloading_start_time = models.TimeField(verbose_name="Offloading Start Time", default="17:00")
    offloading_end_time = models.TimeField(verbose_name="Offloading End Time", default="22:00")

    offloading_time = models.PositiveIntegerField(
        verbose_name="Offloading time in minutes", default="20"
    )
    loading_time = models.PositiveIntegerField(verbose_name="Loading time in minutes", default="20")

    # planning constraint
    round_trip = models.BooleanField(default=False)
    zone_constraint = models.BooleanField(default=False)
    tag_validations = models.BooleanField(default=False)
    fill_ratio = models.PositiveSmallIntegerField(verbose_name="Fill Ratio %", default=100)

    planning_time = models.PositiveIntegerField(
        verbose_name="Planning time in minutes", default="15"
    )
    result_ttl = models.PositiveIntegerField(verbose_name="Result time in minutes", default="25")

    traffic_jams = models.BooleanField(default=True)
    toll_roads = models.BooleanField(default=True)
    disable_compatibility = models.BooleanField(default=False)

    # other flags for backend only
    combine_processing_time = models.BooleanField(default=True)
    performer_transport_restriction = models.BooleanField(default=True)
    hardlink = models.BooleanField(default=True)
    precedence = models.BooleanField(default=True)
    storage_restriction = models.BooleanField(default=True)
    disable_time_windows = models.BooleanField(default=False)
    disable_performer_transport_shift = models.BooleanField(default=False)
    warehouse_gate_count = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.template_name}"


class Project(BaseModel):
    project_id = models.CharField(max_length=255, verbose_name="Project ID", unique=True)
    project_name = models.CharField(max_length=255, verbose_name="Project Name")
    base_address = models.TextField(verbose_name="Base Address")
    base_coordinates = models.PointField(verbose_name="Coordinates")

    planning_template = models.ForeignKey(
        to=PlanningTemplate,
        null=True,
        blank=True,
        related_name="planning_templates",
        verbose_name="Planning Template",
        on_delete=models.SET_NULL,
    )

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


class Notification(BaseModel):
    title = models.CharField(verbose_name="Notification Title", max_length=150)
    message = models.TextField(verbose_name="Notification Message")
    link = models.CharField(verbose_name="Link URL", max_length=500, null=True, blank=True)
    priority = models.CharField(
        verbose_name="Notification Priority",
        max_length=10,
        choices=NOTIFICATION_PRIORITY_CHOICES,
        default=NotificationPriority.LOW,
    )
    expiration_time = models.DateTimeField(verbose_name="Notification Expiration Time")
    notification_type = models.CharField(
        verbose_name="Notification Type",
        max_length=10,
        choices=NOTIFICATION_TYPE_CHOICES,
        default=NotificationType.INFO,
    )
    notification_category = models.CharField(
        verbose_name="Notification Category",
        max_length=50,
        choices=NOTIFICATION_CATEGORY_CHOICES,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.message}"


class UserNotification(BaseModel):
    user = models.ForeignKey(User, related_name="user_notifications", on_delete=models.CASCADE)
    notification = models.ForeignKey(
        Notification, verbose_name="Notification", on_delete=models.CASCADE, related_name="users"
    )
    is_read = models.BooleanField(verbose_name="Mark as read", default=False)
    read_on = models.DateTimeField(verbose_name="Read on", null=True, blank=True)

    def __str__(self):
        return f"{self.user.full_name} - Read {self.is_read}"


class Tag(BaseModel):
    tag = models.CharField(verbose_name="Tag Name", max_length=200, unique=True)
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    tag_type = models.CharField(choices=TAG_TYPE_CHOICES, verbose_name="Tag Type", max_length=32)

    def __str__(self):
        return f"{self.tag}"

    class Meta:
        verbose_name_plural = "Tags"
