import logging
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from drf_extra_fields.geo_fields import PointField
from rest_framework import serializers
from rest_framework.reverse import reverse

from core.models import DashUser, StatusKeyword
from core.models import Notification, UserNotification
from dms.models import (Driver, Trip, Order, OrderItem,
                        OrderAttachment, DriverExpense, Vehicle, VehicleDocument, DriverDocument,
                        TripChatLog, TripMetrics, TelemetryConfig, ProjectUser)
from lib.constants import StatusConstants, OrderConstants, TripStatus, DriverStatus, TripStatusLogs, \
    NotificationPriority, NotificationType, NotificationCategory
from lib.serializers import DynamicFieldsModelSerializer

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = DashUser
        fields = ("username", "password", "contact_number",
                  "email", "profile_image")


class TelemetryConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryConfig
        fields = ("sample_interval", "transmission_interval")


class DriverAppSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Driver
        fields = (
            "user", "license_number", "license_expiry", "license_image",
            "nationality", "national_id_expiry", "national_id_image",
            "visa_number", "visa_expiry", "visa_image", "shift_start",
            "shift_end", "status", "last_seen_on", "vehicle_assigned",
            "project", "service_type", "id")
        read_only_fields = ["created", "modified", "last_seen_on", "id"]

    def create(self, validated_data):
        user_data = validated_data.pop("user", None)
        added_by = self.context.get("request").user
        if user_data:
            password = user_data.pop("password")
            user = DashUser.objects.create(**user_data)
            user.set_password(password)
            validated_data["user"] = user
        validated_data["added_by"] = added_by
        return super(DriverAppSerializer, self).create(validated_data)

    def update(self, obj, validated_data):
        user_data = validated_data.pop("user", None)
        added_by = self.context.get("request").user
        if user_data:
            user = DashUser.objects.filter(id=obj.user.id)
            password = user_data.pop("password")
            user.update(**user_data)
            user.first().set_password(password)
        return super(DriverAppSerializer, self).update(obj, validated_data)


class DriverStatusUpdateSerializer(serializers.ModelSerializer):
    break_reason = serializers.SlugRelatedField(
        slug_field='id', queryset=StatusKeyword.objects.all(),
        write_only=True, required=False)

    class Meta:
        model = Driver
        fields = ("status", "break_reason")
        read_only_fields = ["created", "modified", "last_seen_on", "id",
                            "license_number", "license_expiry", "license_image",
                            "nationality", "national_id_expiry", "national_id_image",
                            "visa_number", "visa_expiry", "visa_image", "shift_start",
                            "shift_end", "vehicle_assigned", "service_type"]

    def validate(self, data):
        obj = self.instance
        try:
            current_trip = obj.current_trip
        except:
            current_trip = False
        break_reason = data.pop("break_reason", False)
        status = data.get("status")
        if current_trip and status:
            existing_trip_status = current_trip.status
            if status == DriverStatus.ON_BREAK:
                current_trip.add_driver_break(obj, break_reason)
                current_trip.status = TripStatus.PAUSED
                # current_trip.add_trip_log(TripStatusLogs.on_break)
            elif status == DriverStatus.OFF_DUTY:
                current_trip.status = TripStatus.PAUSED
                obj.add_attendance_log(DriverStatus.OFF_DUTY)
                current_trip.add_trip_log(TripStatusLogs.off_duty)
            elif obj.status == DriverStatus.OFF_DUTY and status == DriverStatus.ON_DUTY:
                current_trip.status = TripStatus.ACTIVE
                obj.add_attendance_log(DriverStatus.ON_DUTY)
                current_trip.add_trip_log(TripStatusLogs.on_duty)
            elif obj.status == DriverStatus.ON_BREAK and status == DriverStatus.ON_DUTY:
                current_trip.status = TripStatus.ACTIVE
                current_trip.complete_driver_break(obj, None)
                current_trip.add_trip_log(TripStatusLogs.break_complete)
            current_trip.save()
            # msg = "Trip status changed to %s from %s by %s".format(
            # current_trip.status, existing_trip_status, obj.user.username)
        return data

    def update(self, obj, validated_data):
        return super(DriverStatusUpdateSerializer, self).update(obj, validated_data)


class DriverVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ("vehicle_plate_no", "vehicle_image", "tonnage_capacity", "vehicle_make", "vehicle_model",
                  "vehicle_year", "vehicle_cost", "mileage", "cbm_capacity", "fuel_type", "rc_number",
                  "rc_expiry_date", "rc_image", "insurance_policy_number", "insurance_expiry_date",
                  "insurance_type", "insurance_image", "permits")
        read_only_fields = ["created", "modified", "id"]


class DriverDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vehicle_assigned = DriverVehicleSerializer(read_only=True)
    driver_trip = serializers.SerializerMethodField(read_only=True)
    vehicle_plate_no = serializers.SerializerMethodField(read_only=True)
    breaks_list = serializers.SerializerMethodField(read_only=True)
    vehicle_documents = serializers.SerializerMethodField(read_only=True)
    driver_documents = serializers.SerializerMethodField(read_only=True)

    def get_vehicle_documents(self, obj):
        if obj.vehicle_assigned:
            documents = VehicleDocument.objects.filter(vehicle__id=obj.vehicle_assigned.id).values('document',
                                                                                                   'document_type',
                                                                                                   'description')
        else:
            documents = list()
        return documents

    def get_driver_documents(self, obj):
        documents = DriverDocument.objects.filter(driver__id=obj.id).values('document', 'document_type', 'description')
        return documents

    def get_vehicle_plate_no(self, obj):
        return obj.vehicle_assigned.vehicle_plate_no if obj.vehicle_assigned else None

    def get_driver_trip(self, obj):
        try:
            trip = obj.current_trip
        except (Trip.DoesNotExist, AttributeError) as e:
            trip = obj.upcoming_trip

        if trip:
            return {
                "id": trip.id,
                "reference_number": trip.reference_number,
                "status": trip.status,
                "order_count": trip.trip_orders.count(),
                "planned_distance": trip.planned_distance if trip.planned_distance else 'N/A',
                "trip_id": trip.trip_id,
                "trip_date": trip.trip_date.strftime("%d-%m-%Y") if trip.trip_date else "",
                "trip_detail": reverse('driver-trip-detail', kwargs={'trip_id': trip.trip_id}),
                "trip_partitions": trip.trip_order_partition(),
                "trip_start_km" : trip.trip_start_km,
                "trip_end_km": trip.trip_end_km,
            }
        return None

    def get_breaks_list(self, obj):
        break_status_keywords = StatusKeyword.objects.filter(
            status_category=StatusConstants.DRIVER).values("id", "name")
        return break_status_keywords

    class Meta:
        model = Driver
        fields = ["user", "status", "shift_start", "shift_end", "vehicle_plate_no",
                  "driver_trip", "breaks_list", "id", "vehicle_assigned",
                  "license_number", "license_expiry", "license_image", "nationality",
                  "national_id_expiry", "national_id_image", "visa_number",
                  "visa_expiry", "visa_image", "health_card_number", "health_card_expiry",
                  "vehicle_documents", "driver_documents"]
        extra_kwargs = {
            "shift_start": {"format": "%H:%M", 'input_formats': ['%I:%M %p', '%H:%M']},
            "shift_end": {"format": "%H:%M", 'input_formats': ['%I:%M %p', '%H:%M']}
        }


class DriverAppOrderItemSerializer(serializers.ModelSerializer):
    item_detail_url = serializers.SerializerMethodField()
    case_factor = serializers.CharField(source='item.case_factor', read_only=True)
    storage_type = serializers.CharField(source='item.get_storage_type_display', read_only=True)
    cbm = serializers.CharField(source='item.cbm', read_only=True)
    unit = serializers.CharField(source='item.get_unit_display', read_only=True)

    def get_item_detail_url(self, obj):
        return reverse('driver-order-item-detail', kwargs={'pk': obj.pk})

    def validate_delivered_quantity(self, delivered_quantity):
        if delivered_quantity > self.instance.original_quantity:
            raise serializers.ValidationError(
                "Ensure this value is less than or equal to ordered quantity.")
        elif delivered_quantity < 0:
            raise serializers.ValidationError(
                "Ensure this value is greater than 0.")
        return delivered_quantity

    def to_representation(self, instance: OrderItem):
        representation = super().to_representation(instance=instance)
        representation["item"] = instance.item.item_description
        return representation

    class Meta:
        model = OrderItem
        fields = ("item", "original_quantity", "delivered_quantity",
                  "id", "item_detail_url", "case_factor", "storage_type",
                  "cbm", "unit")
        read_only_fields = ("item", "original_quantity", "id", "item_detail_url")


class OrderAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAttachment
        fields = ("attachment", "attachment_type")


