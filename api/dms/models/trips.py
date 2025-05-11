import logging
from decimal import Decimal

from dateutil import tz

from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db.models import Sum, Count, F, Q
from django.utils import timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django_lifecycle import hook, AFTER_CREATE, LifecycleModel

from common.choices import (
    TRIP_STATUS_CHOICES,
    ATTACHMENT_FORMATS,
    MESSAGE_FORMATS,
    DRIVER_EXPENSE_CATEGORY,
    SENSOR_READING_LOG_STATUS,
    TRIP_TEMPERATURE_FILE_STATUS,
)
from common.constants import (
    OrderConstants,
    TripStatus,
    ChatMessageFormat,
    TripStatusLogs,
    FieldConstants,
    TripTemperatureFileStatus,
)
from common.helpers import file_size
from core.models import BaseModel
from dms.helpers import (
    get_chat_log_location,
    get_driver_expense_attachment_path,
    get_trip_temp_log_file_path,
    get_vehicle_partition,
)
from dms.models import Driver, Vehicle, VehicleStorage, StatusKeyword
from dms.models.orders import Order
from users.models import User


logger = logging.getLogger(__name__)


class Helper(BaseModel):
    helper_name = models.CharField(max_length=255, blank=True, null=True)


class Trip(BaseModel, LifecycleModel):
    TRIP_PREFIX = "TRIP"

    reference_number = models.CharField(verbose_name="Reference Number", max_length=50)
    status = models.CharField(
        choices=TRIP_STATUS_CHOICES,
        default=TripStatus.SCHEDULED,
        verbose_name="Trip Status",
        max_length=50,
    )
    helper_name = models.CharField(max_length=50, verbose_name="Helper Name", blank=True, null=True)
    added_by = models.ForeignKey(
        User,
        related_name="trips_created",
        verbose_name="Created By",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    actual_distance = models.DecimalField(
        verbose_name="Actual Distance", blank=True, null=True, decimal_places=2, max_digits=10
    )
    planned_distance = models.DecimalField(
        verbose_name="Planned Distance", blank=True, null=True, decimal_places=2, max_digits=10
    )
    trip_date = models.DateField(verbose_name="Trip Date")
    planned_start_time = models.DateTimeField(blank=True, null=True, verbose_name="Planned Start")
    planned_end_time = models.DateTimeField(blank=True, null=True, verbose_name="Planned End")
    trip_start = models.DateTimeField(blank=True, null=True, verbose_name="Trip Start")
    trip_end = models.DateTimeField(blank=True, null=True, verbose_name="Trip End")

    planned_travelling_time = models.PositiveIntegerField(
        blank=True, null=True, verbose_name="Planned Travelling Time"
    )
    travelling_time = models.PositiveIntegerField(default=0, verbose_name="Travelling Time")
    break_time = models.PositiveIntegerField(default=0, verbose_name="Break Time")
    processing_time = models.PositiveIntegerField(default=0, verbose_name="Processing Time")

    driver = models.ForeignKey(
        Driver, related_name="driver_trips", verbose_name="Driver", on_delete=models.CASCADE
    )
    vehicle = models.ForeignKey(
        Vehicle, related_name="vehicle_trips", verbose_name="Vehicle", on_delete=models.CASCADE
    )
    last_driver_location = models.ForeignKey(
        "TripMetrics",
        related_name="driver_last_location",
        verbose_name="Last Location of Driver",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    trip_start_km = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name="Trip starting time kms"
    )
    trip_end_km = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name="Trip ending time kms"
    )

    @property
    def trip_id(self):
        return "{}{}".format(self.TRIP_PREFIX, str(self.id).zfill(2))

    def get_trip_pk(self, trip_id) -> int:
        return int(trip_id.replace("TRIP", ""))

    def add_order_to_trip(self, order: Order, sequence_number: int):
        if (
            self.status == TripStatus.SCHEDULED
            and order.status == OrderConstants.OrderStatus.UNASSIGNED
        ):
            order.status = OrderConstants.OrderStatus.ASSIGNED
            order.assigned_on = timezone.now()
        elif (
            self.status == TripStatus.ACTIVE
            and order.status == OrderConstants.OrderStatus.UNASSIGNED
        ):
            order.status = OrderConstants.OrderStatus.PICKED_UP
            order.assigned_on = timezone.now()
            order.picked_up_on = timezone.now()
        order.trip = self
        order.sequence_number = sequence_number
        order.save()
        return order

    def start_trip(self):
        msg = None
        if self.status == TripStatus.ACTIVE:
            return

        if self.status == TripStatus.SCHEDULED:
            self.trip_start = timezone.now()
            msg = TripStatusLogs.start
            orders = Order.objects.filter(trip=self, order_type=OrderConstants.OrderType.DELIVERY)
            orders.update(status=OrderConstants.OrderStatus.PICKED_UP, picked_up_on=timezone.now())
        elif self.status == TripStatus.PAUSED:
            msg = TripStatusLogs.resume
        self.add_trip_log(msg=msg)
        self.status = TripStatus.ACTIVE
        self.save()

    def complete_trip(self):
        # TODO capture distance travelled as well break time and travelling time.
        self.trip_end = timezone.now()
        try:
            total_processing_time = Order.objects.filter(
                trip=self,
                status__in=[
                    OrderConstants.OrderStatus.SUCCESSFUL,
                    OrderConstants.OrderStatus.FAILED,
                ],
            ).aggregate(processing_time=Sum("processing_time"))["processing_time"]
            break_time = (
                self.trip_breaks.filter(break_end__isnull=False)
                .annotate(duration=F("break_end") - F("break_start"))
                .aggregate(total_break=Sum("duration"))
                .get("total_break")
            )
            total_break_time = (break_time.seconds // 60) if break_time else 0
            journey_time = self.trip_end - self.trip_start
            journey_time_mins = journey_time.seconds // 60
            self.travelling_time = journey_time_mins - total_break_time - total_processing_time
            self.processing_time = total_processing_time
            self.break_time = total_break_time
            try:
                self.actual_distance = abs(self.trip_end_km - self.trip_start_km)
            except Exception as e:
                logger.exception(e)
                self.actual_distance = 0
        except Exception as e:
            logger.exception(e)
        self.save()
        self.add_trip_log(TripStatusLogs.end)

    def add_driver_break(self, driver, break_reason):
        break_obj = DriverBreak.objects.create(
            driver=driver,
            trip=self,
            break_status_keywords=break_reason if break_reason else None,
            break_start=timezone.now(),
        )
        self.add_trip_log(TripStatusLogs.on_break)
        return break_obj

    def complete_driver_break(self, driver, break_reason):
        break_obj = DriverBreak.objects.filter(
            driver=driver, trip=self, break_start__day=timezone.now().day
        ).latest("created")
        if break_obj:
            break_obj.break_end = timezone.now()
            break_obj.save()
            self.break_time += (break_obj.break_end - break_obj.break_start).seconds // 60
            self.save()
            self.add_trip_log(TripStatusLogs.on_duty)
        return break_obj

    def trip_order_partition(self):
        orders = Order.objects.prefetch_related("order_items").filter(trip=self)
        dry_items_cbm = 0
        chilled_items_cbm = 0
        frozen_items_cbm = 0
        for order in orders:
            dry_items_total = (
                order.order_items.filter(item__storage_type=OrderConstants.StorageTypes.DRY)
                .aggregate(total_cbm=Sum("line_item_cbm"))
                .get("total_cbm")
            )
            dry_items_cbm += dry_items_total if dry_items_total else Decimal("0.00")
            chilled_items_total = (
                order.order_items.filter(item__storage_type=OrderConstants.StorageTypes.CHILLED)
                .aggregate(total_cbm=Sum("line_item_cbm"))
                .get("total_cbm")
            )
            chilled_items_cbm += chilled_items_total if chilled_items_total else Decimal("0.00")
            frozen_items_total = (
                order.order_items.filter(item__storage_type=OrderConstants.StorageTypes.FROZEN)
                .aggregate(total_cbm=Sum("line_item_cbm"))
                .get("total_cbm")
            )
            frozen_items_cbm += frozen_items_total if frozen_items_total else Decimal("0.00")

        vehicle_cbm_capacity = self.vehicle.cbm_capacity

        data = {
            "vehicle_cbm_capacity": vehicle_cbm_capacity,
            "frozen_items_cbm": frozen_items_cbm,
            "chilled_items_cbm": chilled_items_cbm,
            "dry_items_cbm": dry_items_cbm,
        }

        return get_vehicle_partition(data)

    def total_trip_cases(self):
        return self.trip_orders.annotate(order_cases=Sum("order_items__total_cases")).aggregate(
            total_cases=Sum("order_cases")
        )

    def total_orders(self):
        return self.trip_orders.count()

    def total_items(self):
        return sum([order.item_count for order in self.trip_orders.all()])

    def total_item_cbm(self):
        return sum([order.total_item_cbm for order in self.trip_orders.all()])

    def trip_order_count(self):
        return self.trip_orders.aggregate(
            total=Count("id"),
            assigned=Count(
                "id", filter=Q(status=OrderConstants.OrderStatus.ASSIGNED), distinct=True
            ),
            picked_up=Count(
                "id", filter=Q(status=OrderConstants.OrderStatus.PICKED_UP), distinct=True
            ),
            successful=Count(
                "id", filter=Q(status=OrderConstants.OrderStatus.SUCCESSFUL), distinct=True
            ),
            partially_delivered=Count(
                "id", filter=Q(status=OrderConstants.OrderStatus.PARTIAL), distinct=True
            ),
            failed=Count("id", filter=Q(status=OrderConstants.OrderStatus.FAILED), distinct=True),
        )

    def add_trip_log(self, msg, user=False):
        if not user:
            user = self.driver.user
        trip_log = TripLog.objects.create(
            trip=self, trip_status=self.status, message=msg, added_by=user
        )
        return trip_log

    def __str__(self):
        return f"{self.trip_id} - {self.reference_number}"


class BarcodeScanEvent(BaseModel):
    SCAN_TYPE_CHOICES = (
        (OrderConstants.OrderType.PICK_UP, "Pick up"),
        (OrderConstants.OrderType.DELIVERY, "Delivery"),
    )

    order = models.ForeignKey(
        Order, related_name="scanned_items", on_delete=models.CASCADE, verbose_name="Scanned Items"
    )
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, verbose_name="Trip")
    scan_text = models.CharField(max_length=255, verbose_name="Scanned Text")
    scan_type = models.CharField(max_length=50, choices=SCAN_TYPE_CHOICES)

    def __str__(self):
        return f"{self.scan_type} - {self.scan_text}"


