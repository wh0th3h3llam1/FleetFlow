import datetime

from django.contrib.gis.db import models
from django.db.models import Count, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_lifecycle import hook, BEFORE_UPDATE, LifecycleModel, AFTER_CREATE
from phonenumber_field.modelfields import PhoneNumberField

from core.models import BaseModel
from common.choices import (
    ATTACHMENT_TYPE_CHOICES,
    ORDER_TYPE_CHOICES,
    STORAGE_TYPE_CHOICES,
    PAYMENT_TYPE_CHOICES,
    ORDER_STATUS_CHOICES,
    SERVICE_TYPE_CHOICES,
    ITEM_UNIT_CHOICES,
)
from common.constants import (
    FieldConstants,
    ItemUnits,
    OrderConstants,
    OrderStatusLogs,
    ServiceType,
)
from common.helpers import get_order_attachment_path, no_past_date
from dms.models import Project, StatusKeyword
from users.models import User


class ItemMaster(BaseModel):
    item_no = models.CharField(unique=True, max_length=20)
    storage_type = models.CharField(choices=STORAGE_TYPE_CHOICES, max_length=10)
    weight = models.DecimalField(verbose_name="Weight (kg)", max_digits=10, decimal_places=5)
    cbm = models.DecimalField(verbose_name="Volume (cbm)", max_digits=14, decimal_places=10)
    item_description = models.CharField(max_length=200, verbose_name="Item Description")
    unit = models.CharField(choices=ITEM_UNIT_CHOICES, default=ItemUnits.KG, max_length=20)
    case_factor = models.DecimalField(verbose_name="Case Factor", max_digits=10, decimal_places=5)
    length = models.DecimalField(
        verbose_name="Length", blank=True, null=True, max_digits=10, decimal_places=5
    )
    width = models.DecimalField(
        verbose_name="Width", blank=True, null=True, max_digits=10, decimal_places=5
    )
    height = models.DecimalField(
        verbose_name="Height", blank=True, null=True, max_digits=10, decimal_places=5
    )

    def __str__(self):
        return f"{self.item_no} - {self.item_description}"