class DriverTripMetricsSerializer(serializers.ModelSerializer):
    coordinates = PointField()

    def create(self, validated_data):
        driver = self.context.get("request").user.driver
        validated_data["driver"] = driver
        trip = None
        try:
            trip = driver.current_trip
            validated_data["trip"] = trip
        except:
            trip = driver.upcoming_trip
            validated_data["trip"] = trip
        if not trip:
            logger.info(f"No active or scheduled trip found for driver: {driver.user.username}")
        last_metric = super(DriverTripMetricsSerializer, self).create(validated_data)
        if trip:
            trip.last_driver_location = last_metric
            trip.save()
        return last_metric

    class Meta:
        model = TripMetrics
        fields = ("coordinates", "battery", "speed", "timestamp")


class DriverAppOrderSerializer(DynamicFieldsModelSerializer):
    no_of_items = serializers.SerializerMethodField()
    order_detail_url = serializers.SerializerMethodField()
    order_items = DriverAppOrderItemSerializer(many=True, read_only=True)
    pickup_point = serializers.SerializerMethodField()
    drop_point = serializers.SerializerMethodField()
    attachments = OrderAttachmentsSerializer(many=True, read_only=True)
    status_messages = serializers.SerializerMethodField()
    status_keyword = serializers.CharField(required=False)
    delivery_point = PointField(required=False)
    item_partitions = serializers.SerializerMethodField()
    is_pod_uploaded = serializers.SerializerMethodField()
    cancellation_remarks = serializers.CharField(source='driver_remarks')
    update_customer_location = serializers.SerializerMethodField()

    def get_update_customer_location(self, instance: Order):
        return instance.customer_address.project.update_customer_location

    def get_is_pod_uploaded(self, instance: Order):
        return instance.attachments.filter(attachment_type=OrderConstants.AttachmentType.POD).exists()

    def get_no_of_items(self, obj):
        return obj.order_items.all().aggregate(
            total_quantity=Sum('original_quantity')).get("total_quantity")

    def get_item_partitions(self, obj):
        dry_items = obj.order_items.filter(
            item__storage_type="D").aggregate(item_quantity=Sum('original_quantity')).get("item_quantity")
        chilled_items = obj.order_items.filter(
            item__storage_type="C").aggregate(item_quantity=Sum('original_quantity')).get("item_quantity")
        frozen_items = obj.order_items.filter(
            item__storage_type="F").aggregate(item_quantity=Sum('original_quantity')).get("item_quantity")
        return {"dry_items": dry_items, "chilled_items": chilled_items, "frozen_items": frozen_items}

    def get_order_detail_url(self, obj):
        return reverse('driver-orders-detail', kwargs={'pk': obj.pk})

    def get_drop_point(self, obj):
        return f'{float(obj.drop_point.y)},{float(obj.drop_point.x)}'

    def get_pickup_point(self, obj):
        return f'{float(obj.pickup_point.y)},{float(obj.pickup_point.x)}'

    def get_status_messages(self, obj):
        status_messages = {}
        all_statuses = StatusKeyword.objects.filter(
            status_category=StatusConstants.ORDER)
        if obj.order_type == OrderConstants.OrderType.PICK_UP:
            success_status = OrderConstants.OrderStatus.PICKED_UP
            failed_status = OrderConstants.OrderStatus.FAILED
        else:
            success_status = OrderConstants.OrderStatus.SUCCESSFUL
            failed_status = OrderConstants.OrderStatus.FAILED

        status_messages.update({
            "successful": list(
                all_statuses.filter(keyword=success_status).values_list("name", flat=True)),
        })

        if failed_status:
            status_messages.update({"failed": list(
                all_statuses.filter(keyword=failed_status).values_list("name", flat=True))})

        return status_messages

    def validate_status_keyword(self, status_keyword):
        try:
            status_keyword = StatusKeyword.objects.get(name=status_keyword)
            return status_keyword
        except Exception as e:
            raise serializers.ValidationError("Reason is not valid choice")

    class Meta:
        model = Order
        fields = (
            "id","order_id", "status", "customer_name", "contact_email",
            "contact_person", "execution_date", "order_type",
            "order_value", "drop_address", "order_detail_url",
            "contact_number", "reference_number", "no_of_items",
            "order_items", "pickup_point", "drop_point", "attachments",
            "delivery_window_start", "delivery_window_end", "instructions",
            "payment_type", "require_barcode_scanning", "require_proof_of_delivery", "cod_remarks",
            "order_remarks", "payment_collected", "processing_time", 'is_pod_uploaded',
            "cancellation_remarks", "cancelled_on", "pickup_address", "driver_remarks",
            "status_messages", "status_keyword","update_customer_location", "delivery_point", "item_partitions",

        )
        read_only_fields = [
            "id", "attachments", "order_id", "customer_name", "contact_email",
            "contact_person", "execution_date", "order_type",
            "order_value", "drop_address", "order_detail_url",
            "contact_number", "reference_number", "no_of_items",
            "order_items", "pickup_point", "drop_point", "attachments",
            "delivery_window_start", "delivery_window_end", "instructions",
            "payment_type", "require_barcode_scanning", "require_proof_of_delivery",
            "order_remarks", "cancelled_on", "pickup_address",
            "status_messages",
        ]

    def to_representation(self, instance: Order):
        representation = super().to_representation(instance=instance)
        representation["status_keyword"] = instance.status_keyword.name if instance.status_keyword else None
        # if instance.status == OrderConstants.OrderStatus.PARTIAL:
        #     representation["status"] = OrderConstants.OrderStatus.SUCCESSFUL
        return representation