class TripChatLog(BaseModel):
    sender = models.ForeignKey(
        User,
        verbose_name="Message Sender",
        related_name="sent_messages",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    driver = models.ForeignKey(
        Driver, related_name="driver_messages", on_delete=models.CASCADE, verbose_name="Driver"
    )
    trip = models.ForeignKey(
        Trip,
        related_name="trip_chats",
        verbose_name="Trip",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    message = models.TextField(verbose_name="Message Text")
    attachment = models.FileField(
        verbose_name="Attachment",
        upload_to=get_chat_log_location,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(ATTACHMENT_FORMATS), file_size],
    )
    message_format = models.CharField(
        choices=MESSAGE_FORMATS, max_length=32, verbose_name="Message Type", default="text"
    )
    notify = models.BooleanField(verbose_name="Notify", default=False)

    def is_text(self):
        return self.message_format == ChatMessageFormat.TEXT

    @hook(AFTER_CREATE)
    def send_ws_message(self):
        if self.sender == self.driver:
            channel_layer = get_channel_layer()

            driver = self.driver
            driver.last_seen_on = timezone.now()
            driver.save()
            async_to_sync(channel_layer.group_send)(
                str(driver.project.project_id),
                {
                    "type": "message_from_driver",
                    "message": "Driver({}) posted an update {}".format(
                        driver.user.full_name, self.message
                    ),
                    "from": driver.user.full_name,
                    "driver_id": driver.id,
                    "project_id": driver.project.project_id,
                },
            )

    def __str__(self):
        return f"{self.trip.trip_id} - {self.sender}, {self.created}"


class TripLog(BaseModel):
    # Log all synonyms here

    trip = models.ForeignKey(
        Trip, related_name="logs", verbose_name="Trip Logs", on_delete=models.CASCADE
    )
    trip_status = models.CharField(
        choices=TRIP_STATUS_CHOICES,
        default=TripStatus.SCHEDULED,
        verbose_name="Trip Status",
        max_length=50,
    )
    message = models.TextField(verbose_name="Message")
    added_by = models.ForeignKey(
        User, related_name="trip_log", verbose_name="Created By", on_delete=models.DO_NOTHING
    )

    def __str__(self):
        return f"{self.message} - {self.added_by}"

    class Meta:
        ordering = [
            "-created",
        ]


class DriverBreak(BaseModel):
    driver = models.ForeignKey(
        Driver, related_name="driver_breaks", verbose_name="Driver Break", on_delete=models.CASCADE
    )
    trip = models.ForeignKey(
        Trip, related_name="trip_breaks", blank=True, null=True, on_delete=models.CASCADE
    )
    break_start = models.DateTimeField(verbose_name="Break Start")
    break_end = models.DateTimeField(verbose_name="Break End", blank=True, null=True)
    break_status_keywords = models.ForeignKey(
        StatusKeyword,
        related_name="break_reason",
        verbose_name="Break Status Keyword",
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
    )

    # update break end if trip completed by admin to shift end

    def __str__(self):
        return f"{self.driver.user.full_name} - {self.break_start} to {self.break_end}"


class DriverExpense(BaseModel):
    expense_name = models.CharField(max_length=50, verbose_name="Expense Name")
    expense_category = models.CharField(
        choices=DRIVER_EXPENSE_CATEGORY, verbose_name="Expense category", max_length=20
    )
    notes = models.TextField(verbose_name="notes", blank=True, null=True)
    trip = models.ForeignKey(
        Trip,
        verbose_name="Driver Trip",
        on_delete=models.CASCADE,
        related_name="trip_expenses",
        null=True,
        blank=True,
    )
    driver = models.ForeignKey(
        Driver, related_name="driver_expense", verbose_name="Driver", on_delete=models.CASCADE
    )
    amount = models.DecimalField(
        verbose_name="Amount", blank=True, null=True, decimal_places=2, max_digits=10
    )
    fuel_consumption = models.DecimalField(
        verbose_name="Fuel Consumption", blank=True, null=True, decimal_places=2, max_digits=10
    )
    attachment = models.FileField(
        verbose_name="Attachment",
        upload_to=get_driver_expense_attachment_path,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.expense_name


class TripMetrics(BaseModel):
    driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, related_name="driver_locations", blank=True, null=True
    )
    trip = models.ForeignKey(
        Trip,
        related_name="trip_coordinates",
        on_delete=models.CASCADE,
        verbose_name="Trip",
        blank=True,
        null=True,
    )
    coordinates = models.PointField()
    battery = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="Battery Percentage"
    )
    speed = models.PositiveIntegerField(verbose_name="Vehicle Speed", default=0)
    timestamp = models.DateTimeField(verbose_name="Time", default=timezone.now)

    # TODO Device Details (OS Version and other)