class Order(LifecycleModel, BaseModel):
    ORDER_PREFIX = "ORD"

    reference_number = models.CharField(verbose_name="Reference Number", max_length=200)
    invoice_number = models.CharField(
        verbose_name="Invoice Number", max_length=200, null=True, blank=True
    )
    execution_date = models.DateField(
        verbose_name="Execution Date",
        validators=[
            no_past_date,
        ],
    )

    pickup_address = models.TextField(verbose_name="Pickup Address")
    drop_address = models.TextField(verbose_name="Drop Address")
    pickup_point = models.PointField(verbose_name="Pickup Coordinates", blank=True, null=True)
    drop_point = models.PointField(verbose_name="Drop Coordinates", blank=True, null=True)

    # for customer profilling
    customer_address = models.ForeignKey(
        to="CustomerAddress",
        related_name="customer_address_orders",
        verbose_name="Address",
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        to=Project, related_name="project_orders", on_delete=models.CASCADE, blank=True, null=True
    )
    order_type = models.CharField(
        choices=ORDER_TYPE_CHOICES, default=OrderConstants.OrderType.DELIVERY, max_length=20
    )

    order_remarks = models.TextField(
        verbose_name="Order Remarks", default="N/A", blank=True, null=True
    )
    driver_remarks = models.TextField(
        verbose_name="Driver Remarks", default="N/A", blank=True, null=True
    )

    customer_name = models.CharField(
        verbose_name="Customer Name", max_length=FieldConstants.NAME_LENGTH
    )
    contact_email = models.EmailField(verbose_name="Contact Email Address", blank=True, null=True)
    contact_person = models.CharField(
        max_length=FieldConstants.NAME_LENGTH, verbose_name="Contact Person", blank=True, null=True
    )
    contact_number = PhoneNumberField(
        verbose_name=_("Contact Number"),
        blank=True,
        null=True,
    )

    delivery_window_start = models.TimeField(
        verbose_name="Delivery Window Start Time", blank=True, null=True
    )
    delivery_window_end = models.TimeField(
        verbose_name="Delivery Window End Time", blank=True, null=True
    )
    delivery_point = models.PointField(
        verbose_name="Delivery Address Coordinates", blank=True, null=True
    )

    order_value = models.DecimalField(
        verbose_name="Order Value", blank=True, null=True, max_digits=10, decimal_places=2
    )
    service_type = models.CharField(
        verbose_name="Service Type",
        choices=SERVICE_TYPE_CHOICES,
        default=ServiceType.B2B,
        max_length=5,
    )
    # order capacity
    instructions = models.TextField(verbose_name="Special Instructions", blank=True, null=True)
    payment_type = models.CharField(
        verbose_name="Payment Method",
        choices=PAYMENT_TYPE_CHOICES,
        default=OrderConstants.PaymentMethod.PREPAID,
        max_length=25,
    )
    require_barcode_scanning = models.BooleanField(
        verbose_name="Barcode Scanning required",
        default=False,
    )
    require_proof_of_delivery = models.BooleanField(
        verbose_name="Proof Of Delivery required",
        default=True,
    )
    customer_notifications = models.BooleanField(
        verbose_name="Send Customer Notifications",
        default=True,
    )

    status = models.CharField(
        verbose_name="Order Status",
        choices=ORDER_STATUS_CHOICES,
        default=OrderConstants.OrderStatus.UNASSIGNED,
        max_length=25,
    )

    status_keyword = models.ForeignKey(
        to=StatusKeyword,
        on_delete=models.SET_NULL,
        related_name="status_keyword_orders",
        blank=True,
        null=True,
        verbose_name="Status keyword",
    )
    est_pickup_time = models.DateTimeField(
        verbose_name="Estimated Pickup Time",
        blank=True,
        null=True,
    )
    est_drop_time = models.DateTimeField(verbose_name="Estimated Drop Time", blank=True, null=True)

    # set to 1 once trip is active and the order is picked_up/enroute
    attempt_number = models.PositiveIntegerField(verbose_name="Attempt Number", default=0)
    unassigned_on = models.DateTimeField(blank=True, null=True)
    assigned_on = models.DateTimeField(blank=True, null=True)
    picked_up_on = models.DateTimeField(blank=True, null=True)
    completed_on = models.DateTimeField(blank=True, null=True)
    failed_on = models.DateTimeField(blank=True, null=True)
    enroute_on = models.DateTimeField(blank=True, null=True)
    trip = models.ForeignKey(
        to="Trip",
        on_delete=models.SET_NULL,
        related_name="trip_orders",
        blank=True,
        null=True,
    )
    # decided by either trip planning algorithm or by handler manually
    sequence_number = models.PositiveIntegerField(verbose_name="Sequence Number", default=0)
    processing_time = models.PositiveIntegerField(verbose_name="Processing Time", default=5)
    planned_processing_time = models.PositiveIntegerField(
        verbose_name="Planned Processing Time",
        default=5,
    )

    payment_collected = models.DecimalField(
        verbose_name="Payment Collected", blank=True, null=True, max_digits=10, decimal_places=2
    )

    # set to true when order pod is uploaded
    is_pod_uploaded = models.BooleanField(default=False)

    customer_detail_link = models.URLField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(
        to=User, related_name="created_orders", on_delete=models.SET_NULL, blank=True, null=True
    )

    updated_by = models.ForeignKey(
        to=User,
        related_name="updated_orders",
        on_delete=models.SET_NULL,
        verbose_name="Updated By",
        blank=True,
        null=True,
    )
    cancellation_remarks = models.CharField(max_length=255, blank=True, null=True)
    cod_remarks = models.CharField(max_length=255, blank=True, null=True)
    cancelled_on = models.DateTimeField(verbose_name="Cancelled On", blank=True, null=True)

    driver = models.CharField(verbose_name="Driver", blank=True, null=True, max_length=200)

    def __str__(self) -> str:
        return f"{self.reference_number} - {self.customer_name}"

    @property
    def location_window(self):
        order_start_date = self.execution_date
        order_end_date = self.execution_date
        if self.delivery_window_end < self.delivery_window_start:
            order_end_date = order_start_date + datetime.timedelta(days=1)
        return {
            "start_time": datetime.datetime.combine(order_start_date, self.delivery_window_start),
            "end_time": datetime.datetime.combine(order_end_date, self.delivery_window_end),
        }

    @property
    def delivery_window(self):
        if self.delivery_window_start and self.delivery_window_end:
            return (
                f"{self.delivery_window_start.strftime(FieldConstants.TIME_FORMAT)} to "
                f"{self.delivery_window_end.strftime(FieldConstants.TIME_FORMAT)}"
            )
        return None

    @property
    def etc(self):
        if self.order_type == OrderConstants.OrderType.DELIVERY and self.est_drop_time:
            etc = self.est_drop_time.strftime(FieldConstants.FULL_DATE_TIME_FORMAT)
        elif self.order_type == OrderConstants.OrderType.PICK_UP and self.est_pickup_time:
            etc = self.est_pickup_time.strftime(FieldConstants.FULL_DATE_TIME_FORMAT)
        else:
            etc = "N/A"
        return etc

    def address(self):
        if self.order_type == OrderConstants.OrderType.DELIVERY:
            return self.drop_address
        else:
            return self.pickup_address

    @property
    def coordinates(self):
        if self.order_type == OrderConstants.OrderType.DELIVERY:
            return self.drop_point
        else:
            return self.pickup_point

    @property
    def remarks(self):
        if self.status in [
            OrderConstants.OrderStatus.FAILED,
            OrderConstants.OrderStatus.SUCCESSFUL,
            OrderConstants.OrderStatus.PARTIAL,
        ]:
            return self.driver_remarks
        elif self.status == OrderConstants.OrderStatus.CANCELLED:
            return self.cancellation_remarks

    @property
    def order_id(self):
        return f"{self.ORDER_PREFIX}, {str(self.id).zfill(2)}"

    @property
    def get_order_items(self):
        return [
            {
                "item_no": order_item.item.item_no,
                "quantity": order_item.original_quantity,
                "item_description": order_item.item.item_description,
                "delivered_quantity": order_item.delivered_quantity,
                "total_cases": order_item.total_cases,
                "delivered_cases": order_item.delivered_cases,
            }
            for order_item in self.order_items.select_related("item").all()
        ]

    @property
    def get_detailed_order_items(self):
        return [
            {
                "item_id": order_item.item.id,
                "item_no": order_item.item.item_no,
                "original_quantity": order_item.original_quantity,
                "delivered_quantity": order_item.delivered_quantity,
                "item_description": order_item.item.item_description,
                "storage_type": order_item.item.storage_type,
                "cbm": order_item.item.cbm,
                "weight": order_item.item.weight,
            }
            for order_item in self.order_items.select_related("item").all()
        ]

    @staticmethod
    def get_order_pk(order_id):
        return int(order_id.replace(Order.ORDER_PREFIX, ""))

    @hook(BEFORE_UPDATE, when="status", is_now=OrderConstants.OrderStatus.UNASSIGNED)
    def unassigned_order(self):
        self.unassigned_on = timezone.now()
        self.assigned_on = None
        self.picked_up_on = None
        self.trip = None

    @hook(AFTER_CREATE, when="status", is_now=OrderConstants.OrderStatus.UNASSIGNED)
    def unassigned(self):
        # from dms.tasks import send_notification

        # send customer notification
        # self.unassigned_on = timezone.now()
        # send_notification.apply_async(args=[json.dumps(self.id)])
        pass
        # send websocket message

    @hook(BEFORE_UPDATE, when="status", is_now=OrderConstants.OrderStatus.SUCCESSFUL)
    def completed(self):
        # send customer notification
        # send websocket message
        msg = self.reference_number + " - " + OrderStatusLogs.completed
        self.add_order_log(msg)
        self.completed_on = timezone.now()
        self.driver = self.trip.driver.user.full_name if self.trip else ""
        quantity = self.order_items.aggregate(
            delivered_quantity=Sum("delivered_quantity"), original_quantity=Sum("original_quantity")
        )
        if quantity["original_quantity"] != quantity["delivered_quantity"]:
            self.status = OrderConstants.OrderStatus.PARTIAL

        if self.trip:
            self.trip.processing_time += self.processing_time
            self.trip.save()
            self.trip.add_trip_log(msg)

    @hook(
        BEFORE_UPDATE, when="status", is_now=OrderConstants.OrderStatus.ASSIGNED, has_changed=True
    )
    def assigned(self):
        # send customer notification
        # send websocket message
        msg = self.reference_number + " - " + OrderStatusLogs.assigned
        self.add_order_log(msg)
        self.assigned_on = timezone.now()
        # if self.trip:
        #     self.trip.add_trip_log(msg)

    @hook(BEFORE_UPDATE, when="status", is_now=OrderConstants.OrderStatus.PICKED_UP)
    def picked_up(self):
        # send customer notification
        # send websocket message
        msg = self.reference_number + " - " + OrderStatusLogs.picked_up
        self.add_order_log(msg)
        self.picked_up_on = timezone.now()
        # if self.trip:
        #     self.trip.add_trip_log(msg)

    @hook(BEFORE_UPDATE, when="status", is_now=OrderConstants.OrderStatus.ENROUTE)
    def enroute(self):
        # send customer notification
        # update status in UI
        # send websocket message
        msg = self.reference_number + " - " + OrderStatusLogs.enroute
        self.enroute_on = timezone.now()
        self.add_order_log(msg)
        if self.trip:
            self.trip.add_trip_log(msg)

    @hook(BEFORE_UPDATE, when="status", is_now=OrderConstants.OrderStatus.FAILED)
    def failed(self):
        # send customer notification
        # update status in UI
        # send websocket message
        msg = self.reference_number + " - " + OrderStatusLogs.failed
        self.order_items.all().update(delivered_quantity=0)
        self.add_order_log(msg)
        self.failed_on = timezone.now()
        self.trip.add_trip_log(msg)

    @hook(BEFORE_UPDATE, when="status", is_now=OrderConstants.OrderStatus.CANCELLED)
    def cancelled(self):
        # send customer notification
        # update status in UI
        # send websocket message
        msg = f"{self.reference_number} - {OrderStatusLogs.cancelled} - {self.cancellation_remarks}"
        # self.add_order_log(msg)
        self.cancelled_on = timezone.now()
        if self.trip:
            self.trip.add_trip_log(msg)

    def upload_pod(self, attachment, uploaded_by):
        pod_obj = OrderAttachment.objects.create(
            attachment=attachment,
            attachment_type=OrderConstants.AttachmentType.POD,
            order=self,
            uploaded_by=uploaded_by,
        )
        self.is_pod_uploaded = True
        self.updated_by = uploaded_by
        msg = self.reference_number + " - " + OrderStatusLogs.pod_upload
        self.add_order_log(msg)
        if self.trip:
            self.trip.add_trip_log(msg)
        return pod_obj

    def add_order_line_items(self, line_item, quantity, delivered_quantity=None, save_to_db=True):
        if delivered_quantity is None:
            delivered_quantity = quantity
        data = {
            "item": line_item,
            "order": self,
            "original_quantity": quantity,
            "delivered_quantity": int(delivered_quantity),
            "total_cases": quantity / line_item.case_factor,
            "delivered_cases": int(delivered_quantity) / line_item.case_factor,
            "save_to_db": save_to_db,
        }
        return OrderItem.create_order_item(data)

    def add_order_log(self, msg, user=False):
        if not user:
            user = self.updated_by
        # msg = self.reference_number + " - " + msg
        order_log = OrderStatusLog.objects.create(order=self, message=msg, added_by=user)
        return order_log

    def update_delivered_quantity_to_zero(self, instance):
        instance.order_items.all().update(delivered_quantity=0)
        return instance

    def get_storage_types(self, instance) -> list:
        items = self.get_storage_wise_item_count(instance)
        storage_type = list()

        if items.get("dry"):
            storage_type.append("dry")
        if items.get("chilled"):
            storage_type.append("chilled")
        if items.get("frozen"):
            storage_type.append("frozen")
        return storage_type

    def get_storage_wise_item_count(self, instance):
        return instance.order_items.all().aggregate(
            dry=Count("id", filter=Q(item__storage_type=OrderConstants.StorageTypes.DRY)),
            chilled=Count("id", filter=Q(item__storage_type=OrderConstants.StorageTypes.CHILLED)),
            frozen=Count("id", filter=Q(item__storage_type=OrderConstants.StorageTypes.FROZEN)),
            total=Count("id"),
        )

    def get_storage_wise_item_quantity(self, instance):
        return instance.order_items.all().aggregate(
            dry=Coalesce(
                Sum(
                    "original_quantity",
                    filter=Q(item__storage_type=OrderConstants.StorageTypes.DRY),
                ),
                Value(0),
            ),
            chilled=Coalesce(
                Sum(
                    "original_quantity",
                    filter=Q(item__storage_type=OrderConstants.StorageTypes.CHILLED),
                ),
                Value(0),
            ),
            frozen=Coalesce(
                Sum(
                    "original_quantity",
                    filter=Q(item__storage_type=OrderConstants.StorageTypes.FROZEN),
                ),
                Value(0),
            ),
            total=Coalesce(Sum("original_quantity"), Value(0)),
        )

    @property
    def item_count(self):
        return self.order_items.count()

    @property
    def total_item_cbm(self):
        return sum(
            [
                order_item.line_item_cbm if order_item.line_item_cbm else 0
                for order_item in self.order_items.all()
            ]
        )


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    item = models.ForeignKey(ItemMaster, related_name="item_orders", on_delete=models.CASCADE)
    original_quantity = models.PositiveIntegerField(default=1)
    delivered_quantity = models.PositiveIntegerField(default=0)
    total_cases = models.DecimalField(default=1, max_digits=10, decimal_places=2)
    delivered_cases = models.DecimalField(default=1, max_digits=10, decimal_places=2)
    line_item_cbm = models.DecimalField(
        verbose_name="Line Item Volume (cbm)",
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=5,
    )
    line_item_weight = models.DecimalField(
        verbose_name="Line Item Weight (Kg)", blank=True, null=True, max_digits=10, decimal_places=3
    )

    @staticmethod
    def calculate_cbm(item_cbm, quantity):
        return item_cbm * quantity

    @staticmethod
    def calculate_weight(item_weight, quantity):
        return item_weight * quantity

    @classmethod
    def create_order_item(
        cls,
        data,
    ):
        try:
            item = data.get("item")
            quantity = data.get("original_quantity")
            save_to_db = data.pop("save_to_db")
        except Exception:
            pass
        else:
            line_item_weight = OrderItem.calculate_weight(item.weight, quantity)
            line_item_cbm = OrderItem.calculate_cbm(item.cbm, quantity)
            data["line_item_weight"] = line_item_weight
            data["line_item_cbm"] = line_item_cbm
            if save_to_db:
                item = OrderItem.objects.create(**data)
            else:
                item = OrderItem(**data)
            return item

    def __str__(self):
        return f"{self.order.order_id} - {self.item.item_no}"


