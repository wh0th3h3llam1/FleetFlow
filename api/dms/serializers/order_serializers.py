import logging
from datetime import datetime, timedelta, date
from django.contrib.gis.geos.point import Point

from django.db.models import Sum, Q
from django.utils import timezone
from drf_extra_fields.geo_fields import PointField
from psycopg2 import IntegrityError
from rest_framework import serializers

from dms.helpers import update_order_details
from dms.models import (
    Order,
    ItemMaster,
    CustomerAddress,
    CustomerAddressTimeSlots,
    Project,
    OrderItem,
    OrderStatusLog,
    Trip,
    Driver,
    Vehicle,
    OrderAttachment,
    Tag,
    Notification,
    UserNotification,
)
from common.choices import (
    STORAGE_TYPE_CHOICES,
    ITEM_UNIT_CHOICES,
    PAYMENT_TYPE_CHOICES,
    ORDER_STATUS_CHOICES,
)
from common.constants import (
    OrderConstants,
    FieldConstants,
    ServiceType,
    NotificationPriority,
    NotificationType,
    NotificationCategory,
    TagType,
)
from core.serializers import DynamicFieldsModelSerializer
from core.validators import no_past_date, PHONE_REGEX
from .common_serializers import ProjectSerializer

logger = logging.getLogger(__name__)


class CustomerAddressTimeSlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddressTimeSlots
        fields = ("from_time", "to_time")


class CustomerAddressSerializer(DynamicFieldsModelSerializer):
    coordinates = PointField(required=False)
    time_slots = CustomerAddressTimeSlotsSerializer(many=True, required=False)
    project = serializers.CharField(required=True)
    projects = serializers.SerializerMethodField()
    from_time = serializers.TimeField(write_only=True, required=False)
    to_time = serializers.TimeField(write_only=True, required=False)
    customer_type = serializers.CharField(required=False, max_length=5)
    customer_code = serializers.CharField(max_length=100)
    tags = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    assigned_tags = serializers.SerializerMethodField()
    assigned_driver_tags = serializers.SerializerMethodField()
    assigned_vehicle_tags = serializers.SerializerMethodField()

    def get_assigned_driver_tags(self, instance):
        return [
            {"tag": customer_tag.tag.tag, "id": customer_tag.tag.id}
            for customer_tag in instance.customer_tags.filter(tag__tag_type=TagType.DRIVER_TAG)
        ]

    def get_assigned_vehicle_tags(self, instance):
        return [
            {"tag": customer_tag.tag.tag, "id": customer_tag.tag.id}
            for customer_tag in instance.customer_tags.filter(tag__tag_type=TagType.VEHICLE_TAG)
        ]

    def get_assigned_tags(self, instance):
        return [
            {"tag": customer_tag.tag.tag, "id": customer_tag.tag.id}
            for customer_tag in instance.customer_tags.all()
        ]

    def get_projects(self, instance):
        projects = ProjectSerializer(
            self.context.get("all_projects"),
            many=True,
            fields=("project_id", "project_name"),
            read_only=True,
        )
        return projects.data

    def validate_project(self, project_id):
        try:
            all_projects = self.context.get("all_projects")
            project = all_projects.get(project_id=project_id)
        except Exception:
            raise serializers.ValidationError(
                f"Project with project_id {project_id} does not exist."
            )
        else:
            return project

    def validate_customer_type(self, customer_type):
        customer_type_mapping = {"b2b": ServiceType.B2B, "b2c": ServiceType.B2C}
        customer = None
        try:
            customer = customer_type_mapping[customer_type.lower()]
        except KeyError:
            raise serializers.ValidationError(
                "Invalid Customer Type. Valid Customer Types are B2B/B2C."
            )
        else:
            return customer

    def validate_tags(self, tags):
        if not tags:
            return ""

        stripped_tags = [tag.strip() for tag in tags.split(",")]
        tag_list = [
            Tag.objects.get_or_create(tag=tag, tag_type=TagType.VEHICLE_TAG)
            for tag in stripped_tags
        ]

        return ",".join(stripped_tags)

    def to_representation(self, instance: CustomerAddress):
        representation = super(CustomerAddressSerializer, self).to_representation(instance=instance)
        if instance.project:
            representation["project"] = instance.project.project_id
            representation["project_name"] = instance.project.project_name
        if not instance.coordinates:
            representation["coordinates"] = {"latitude": "", "longitude": ""}
        return representation

    class Meta:
        model = CustomerAddress
        fields = [
            "customer_code",
            "customer_name",
            "address",
            "customer_type",
            "contact_number",
            "project",
            "contact_email",
            "contact_number",
            "coordinates",
            "contact_person",
            "processing_time",
            "remarks",
            "extra_info",
            "whatsapp_notification",
            "email_notification",
            "id",
            "from_time",
            "to_time",
            "time_slots",
            "projects",
            "tags",
            "assigned_tags",
            "assigned_driver_tags",
            "assigned_vehicle_tags",
        ]
        read_only_fields = ["created", "modified", "id"]

    def validate(self, attrs):
        coordinates = attrs.get("coordinates")
        project = attrs.get("project")
        all_projects = self.context.get("all_projects")
        processing_time = attrs.get("processing_time")
        if not (
            project.serviceable_area
            and project in all_projects.filter(serviceable_area__intersects=coordinates)
        ):
            raise serializers.ValidationError(
                "Coordinates are outside the project serviceable area."
            )

        from_time = attrs.get("from_time")
        to_time = attrs.get("to_time")

        if from_time and to_time:
            if from_time == to_time:
                raise serializers.ValidationError("From time and to time can not be same.")

        time_slots = attrs.get("time_slots", [])
        if time_slots:
            from_time = time_slots[0]["from_time"]
            to_time = time_slots[0]["to_time"]
            if from_time and to_time:
                if from_time == to_time:
                    raise serializers.ValidationError("From time and to time can not be same.")

                duration = datetime.combine(date.min, to_time) - datetime.combine(
                    date.min, from_time
                )
                duration_in_mins = duration.seconds // 60
                if duration_in_mins < processing_time:
                    raise serializers.ValidationError(
                        "Delivery window should be larger than processing time."
                    )
        existing_codes = self.context.get("existing_customer_codes", None)
        if existing_codes:
            customer_code = attrs.get("customer_code")
            if customer_code in existing_codes:
                attrs["exists"] = True
        return attrs

    def create(self, validated_data):
        exists = validated_data.pop("exists", False)
        if not exists:
            tags = validated_data.pop("tags", [])
            # new customer creation
            time_slots = validated_data.pop("time_slots", False)
            from_time = validated_data.pop("from_time", False)
            to_time = validated_data.pop("to_time", False)
            validated_data["created_by"] = self.context.get("request").user
            customer = super(CustomerAddressSerializer, self).create(validated_data)
            if from_time and to_time and not time_slots:
                time_slots = [{"from_time": from_time, "to_time": to_time}]

            if time_slots:
                customer.add_time_slots(time_slots)

            if tags:
                tags = tags.split(",")
                customer.add_tags(tags)

            return customer
        else:
            # allowing bulk update of order.
            customer_code = validated_data.get("customer_code")
            time_slots = validated_data.get("time_slots", False)
            from_time = validated_data.pop("from_time", False)
            to_time = validated_data.pop("to_time", False)
            if from_time and to_time and not time_slots:
                time_slots = [{"from_time": from_time, "to_time": to_time}]
                validated_data["time_slots"] = time_slots
            customer = CustomerAddress.objects.get(customer_code=customer_code)
            return self.update(instance=customer, validated_data=validated_data)

    def update_unassigned_orders(self, request, customer):
        orders = Order.objects.filter(
            status=OrderConstants.OrderStatus.UNASSIGNED, customer_address=customer
        )
        fields_to_be_updated = (
            "pickup_address",
            "drop_address",
            "pickup_point",
            "drop_point",
            "delivery_window_start",
            "delivery_window_end",
            "planned_processing_time",
            "contact_person",
            "customer_name",
            "contact_email",
        )
        for order in orders:
            order.planned_processing_time = customer.processing_time
            order.customer_name = customer.customer_name
            order.contact_person = customer.contact_person
            order.contact_email = customer.contact_email
            time_slot = customer.time_slots.order_by("from_time").first()
            order.delivery_window_start = time_slot.from_time
            order.delivery_window_end = time_slot.to_time
            if order.order_type == OrderConstants.OrderType.DELIVERY:
                order.drop_point = customer.coordinates
                order.drop_address = customer.address
            else:
                order.pickup_point = customer.coordinates
                order.pickup_address = customer.address
        Order.objects.bulk_update(orders, fields=fields_to_be_updated)
        message = (
            f"Order Details for {len(orders)} unassigned orders updated automatically because of change in"
            f" customer details by {request.user.full_name}."
        )
        notification = Notification.objects.create(
            title=f"Order details updated.",
            message=message,
            priority=NotificationPriority.HIGH,
            notification_type=NotificationType.INFO,
            notification_category=NotificationCategory.ORDER,
            expiration_time=timezone.now() + timedelta(days=1),
        )
        UserNotification.objects.create(notification=notification, user=request.user)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        time_slots = validated_data.pop("time_slots", False)
        tags = validated_data.pop("tags", [])
        validated_data["updated_by"] = request.user
        customer = super(CustomerAddressSerializer, self).update(instance, validated_data)
        customer.time_slots.all().delete()
        if time_slots:
            customer.add_time_slots(time_slots)
        self.update_unassigned_orders(request, customer)
        if tags:
            tags = tags.split(",")
        customer.add_tags(tags)
        return customer