class TripTemperatureLog(BaseModel):
    sensor = models.ForeignKey(
        VehicleStorage,
        related_name="trip_temperature_sensor",
        verbose_name="Sensor ID",
        on_delete=models.CASCADE,
    )
    temperature = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Temperature")
    timestamp = models.DateTimeField(verbose_name="Trip Time", default=timezone.now)

    @property
    def ts(self):
        return self.timestamp.astimezone(tz.gettz(settings.TIME_ZONE)).strftime(
            FieldConstants.FULL_TIME_FORMAT
        )

    def __str__(self):
        return f"{self.sensor.sensor_id} - {self.temperature}"


class SensorReadingLog(BaseModel):
    sensor = models.ForeignKey(
        VehicleStorage, related_name="Sensor", on_delete=models.CASCADE, blank=True, null=True
    )
    file_name = models.CharField(max_length=200, verbose_name="File Name")
    status = models.CharField(
        max_length=255, verbose_name="Status of the Task", choices=SENSOR_READING_LOG_STATUS
    )
    reason = models.CharField(
        max_length=255, verbose_name="Reason for the Status", blank=True, null=True
    )

    def __str__(self):
        return f"{self.sensor} - {self.status}"


class TripTemperatureFile(BaseModel):
    FILE_FORMATS = ["xls", "xlsx"]
    uploaded_filename = models.CharField(max_length=250, blank=True, null=True)
    file_name = models.FileField(
        upload_to=get_trip_temp_log_file_path,
        validators=[FileExtensionValidator(allowed_extensions=FILE_FORMATS)],
        verbose_name="File Name",
    )
    status = models.CharField(
        max_length=100,
        choices=TRIP_TEMPERATURE_FILE_STATUS,
        default=TripTemperatureFileStatus.NOT_PROCESSED,
    )
    processed = models.BooleanField(verbose_name="File Processed", default=False)
    added_by = models.ForeignKey(
        User,
        related_name="temperature_files_added_by",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.file_name} - {self.status}"