class OrderStatusLog(BaseModel):
    # Log all synonyms here

    order = models.ForeignKey(to=Order, related_name="logs", on_delete=models.CASCADE)
    status_keyword = models.ForeignKey(
        to=StatusKeyword,
        related_name="status_orders",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    message = models.CharField(max_length=255)
    added_by = models.ForeignKey(
        to=User,
        related_name="order_log",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )


class OrderAttachment(BaseModel):
    order = models.ForeignKey(Order, related_name="attachments", on_delete=models.CASCADE)
    attachment = models.FileField(upload_to=get_order_attachment_path, verbose_name="Attachment")
    attachment_type = models.CharField(choices=ATTACHMENT_TYPE_CHOICES, max_length=50)
    uploaded_by = models.ForeignKey(
        to=User,
        related_name="attachments_uploaded",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.order.reference_number} - {self.attachment_type}"


class CustomerAddress(BaseModel):
    ADDRESS_PREFIX = "ADDR"

    customer_code = models.CharField(max_length=100, verbose_name="Customer Code", unique=True)
    customer_name = models.CharField(max_length=100, verbose_name="Name")
    customer_type = models.CharField(
        verbose_name="Service Type",
        choices=SERVICE_TYPE_CHOICES,
        default=ServiceType.B2C,
        max_length=5,
    )
    contact_number = PhoneNumberField(
        verbose_name="Contact Number",
        blank=True,
        null=True,
    )
    contact_email = models.EmailField(verbose_name="Email ID", blank=True, null=True)
    project = models.ForeignKey(
        to=Project,
        related_name="customer_addresses",
        verbose_name="Project",
        on_delete=models.CASCADE,
    )
    # location => PointField
    address = models.TextField(verbose_name="Address")
    coordinates = models.PointField(blank=True, null=True)
    contact_person = models.CharField(
        verbose_name="Contact Person Name", max_length=100, blank=True, null=True
    )
    remarks = models.TextField(verbose_name="Remarks", blank=True, null=True)
    processing_time = models.PositiveSmallIntegerField(verbose_name="Processing Time", default=5)
    extra_info = models.JSONField(verbose_name="Extra Information", blank=True, null=True)
    email_notification = models.BooleanField(default=False, verbose_name="Email Notification")
    created_by = models.ForeignKey(
        to=User,
        related_name="created_customer_addresses",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    updated_by = models.ForeignKey(
        to=User,
        related_name="updated_customer_addresses",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Customer Address"
        verbose_name_plural = "Customer Addresses"

    def __str__(self):
        return f"{self.address_id} - {self.customer_name} - {self.address} - {self.customer_code}"

    @property
    def address_id(self):
        return f"{self.ADDRESS_PREFIX}, {str(self.id).zfill(2)}"

    @staticmethod
    def clean_customer_name(name: str):
        name = name.replace("&", " and ")
        val = " ".join(name.strip().split())
        return val

    def add_time_slots(self, time_slots: list[dict]):
        for rec in time_slots:
            CustomerAddressTimeSlots.objects.create(
                customer_address=self,
                from_time=rec.get("from_time"),
                to_time=rec.get("to_time"),
            )


class CustomerAddressTimeSlots(BaseModel):
    customer_address = models.ForeignKey(
        to=CustomerAddress, related_name="time_slots", on_delete=models.CASCADE
    )
    from_time = models.TimeField(verbose_name="From Time")
    to_time = models.TimeField(verbose_name="To Time")

    def __str__(self) -> str:
        return f"{self.customer_address} - {self.from_time} - {self.to_time}"