class ItemMasterSerializer(serializers.ModelSerializer):
    # storage_type = serializers.ChoiceField(choices=STORAGE_TYPE_CHOICES)
    item_no = serializers.CharField(max_length=20, required=True)
    storage_type = serializers.CharField(max_length=10, required=True)
    unit = serializers.CharField(max_length=20, required=True)
    weight = serializers.DecimalField(max_digits=10, decimal_places=5, min_value=0.00001)
    cbm = serializers.DecimalField(max_digits=10, decimal_places=7)
    height = serializers.DecimalField(
        max_digits=10, decimal_places=5, min_value=0.00001, required=True
    )
    width = serializers.DecimalField(
        max_digits=10, decimal_places=5, min_value=0.00001, required=True
    )
    length = serializers.DecimalField(
        max_digits=10, decimal_places=5, min_value=0.00001, required=True
    )
    case_factor = serializers.DecimalField(
        max_digits=10, decimal_places=5, min_value=0.00001, required=True
    )

    def validate_item_no(self, val):
        existing_item_nos = self.context.get("existing_item_nos")
        if self.instance and val in existing_item_nos and not self.instance.item_no == val:
            raise serializers.ValidationError(f"An item with item no {val} already exists.")
        return val

    def validate_storage_type(self, val):
        for storage_value, storage_key in STORAGE_TYPE_CHOICES:
            if storage_key.lower() == val.lower():
                return storage_value

        valid_choices = ",".join([choice[1] for choice in STORAGE_TYPE_CHOICES])
        raise serializers.ValidationError(
            f"{val} is not a valid choice. Valid choices are : {valid_choices}"
        )

    def validate_unit(self, val):
        for unit_value, unit_key in ITEM_UNIT_CHOICES:
            if unit_key.lower() == val.lower():
                return unit_value

        valid_choices = ",".join([choice[1] for choice in ITEM_UNIT_CHOICES])
        raise serializers.ValidationError(
            f"{val} is not a valid choice. Valid choices are : {valid_choices}"
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["storage_type"] = instance.get_storage_type_display()
        representation["unit"] = instance.get_unit_display()
        return representation

    def validate(self, attrs):
        existing_item_nos = self.context.get("existing_item_nos")
        item_no = attrs.get("item_no")
        if item_no in existing_item_nos:
            attrs["exists"] = True
        return attrs

    class Meta:
        model = ItemMaster
        fields = (
            "item_no",
            "storage_type",
            "weight",
            "cbm",
            "item_description",
            "unit",
            "case_factor",
            "length",
            "width",
            "height",
            "id",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "weight": {
                "error_messages": {"min_value": "Ensure this value is greater than 0.00001"}
            },
            "length": {"error_messages": {"min_value": "Ensure this value is greater than 1"}},
            "height": {
                "error_messages": {"min_value": "Ensure this value is greater than 0.00001"}
            },
            "width": {"error_messages": {"min_value": "Ensure this value is greater than 0.00001"}},
            "cbm": {"error_messages": {"min_value": "Ensure this value is greater than 0.0000001"}},
        }

    def create(self, validated_data):
        if validated_data.pop("exists", False):
            item_no = validated_data.get("item_no")
            existing_item_nos = self.context.get("existing_item_nos")
            instance = ItemMaster.objects.get(id=existing_item_nos.get(item_no))
            instance = super().update(instance=instance, validated_data=validated_data)
        else:
            instance = super().create(validated_data)
        return instance


class BulkCreateOrderSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = []
        order_items = {}
        for attrs in validated_data:
            order_items[attrs["reference_number"]] = attrs.pop("order_items")
            result.append(self.child.create(attrs))
        # result = [self.child.create(attrs) for attrs in validated_data]
        try:
            self.child.Meta.model.objects.bulk_create(result, batch_size=1000)
        except IntegrityError as e:
            raise serializers.ValidationError(e)
        else:
            line_items = []
            all_items = self.context.get("all_items")
            for order in result:
                for line_item in order_items[order.reference_number]:
                    item = all_items.get(item_no=line_item["item_no"])
                    quantity = line_item["quantity"]
                    order_item = order.add_order_line_items(
                        line_item=item, quantity=quantity, save_to_db=False
                    )
                    line_items.append(order_item)
            OrderItem.objects.bulk_create(line_items, batch_size=1000)
        return result


class OrderStatusLogSerializer(serializers.ModelSerializer):

    def to_representation(self, instance: Trip):
        representation = super().to_representation(instance=instance)
        representation["added_by"] = instance.added_by.full_name if instance.added_by else ""
        return representation

    class Meta:
        model = OrderStatusLog
        fields = ("message", "added_by", "created")


class OrderItemSerializer(DynamicFieldsModelSerializer):
    item_unit = serializers.CharField(source="item.unit", read_only=True)
    storage_type = serializers.CharField(source="item.get_storage_type_display", read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.item:
            representation["item"] = "{}-{}".format(
                instance.item.item_no, instance.item.item_description
            )
        return representation

    class Meta:
        model = OrderItem
        fields = (
            "item",
            "original_quantity",
            "delivered_quantity",
            "total_cases",
            "delivered_cases",
            "item_unit",
            "storage_type",
        )


class TripDriverSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, read_only=True, source="user.username")
    contact_number = serializers.CharField(read_only=True, source="user.contact_number")
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Driver
        fields = (
            "id",
            "shift_start",
            "shift_end",
            "service_type",
            "status",
            "username",
            "contact_number",
            "first_name",
            "last_name",
        )
        read_only_fields = (
            "id",
            "shift_start",
            "shift_end",
            "service_type",
            "status",
            "username",
            "contact_number",
            "first_name",
            "last_name",
        )


class TripVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = (
            "vehicle_plate_no",
            "tonnage_capacity",
            "vehicle_make",
            "vehicle_model",
            "vehicle_year",
            "vehicle_cost",
            "mileage",
            "cbm_capacity",
            "fuel_type",
            "status",
            "id",
        )


class OrderTripSerializer(serializers.ModelSerializer):
    driver = TripDriverSerializer(read_only=True)
    vehicle = TripVehicleSerializer(read_only=True)

    class Meta:
        model = Trip
        fields = (
            "reference_number",
            "status",
            "driver",
            "vehicle",
            "id",
            "trip_date",
            "modified",
            "trip_id",
        )
        read_only_fields = (
            "reference_number",
            "status",
            "driver",
            "vehicle",
            "id",
            "trip_date",
            "modified",
            "trip_id",
        )


class TripLoadSheetSerializer(DynamicFieldsModelSerializer):
    delivery_date = serializers.DateField(source="execution_date", label="Delivery Date")
    dry_items = serializers.IntegerField()
    chilled_items = serializers.IntegerField()
    frozen_items = serializers.IntegerField()
    driver_name = serializers.CharField()
    vehicle_number = serializers.CharField()
    total_items = serializers.IntegerField(label="Total Items")
    customer_code = serializers.CharField(source="customer_address.customer_code")
    delivery_location = serializers.CharField(source="address")

    class Meta:
        model = Order
        fields = (
            "delivery_date",
            "driver_name",
            "vehicle_number",
            "reference_number",
            "customer_code",
            "customer_name",
            "delivery_location",
            "frozen_items",
            "chilled_items",
            "dry_items",
            "total_items",
            "invoice_number",
        )


class OrderAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAttachment
        fields = ("id", "order", "attachment", "attachment_type")


class OrderSerializer(DynamicFieldsModelSerializer):
    no_of_items = serializers.SerializerMethodField()
    total_cbm = serializers.SerializerMethodField()
    total_kg = serializers.SerializerMethodField()
    execution_date = serializers.DateField()
    customer_code = serializers.CharField(max_length=100, required=False)
    customer_name = serializers.CharField(max_length=100, required=False)
    address = serializers.CharField(required=False, allow_null=True)
    coordinates = PointField(required=False)
    order_coordinates = serializers.SerializerMethodField()
    processing_time = serializers.IntegerField(default=5, required=False, allow_null=True)
    new_customer = serializers.BooleanField(default=False, write_only=True)
    barcode_scanning = serializers.BooleanField(source="require_barcode_scanning", default=False)
    pod_required = serializers.BooleanField(source="require_proof_of_delivery", default=True)
    whatsapp_notification = serializers.BooleanField(required=False, default=False, write_only=True)
    email_notification = serializers.BooleanField(required=False, default=False, write_only=True)
    items = serializers.ListField(source="get_order_items", read_only=True)
    order_items = serializers.ListField(write_only=True)
    projects = serializers.SerializerMethodField()
    project = serializers.CharField(max_length=255, required=False)
    logs = OrderStatusLogSerializer(many=True, read_only=True)
    trip = OrderTripSerializer(read_only=True)
    driver_name = serializers.SerializerMethodField()
    status_keyword = serializers.SerializerMethodField()
    etc = serializers.DateTimeField(read_only=True)
    updated_on = serializers.DateTimeField(format=FieldConstants.DATE_TIME_FORMAT, read_only=True)
    warehouse_details = serializers.SerializerMethodField()
    assigned_time = serializers.SerializerMethodField()
    picked_up_time = serializers.SerializerMethodField()
    completed_time = serializers.SerializerMethodField()
    failed_time = serializers.SerializerMethodField()
    cancelled_time = serializers.SerializerMethodField()
    total_delivered_items = serializers.SerializerMethodField()
    pod_attachments = serializers.SerializerMethodField()
    actual_delivery_location = serializers.SerializerMethodField()
    total_dry_items = serializers.SerializerMethodField()
    total_chilled_items = serializers.SerializerMethodField()
    total_frozen_items = serializers.SerializerMethodField()
    remarks = serializers.CharField(read_only=True)
    order_attachments = serializers.SerializerMethodField()

    def get_order_attachments(self, instance: Order):
        order_attachments = instance.attachments.filter(
            attachment_type=OrderConstants.AttachmentType.ORDER
        )
        return [
            {
                "url": (
                    self.context["request"].build_absolute_uri(order_attachment.attachment.url)
                    if order_attachment.attachment
                    else None
                ),
                "name": order_attachment.attachment.name.split("/")[-1],
                "id": order_attachment.id,
            }
            for order_attachment in order_attachments
            if order_attachment.attachment
        ]

    def get_order_coordinates(self, instance: Order):
        try:
            if instance.order_type == OrderConstants.OrderType.DELIVERY:
                point = [instance.drop_point.x, instance.drop_point.y]
            else:
                point = [instance.pickup_point.x, instance.pickup_point.y]
        except AttributeError as ae:
            point = list()

        return point

    def get_actual_delivery_location(self, instance: Order):
        location = {"address": None, "coordinates": None, "timestamp": None}
        try:
            ts = None
            address = instance.address()
            coords = instance.delivery_point
            ts = instance.completed_on
            location["timestamp"] = ts.strftime(FieldConstants.DATE_TIME_FORMAT) if ts else None

            if coords:
                location["coordinates"] = [coords.x, coords.y]

        except AttributeError as ae:
            logger.exception(ae)
        except Exception as e:
            logger.exception(e)

        return location

    def get_warehouse_details(self, instance):
        return {
            "address": instance.project.base_address,
            "coordinates": [
                instance.project.base_coordinates.x,
                instance.project.base_coordinates.y,
            ],
        }

    ########## Getters ###############

    def get_status_keyword(self, instance):
        return instance.status_keyword.name if instance.status_keyword else None

    def get_driver_name(self, instance):
        return instance.trip.driver.user.full_name if instance.trip else None

    def get_projects(self, instance):
        projects = self.context.get("all_projects")
        projects = ProjectSerializer(
            projects, many=True, fields=("project_name", "project_id"), read_only=True
        )
        return projects.data

    def get_no_of_items(self, obj):
        return (
            obj.order_items.all()
            .aggregate(total_quantity=Sum("original_quantity"))
            .get("total_quantity")
        )

    def get_total_delivered_items(self, obj):
        return (
            obj.order_items.all()
            .aggregate(total_delivered_items=Sum("delivered_quantity"))
            .get("total_delivered_items")
        )

    def get_total_dry_items(self, obj):
        return (
            obj.order_items.all()
            .aggregate(
                dry_items=Sum(
                    "original_quantity",
                    filter=Q(item__storage_type=OrderConstants.StorageTypes.DRY),
                )
            )
            .get("dry_items")
        )

    def get_total_chilled_items(self, obj):
        return (
            obj.order_items.all()
            .aggregate(
                chilled_items=Sum(
                    "original_quantity",
                    filter=Q(item__storage_type=OrderConstants.StorageTypes.CHILLED),
                )
            )
            .get("chilled_items")
        )

    def get_total_frozen_items(self, obj):
        return (
            obj.order_items.all()
            .aggregate(
                frozen_items=Sum(
                    "original_quantity",
                    filter=Q(item__storage_type=OrderConstants.StorageTypes.FROZEN),
                )
            )
            .get("frozen_items")
        )

    def get_total_cbm(self, obj):
        return obj.order_items.all().aggregate(total_cbm=Sum("line_item_cbm")).get("total_cbm")

    def get_total_kg(self, obj):
        return obj.order_items.all().aggregate(total_kg=Sum("line_item_weight")).get("total_kg")

    def get_assigned_time(self, obj: Order):
        assigend_time = None
        if obj.assigned_on:
            assigend_time = datetime.strftime(obj.assigned_on, FieldConstants.DATE_TIME_FORMAT)
        return assigend_time

    def get_picked_up_time(self, obj: Order):
        # return obj.picked_up_on if obj.picked_up_on else None
        pickup_time = None
        if obj.picked_up_on:
            pickup_time = datetime.strftime(obj.picked_up_on, FieldConstants.DATE_TIME_FORMAT)
        return pickup_time

    def get_completed_time(self, obj: Order):
        completed_time = None
        if obj.completed_on:
            completed_time = datetime.strftime(obj.completed_on, FieldConstants.DATE_TIME_FORMAT)
        return completed_time

    def get_failed_time(self, obj: Order):
        failed_time = None
        if obj.failed_on:
            failed_time = datetime.strftime(obj.failed_on, FieldConstants.DATE_TIME_FORMAT)
        return failed_time

    def get_cancelled_time(self, obj: Order):
        cancelled_time = None
        if obj.cancelled_on:
            cancelled_time = datetime.strftime(obj.cancelled_on, FieldConstants.DATE_TIME_FORMAT)
        return cancelled_time

    def get_pod_attachments(self, obj: Order):
        pod_attachments = obj.attachments.filter(attachment_type="pod")
        return [
            {
                "url": (
                    self.context["request"].build_absolute_uri(order_attachment.attachment.url)
                    if order_attachment.attachment
                    else None
                ),
                "name": order_attachment.attachment.name.split("/")[-1],
            }
            for order_attachment in pod_attachments
        ]

    ######### validations ###############

    def validate_project(self, val):
        if val:
            try:
                project = self.context.get("all_projects").get(project_id=val)
            except Project.DoesNotExist as e:
                raise serializers.ValidationError(f"No project found with project id {val}")
            return project

    def validate_status(self, val):
        if self.instance and val != self.instance.status:
            # unassigned => cancelled
            # assigned => unassigned
            # picked_up => unassigned/successful/failed/partially_delivered
            # enroute => unassigned/successful/failed/partially_delivered
            # successful => failed/partially_delivered
            # failed => successful/partially_delivered
            # partially_delivered => unassigned
            OrderStatuses = OrderConstants.OrderStatus

            if self.instance.status == OrderStatuses.CANCELLED:
                raise serializers.ValidationError("Status of cancelled order can not be changed.")

            StatusMapping = {
                OrderStatuses.UNASSIGNED: [
                    OrderStatuses.CANCELLED,
                ],
                OrderStatuses.ASSIGNED: [OrderStatuses.UNASSIGNED, OrderStatuses.CANCELLED],
                OrderStatuses.PICKED_UP: [
                    OrderStatuses.UNASSIGNED,
                    OrderStatuses.SUCCESSFUL,
                    OrderStatuses.FAILED,
                    OrderStatuses.CANCELLED,
                    OrderStatuses.PARTIAL,
                ],
                OrderStatuses.PARTIAL: [
                    OrderStatuses.UNASSIGNED,
                    OrderStatuses.FAILED,
                    OrderStatuses.SUCCESSFUL,
                ],
                OrderStatuses.SUCCESSFUL: [
                    OrderStatuses.FAILED,
                    OrderStatuses.UNASSIGNED,
                    OrderStatuses.CANCELLED,
                    OrderStatuses.PARTIAL,
                ],
                OrderStatuses.FAILED: [
                    OrderStatuses.SUCCESSFUL,
                    OrderStatuses.UNASSIGNED,
                    OrderStatuses.CANCELLED,
                    OrderStatuses.PARTIAL,
                ],
            }
            valid_choices = StatusMapping.get(self.instance.status)
            if val not in valid_choices:
                valid_choices_list = []
                OrderStatusMapping = dict(ORDER_STATUS_CHOICES)
                for choices in valid_choices:
                    if choices == OrderStatuses.SUCCESSFUL:
                        valid_choices_list.append("Delivered")
                    elif choices == OrderStatuses.FAILED:
                        valid_choices_list.append("Returned")
                    else:
                        valid_choices_list.append(OrderStatusMapping.get(choices))

                error_message = ",".join(valid_choices_list)
                raise serializers.ValidationError(
                    f"Invalid Choice. Valid Choices are : {error_message}"
                )
            else:
                return val
        else:
            return val

    def validate_address(self, val):
        if self.instance and not val:
            raise serializers.ValidationError("Address is required.")
        return val

    def validate_execution_date(self, val):
        if self.instance:
            if (
                val == self.instance.execution_date
                or self.instance.status == OrderConstants.OrderStatus.UNASSIGNED
            ):
                return val
            else:
                raise serializers.ValidationError("Date of planned order can not be changed.")
        return val

    def validate_coordinates(self, val):
        if self.instance and not val:
            raise serializers.ValidationError("Coordinates are required.")
        return val

    def validate(self, attrs):
        request = self.context.get("request")
        if request:
            request_user = request.user
        else:
            request_user = self.context.get("user")
        new_customer = attrs.pop("new_customer", False)
        customer_code = attrs.pop("customer_code", None)
        customer_addresses = self.context.get("all_customer_addresses")
        order_status = attrs.get("status")

        whatsapp_notifications = attrs.pop("whatsapp_notification", False)
        email_notifications = attrs.pop("email_notification", False)
        if self.instance:
            address = attrs.pop("address")
            coordinates = attrs.pop("coordinates")
            order_type = attrs.get("order_type")
            project = attrs.get("project")
            if (
                order_status != self.instance.status
                and order_status == OrderConstants.OrderStatus.CANCELLED
                and not attrs.get("cancellation_remarks")
            ):
                raise serializers.ValidationError("Please provide cancellation remarks.")

            if order_type == OrderConstants.OrderType.DELIVERY:
                attrs["drop_address"] = address
                attrs["drop_point"] = coordinates
                attrs["pickup_address"] = project.base_address
                attrs["pickup_point"] = project.base_coordinates
            else:
                attrs["pickup_address"] = address
                attrs["pickup_point"] = coordinates
                attrs["drop_address"] = project.base_address
                attrs["drop_point"] = project.base_coordinates
        else:
            if customer_code and not new_customer:
                try:
                    customer_addr = customer_addresses.get(customer_code=customer_code)
                    address = attrs.pop("address", None)
                    processing_time = attrs.pop("processing_time", None)
                    # whatsapp_notification = attrs.pop("whatsapp_notification", False)
                    # email_notification = attrs.pop("email_notification", False)
                except CustomerAddress.DoesNotExist as e:
                    raise serializers.ValidationError("Customer code does not exist.")
                except Exception as e:
                    logger.exception(e)
                else:
                    attrs["customer_address"] = customer_addr
                    attrs["customer_name"] = customer_addr.customer_name
                    attrs["contact_email"] = attrs.pop("contact_email", customer_addr.contact_email)
                    attrs["contact_person"] = attrs.pop(
                        "contact_person", customer_addr.contact_person
                    )
                    attrs["contact_number"] = attrs.pop(
                        "contact_number", customer_addr.contact_number
                    )
                    attrs["service_type"] = attrs.pop("customer_type", customer_addr.customer_type)
                    attrs["order_type"] = OrderConstants.OrderType.DELIVERY
                    if not attrs.get("delivery_window_start"):
                        time_slot = customer_addr.time_slots.all().order_by("from_time").first()
                        if time_slot:
                            attrs["delivery_window_start"] = time_slot.from_time
                            attrs["delivery_window_end"] = time_slot.to_time
                    attrs["project"] = customer_addr.project
                    if attrs.get("order_type") == OrderConstants.OrderType.DELIVERY:
                        attrs["pickup_address"] = customer_addr.project.base_address
                        attrs["pickup_point"] = customer_addr.project.base_coordinates
                        attrs["drop_point"] = customer_addr.coordinates
                        attrs["drop_address"] = customer_addr.address
                    else:
                        attrs["drop_point"] = customer_addr.project.base_coordinates
                        attrs["drop_address"] = customer_addr.project.base_address
                        attrs["pickup_point"] = customer_addr.coordinates
                        attrs["pickup_address"] = customer_addr.address
                    attrs["planned_processing_time"] = customer_addr.processing_time
                    attrs["order_remarks"] = customer_addr.remarks
                    # attrs["whatsapp_notification"] = customer_addr.whatsapp_notification
                    # attrs["email_notification"] = customer_addr.email_notification
            elif customer_code and new_customer:
                project = attrs.get("project")
                customer_name = attrs.get("customer_name")
                address = attrs.pop("address", None)
                contact_person = attrs.get("contact_person")
                contact_number = attrs.get("contact_number")
                contact_email = attrs.get("contact_email")
                coordinates = attrs.pop("coordinates", None)
                processing_time = attrs.pop("processing_time", 5)
                missing_fields = []
                if not customer_name:
                    missing_fields.append("Customer Name")
                if not address:
                    missing_fields.append("Address")
                if not contact_number:
                    missing_fields.append("Contact Number")
                if not contact_person:
                    missing_fields.append("Contact Person")
                if not project:
                    missing_fields.append("Project")
                if not coordinates:
                    missing_fields.append("Coordinates")
                if missing_fields:
                    missing_fields = ",".join(missing_fields)
                    raise serializers.ValidationError(
                        f"Following fields are required : {missing_fields}"
                    )
                else:
                    attrs["customer_address_details"] = {
                        "project": project.project_id,
                        "address": address,
                        "customer_name": customer_name,
                        "contact_number": contact_number,
                        "contact_email": contact_email,
                        "contact_person": contact_person,
                        "customer_code": customer_code,
                        "processing_time": processing_time,
                        "whatsapp_notification": whatsapp_notifications,
                        "email_notification": email_notifications,
                        "coordinates": {"latitude": coordinates.y, "longitude": coordinates.x},
                        "from_time": attrs.get("delivery_window_start"),
                        "to_time": attrs.get("delivery_window_end"),
                    }
                    customer_address = CustomerAddressSerializer(
                        data=attrs["customer_address_details"], context=self.context
                    )
                    if not customer_address.is_valid(raise_exception=False):
                        logger.exception(customer_address.errors)
                        err_msg = str(list(customer_address.errors.values())[0][0])
                        raise serializers.ValidationError(f"{err_msg}")
                    else:
                        order_type = attrs.get("order_type")
                        if order_type == OrderConstants.OrderType.DELIVERY:
                            attrs["drop_address"] = address
                            attrs["drop_point"] = coordinates
                            attrs["pickup_address"] = project.base_address
                            attrs["pickup_point"] = project.base_coordinates
                        else:
                            attrs["pickup_address"] = address
                            attrs["pickup_point"] = coordinates
                            attrs["drop_address"] = project.base_address
                            attrs["drop_point"] = project.base_coordinates
                        attrs["planned_processing_time"] = processing_time
            attrs["created_by"] = request_user
        attrs["updated_by"] = request_user
        return attrs

    def validate_order_items(self, order_items):
        all_items = self.context.get("all_items")
        if all_items and order_items:
            non_existent_item_nos = []
            for order_item in order_items:
                try:
                    all_items.get(item_no=order_item["item_no"])
                except ItemMaster.DoesNotExist as e:
                    non_existent_item_nos.append(order_item["item_no"])
            if non_existent_item_nos:
                non_existent_item_nos = ",".join(non_existent_item_nos)
                raise serializers.ValidationError(
                    f"Non existent item numbers : {non_existent_item_nos}"
                )
        return order_items

    def create(self, validated_data):
        line_items_data = validated_data.pop("order_items", None)
        if isinstance(self._kwargs["data"], dict):
            customer_address_details = validated_data.pop("customer_address_details", None)
            if customer_address_details:
                customer_address_serializer = CustomerAddressSerializer(
                    data=customer_address_details, context=self.context
                )
                if customer_address_serializer.is_valid(raise_exception=False):
                    validated_data["customer_address"] = customer_address_serializer.save()
            order = super(OrderSerializer, self).create(validated_data)
            if line_items_data:
                all_items = self.context.get("all_items")
                for item in line_items_data:
                    line_item = all_items.get(item_no=item["item_no"])
                    order.add_order_line_items(line_item=line_item, quantity=int(item["quantity"]))
        else:
            order = Order(**validated_data)
        return order

    def update(self, instance, validated_data):
        line_items_data = validated_data.pop("order_items", None)
        status = validated_data.get("status", None)
        instance = update_order_details(instance, status)
        order = super(OrderSerializer, self).update(instance, validated_data)
        if line_items_data:
            all_items = self.context.get("all_items")
            order.order_items.all().delete()
            for item in line_items_data:
                line_item = all_items.get(item_no=item["item_no"])
                if order.status in [
                    OrderConstants.OrderStatus.SUCCESSFUL,
                    OrderConstants.OrderStatus.UNASSIGNED,
                    OrderConstants.OrderStatus.ASSIGNED,
                    OrderConstants.OrderStatus.PICKED_UP,
                ]:
                    item_update_data = {
                        "line_item": line_item,
                        "quantity": int(item["quantity"]),
                        "delivered_quantity": int(item["quantity"]),
                    }
                elif order.status in [
                    OrderConstants.OrderStatus.FAILED,
                    OrderConstants.OrderStatus.CANCELLED,
                ]:
                    item_update_data = {
                        "line_item": line_item,
                        "quantity": int(item["quantity"]),
                        "delivered_quantity": 0,
                    }
                else:
                    item_update_data = {
                        "line_item": line_item,
                        "quantity": int(item["quantity"]),
                        "delivered_quantity": item.get("delivered_quantity"),
                    }

                order.add_order_line_items(**item_update_data)
        return order

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.project:
            representation["project"] = instance.project.project_id
            representation["project_name"] = instance.project.project_name
        return representation

    class Meta:
        model = Order
        fields = (
            "order_id",
            "status",
            "order_items",
            "execution_date",
            "order_type",
            "order_remarks",
            "order_value",
            "instructions",
            "payment_type",
            "barcode_scanning",
            "reference_number",
            "items",
            "id",
            "pickup_address",
            "drop_address",
            "pod_required",
            "customer_notifications",
            "delivery_window_start",
            "delivery_window_end",
            "project",
            "projects",
            "no_of_items",
            "total_cbm",
            "total_kg",
            "sequence_number",
            "attempt_number",
            "trip",
            "pickup_point",
            "drop_point",
            "invoice_number",
            "payment_collected",
            "logs",
            "new_customer",
            "planned_processing_time",
            "payment_type",
            "assigned_time",
            "picked_up_time",
            "completed_time",
            "failed_time",
            "cancelled_time",
            "total_delivered_items",
            "whatsapp_notification",
            "email_notification",
            "processing_time",
            "customer_code",
            "customer_name",
            "contact_email",
            "contact_person",
            "contact_number",
            "service_type",
            "coordinates",
            "address",
            "driver_name",
            "status_keyword",
            "updated_on",
            "etc",
            "warehouse_details",
            "cancellation_remarks",
            "cod_remarks",
            "pod_attachments",
            "actual_delivery_location",
            "total_dry_items",
            "total_chilled_items",
            "total_frozen_items",
            "order_coordinates",
            "remarks",
            "order_attachments",
        )
        read_only_fields = [
            "id",
            "created",
            "modified",
            "created_by",
            "updated_by",
            "no_of_items",
            "pickup_point",
            "drop_point",
            "total_cbm",
            "logs",
            "total_kg",
            "attempt_number",
            "trip",
            "sequence_number",
            "planned_processing_time",
            "pickup_address",
            "drop_address",
            "projects",
            "total_dry_items",
            "total_chilled_items",
            "total_frozen_items",
        ]
        list_serializer_class = BulkCreateOrderSerializer


class BulkUploadOrderItemSerializer(serializers.Serializer):
    reference_number = serializers.CharField(max_length=200)
    item_no = serializers.CharField(max_length=20)
    customer_code = serializers.CharField(max_length=100)
    delivery_date = serializers.DateField(
        validators=[
            no_past_date,
        ],
        input_formats=FieldConstants.MULTIPLE_DATE_FORMATS,
    )
    quantity = serializers.IntegerField(min_value=1)

    def validate_item_no(self, val):
        item_nos = self.context.get("item_nos")
        if val not in item_nos:
            raise serializers.ValidationError(f"Item Number {val} does not exist.")
        return val

    def validate_customer_code(self, val):
        customer_codes = self.context.get("customer_codes")
        if val not in customer_codes:
            raise serializers.ValidationError(f"Customer code {val} does not exist.")
        return val

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class BulkUpdateOrderSerializer(serializers.Serializer):
    reference_number = serializers.CharField(max_length=200)
    invoice_number = serializers.CharField(max_length=200, required=False)
    execution_date = serializers.DateField(input_formats=FieldConstants.MULTIPLE_DATE_FORMATS)
    payment_type = serializers.CharField(max_length=200, required=False)
    # require_proof_of_delivery = serializers.BooleanField(required=False)
    require_proof_of_delivery = serializers.CharField(required=False)
    order_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    from_time = serializers.TimeField(required=False)
    to_time = serializers.TimeField(required=False)

    def validate(self, attrs):

        TRUE_VALUES = {
            "t",
            "T",
            "y",
            "Y",
            "yes",
            "Yes",
            "YES",
            "true",
            "True",
            "TRUE",
            "on",
            "On",
            "ON",
            "1",
            1,
            True,
        }
        FALSE_VALUES = {
            "f",
            "F",
            "n",
            "N",
            "no",
            "No",
            "NO",
            "false",
            "False",
            "FALSE",
            "off",
            "Off",
            "OFF",
            "0",
            0,
            0.0,
            False,
        }
        payment_type = attrs.get("payment_type", None)
        require_pod = attrs.get("require_proof_of_delivery", None)
        order_value = attrs.get("order_value", None)

        error_dict = dict()
        if payment_type == OrderConstants.PaymentMethod.COD and order_value is None:
            error_dict.update({"order_value": "Order Value is Required if Payment type is COD"})

        if require_pod is not None:
            if require_pod in TRUE_VALUES:
                attrs["require_proof_of_delivery"] = True
            elif require_pod in FALSE_VALUES:
                attrs["require_proof_of_delivery"] = False
            else:
                error_dict.update(
                    {"require_proof_of_delivery": "Invalid Choice. Valid choices are yes/no."}
                )

        if error_dict != dict():
            raise serializers.ValidationError(error_dict)
        return attrs

    def validate_payment_type(self, payment_type):
        for key, value in PAYMENT_TYPE_CHOICES:
            if key.lower() == payment_type.lower():
                return key

        raise serializers.ValidationError(
            f"Invalid Payment Type. Choices are {', '.join([i[0].title() for i in PAYMENT_TYPE_CHOICES])}"
        )

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class BulkUploadB2COrderSerializer(serializers.Serializer):
    reference_number = serializers.CharField(max_length=200)
    item_no = serializers.CharField(max_length=20)
    delivery_date = serializers.DateField(
        validators=[
            no_past_date,
        ],
        input_formats=FieldConstants.MULTIPLE_DATE_FORMATS,
    )
    quantity = serializers.IntegerField(min_value=1)
    customer_number = serializers.CharField(required=True, validators=[PHONE_REGEX], min_length=8)
    customer_name = serializers.CharField(required=False)
    customer_type = serializers.CharField(required=True, max_length=3)
    contact_email = serializers.EmailField(required=True)
    project_id = serializers.CharField(required=True)
    processing_time = serializers.IntegerField(required=False, default=10)
    address = serializers.CharField(required=True)
    latitude = serializers.FloatField(required=True)
    longitude = serializers.FloatField(required=True)
    from_time = serializers.TimeField(required=False, input_formats=[FieldConstants.TIME_FORMAT])
    to_time = serializers.TimeField(required=False, input_formats=[FieldConstants.TIME_FORMAT])
    whatsapp_notification = serializers.BooleanField(required=False, default=True)
    email_notification = serializers.BooleanField(required=False, default=True)
    tags = serializers.CharField(required=False)

    def validate_item_no(self, item_no):
        item_no_list = self.context.get("item_no_list")
        if item_no not in item_no_list:
            raise serializers.ValidationError(f"Item Number {item_no} does not exist.")
        return item_no

    def validate_project_id(self, project_id):
        try:
            all_projects = self.context.get("all_projects")
            project = all_projects.get(project_id=project_id)
        except Exception as e:
            raise serializers.ValidationError(
                f"Project with project_id {project_id} does not exist."
            )
        return project

    def validate_customer_number(self, value):
        if "+" in value:
            special_char_seperated_value = value.split("+")[1]
            validated_num = "".join(special_char_seperated_value.split(" "))
        else:
            validated_num = "".join(value.split(" "))
        return validated_num

    def validate_customer_type(self, customer_type):
        if customer_type not in [ServiceType.B2B, ServiceType.B2C]:
            raise serializers.ValidationError("Invalid Choice. Valid choice is B2B/B2C")
        return customer_type

    def validate(self, attrs):
        project = attrs.get("project_id")
        latitude = attrs.get("latitude", None)
        longitude = attrs.get("longitude", None)
        all_projects = self.context.get("all_projects")
        tags = attrs.get("tags", [])
        coordinates = Point(longitude, latitude)

        if not (
            project.serviceable_area
            and project in all_projects.filter(serviceable_area__intersects=coordinates)
        ):
            raise serializers.ValidationError(
                {"latitude": "Customer Coordinates are outside the project serviceable area."}
            )

        customer_number = attrs.get("customer_number")
        customer_type = attrs.get("customer_type")

        customer = CustomerAddress.objects.filter(
            contact_number=customer_number, customer_type=customer_type
        )
        if not customer:
            customer_name = attrs.get("customer_name")
            contact_email = attrs.get("contact_email")
            processing_time = attrs.get("processing_time")
            address = attrs.get("address")

            from_time = attrs.get("from_time")
            to_time = attrs.get("to_time")
            time_slots = [{"from_time": from_time, "to_time": to_time}]

            whatsapp_notification = attrs.get("whatsapp_notification", True)
            email_notification = attrs.get("email_notification", True)

            customer_code = f"{customer_type}-{customer_number}"

            validate_customer = {
                "customer_code": customer_code,
                "customer_name": customer_name,
                "customer_type": customer_type,
                "contact_number": customer_number,
                "contact_email": contact_email,
                "project": project.project_id,
                "processing_time": processing_time,
                "address": address,
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "time_slots": time_slots,
                "whatsapp_notification": whatsapp_notification,
                "email_notification": email_notification,
                "tags": tags,
            }

            customer_context = {
                "all_projects": all_projects,
                "request": self.context.get("request"),
            }
            customer_serializer = CustomerAddressSerializer(
                data=validate_customer, context=customer_context
            )

            if customer_serializer.is_valid():
                customer = customer_serializer.save()
            else:
                raise serializers.ValidationError(customer_serializer.errors)
        return attrs


class OrderListSerializer(serializers.ModelSerializer):
    project = serializers.CharField(source="project.project_id")
    trip_reference_number = serializers.SerializerMethodField()
    driver = serializers.SerializerMethodField()
    vehicle = serializers.SerializerMethodField()
    zone = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "reference_number",
            "address",
            "project",
            "delivery_window_start",
            "delivery_window_end",
            "delivery_window",
            "driver",
            "trip_reference_number",
            "vehicle",
            "zone",
            "status",
            "unassigned_on",
            "assigned_on",
            "picked_up_on",
            "completed_on",
            "failed_on",
        ]

    def get_trip_reference_number(self, instance):
        return instance.trip.reference_number if instance.trip else "N/A"

    def get_driver(self, instance):
        return instance.trip.driver.user.username if instance.trip else "N/A"

    def get_vehicle(self, instance):
        return instance.trip.vehicle.vehicle_plate_no if instance.trip else "N/A"

    def get_zone(self, instance):
        return instance.trip.driver.zone.zone_name if instance.trip else "N/A"