class PODUploadSerializer(serializers.Serializer):
    attachment = serializers.FileField(required=True)


class UpdateOrderAddressSerializer(serializers.ModelSerializer):
    pickup_point = serializers.SerializerMethodField()
    drop_point = serializers.SerializerMethodField()
    update_drop_point = PointField(write_only=True)
    def get_drop_point(self, obj):
        return f'{float(obj.drop_point.y)},{float(obj.drop_point.x)}'

    def get_pickup_point(self, obj):
        return f'{float(obj.pickup_point.y)},{float(obj.pickup_point.x)}'

    class Meta:
        model = Order
        fields = ('id', "order_id", "drop_point", "pickup_point", "update_drop_point")

    def update(self, instance, attrs):
        # latitude = attrs.get('latitude')
        # longitude = attrs.get('longitude')
        updated_point = attrs.get('update_drop_point')
        order = self.instance
        customer = order.customer_address
        customer.coordinates = updated_point
        if order.order_type == OrderConstants.OrderType.DELIVERY:
            order.drop_point = updated_point
        else:
            order.pickup_point = updated_point
        order.save()
        customer.save()
        return order

class TripOrderSerializer(serializers.ModelSerializer):
    no_of_items = serializers.SerializerMethodField()
    order_detail_url = serializers.SerializerMethodField()
    pickup_point = serializers.SerializerMethodField()
    drop_point = serializers.SerializerMethodField()

    def get_no_of_items(self, obj):
        return obj.order_items.all().aggregate(
            total_quantity=Sum('original_quantity')).get("total_quantity")

    def get_order_detail_url(self, obj):
        return reverse('driver-orders-detail', kwargs={'pk': obj.pk})

    def get_drop_point(self, obj):
        return f'{float(obj.drop_point.y)},{float(obj.drop_point.x)}'

    def get_pickup_point(self, obj):
        return f'{float(obj.pickup_point.y)},{float(obj.pickup_point.x)}'

    class Meta:
        model = Order
        fields = (
            "id", "order_id", "status", "customer_name", "contact_email",
            "contact_person", "execution_date", "order_type",
            "order_value", "drop_address", "order_detail_url",
            "contact_number", "reference_number", "no_of_items",
            "pickup_point", "drop_point"
        )
        read_only_fields = [
            "id", "order_id", "status", "customer_name", "contact_email",
            "contact_person", "execution_date", "order_type",
            "order_value", "drop_address", "order_detail_url",
            "contact_number", "reference_number", "no_of_items",
            "pickup_point", "drop_point"
        ]

    def to_representation(self, instance: Order):
        representation = super().to_representation(instance=instance)
        # if instance.status == OrderConstants.OrderStatus.PARTIAL:
        #     representation["status"] = OrderConstants.OrderStatus.SUCCESSFUL
        return representation

    # def update(self, instance, validated_data, attrs):
    #     latitude = attrs.get('latitude')
    #     longitude = attrs.get('longitude')
    #     drop_address = PointField(latitude, longitude)
    #     order = self.instance
    #
    #     return attrs


class DriverAppTripSerializer(DynamicFieldsModelSerializer):
    # trip_orders = TripOrderSerializer(many=True, read_only=True)
    order_count = serializers.SerializerMethodField(read_only=True)
    trip_partitions = serializers.SerializerMethodField(read_only=True)
    trip_orders = serializers.SerializerMethodField()

    def get_trip_orders(self, obj: Trip):
        trip_orders = obj.trip_orders.order_by('sequence_number').all()
        return TripOrderSerializer(trip_orders, many=True).data

    def get_order_count(self, obj: Trip):
        trip_orders = obj.trip_orders.all()
        total = trip_orders.count()
        successful = trip_orders.filter(
            status=OrderConstants.OrderStatus.SUCCESSFUL).count()
        partially_delivered = trip_orders.filter(
            status=OrderConstants.OrderStatus.PARTIAL).count()
        failed = trip_orders.filter(status=OrderConstants.OrderStatus.FAILED).count()
        unattempted = total - successful - partially_delivered - failed

        return {
            "total": total,
            "successful": successful,
            "partially_delivered": partially_delivered,
            "failed": failed,
            "unattempted": unattempted
        }

    def get_trip_partitions(self, obj: Trip):
        return obj.trip_order_partition()

    # app work is panding.
    # def validate_trip_end_km(self, trip_end_km: int):
    #     if trip_end_km >= self.instance.trip_start_km:
    #         return self.instance.trip_end_km
    #     else:
    #         raise serializers.ValidationError("Trip End KM must be greater than Trip Start KM")

    class Meta:
        model = Trip
        fields = ("reference_number", "status", "vehicle", "trip_partitions",
                  "trip_orders", "trip_id", "order_count", "helper_name","trip_start_km", "trip_end_km")
        read_only_fields = ["trip_id", "reference_number", "vehicle", "trip_partitions"]

    def to_representation(self, instance: Trip):
        representation = super().to_representation(instance=instance)
        representation["vehicle"] = instance.vehicle.vehicle_plate_no
        return representation

    def update(self, instance, validated_data):
        status = validated_data.get('status', None)
        if status and self.instance.status == TripStatus.SCHEDULED and status == TripStatus.ACTIVE:
            instance.start_trip()
        elif status and status == TripStatus.COMPLETED:
            instance.complete_trip()
        return super().update(instance=instance, validated_data=validated_data)


class DriverExpenseSerializer(serializers.ModelSerializer):
    attachment = serializers.FileField(required=False)

    def create(self, validated_data):
        try:
            driver = self.context.get('request').user.driver
            current_trip = driver.current_trip
        except Exception as e:
            raise serializers.ValidationError(f"No Active Trip Exists.")
        validated_data['trip'] = current_trip
        validated_data['driver'] = driver
        return super(DriverExpenseSerializer, self).create(validated_data)

    class Meta:
        model = DriverExpense
        fields = ["id", "expense_name", "expense_category", "fuel_consumption",
                  "notes", "amount", "attachment"]


class TripChatLogSerializer(serializers.ModelSerializer):
    send_by_driver = serializers.BooleanField(read_only=True)
    message = serializers.CharField(default="")

    class Meta:
        model = TripChatLog
        fields = ["message", "attachment",
                  "message_format", "notify", "send_by_driver",
                  "created"]
        read_only_fields = ["sender", "trip", "driver", "created"]

    def validate(self, attrs):
        if "attachment" in attrs:
            attachment = attrs.get("attachment")
            if attachment:
                extension = attachment.name.split(".")[-1]
                if extension in ["jpg", "png", "gif", "jpeg"]:
                    attrs["message_format"] = "image"
                elif extension in ["pdf", "doc", "docx", "xls", "xlsx"]:
                    attrs["message_format"] = "document"
                elif extension in ["mp3", "wav", "aac"]:
                    attrs["message_format"] = "audio"
                elif extension in ["mp4", "wmv", "avi", "mov"]:
                    attrs["message_format"] = "video"
            else:
                attrs["message_format"] = "text"
        return attrs

    def to_representation(self, instance: TripChatLog):
        representation = super().to_representation(instance=instance)
        if instance.attachment:
            representation['message'] = instance.attachment.url
        representation["driver"] = instance.driver.user.username
        representation["trip"] = instance.trip.trip_id if instance.trip else ""
        representation["sender"] = instance.sender.username if instance.sender else ""
        representation["created"] = instance.created.timestamp()

        return representation

    def create(self, validated_data):
        trip = self.context.get('trip')
        driver = self.context.get('driver')
        user = self.context.get('request').user
        validated_data['trip'] = trip
        validated_data['driver'] = driver
        validated_data['sender'] = user
        trip_chat_log = super().create(validated_data)
        notification = Notification.objects.create(
            title=f"Driver f{driver.user.full_name} has sent a message",
            message=trip_chat_log.message,
            priority=NotificationPriority.LOW,
            notification_category=NotificationCategory.DRIVER,
            notification_type=NotificationType.SUCCESS,
            expiration_time=timezone.now() + timedelta(hours=2))
        project_user_to_be_notified = ProjectUser.objects.all().filter(project=driver.project)
        user_notifications = []
        for project_user in project_user_to_be_notified:
            user_notifications.append(UserNotification(
                user=project_user.user, notification=notification
            ))
        UserNotification.objects.bulk_create(user_notifications)
        return trip_chat_log
