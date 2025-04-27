from common.constants import (
    DriverStatus,
    ItemUnits,
    OrderConstants,
    ProjectStatus,
    ServiceType,
    StatusConstants,
)
from model_utils import Choices


PROJECT_STATUS_CHOICES = Choices(
    (ProjectStatus.ACTIVE, "Active"), (ProjectStatus.DEACTIVATED, "Inactive")
)


ITEM_UNIT_CHOICES = (
    (ItemUnits.KG, "Kg"),
    (ItemUnits.CASE, "Case"),
    (ItemUnits.EACH, "Each"),
)


DRIVER_STATUS_CHOICES = (
    (DriverStatus.ON_DUTY, "On Duty"),
    (DriverStatus.OFF_DUTY, "Off Duty"),
    (DriverStatus.ON_TRIP, "On Trip"),
    (DriverStatus.ON_BREAK, "Break"),
    (DriverStatus.DEACTIVATED, "Deactivated"),
)
SERVICE_TYPE_CHOICES = (
    (ServiceType.B2B, "B2B"),
    (ServiceType.B2C, "B2C"),
)


STATUS_CATEGORY_CHOICES = (
    (StatusConstants.ORDER, "Order"),
    (StatusConstants.TRIP, "Trip"),
    (StatusConstants.DRIVER, "Driver"),
    (StatusConstants.VEHICLE, "Vehicle"),
)

ORDER_TYPE_CHOICES = (
    (OrderConstants.OrderType.DELIVERY, "Delivery"),
    (OrderConstants.OrderType.PICK_UP, "Pickup"),
)

PAYMENT_TYPE_CHOICES = (
    (OrderConstants.PaymentMethod.PREPAID, "Prepaid"),
    (OrderConstants.PaymentMethod.COD, "Cash on Delivery"),
    (OrderConstants.PaymentMethod.CREDIT, "Credit"),
)

STORAGE_TYPE_CHOICES = (
    (OrderConstants.StorageTypes.DRY, "Dry"),
    (OrderConstants.StorageTypes.CHILLED, "Chilled"),
    (OrderConstants.StorageTypes.FROZEN, "Frozen"),
)

ORDER_STATUS_CHOICES = (
    (OrderConstants.OrderStatus.UNASSIGNED, "Unassigned"),
    (OrderConstants.OrderStatus.ASSIGNED, "Assigned"),
    (OrderConstants.OrderStatus.PICKED_UP, "Picked Up"),
    (OrderConstants.OrderStatus.ENROUTE, "Enroute"),
    (OrderConstants.OrderStatus.SUCCESSFUL, "Successful"),
    (OrderConstants.OrderStatus.FAILED, "Failed"),
    (OrderConstants.OrderStatus.CANCELLED, "Cancelled"),
    (OrderConstants.OrderStatus.PARTIAL, "Partially Delivered"),
)

ATTACHMENT_TYPE_CHOICES = (
    (OrderConstants.AttachmentType.POD, "Proof of delivery"),
    (OrderConstants.AttachmentType.ORDER, "Order"),
    (OrderConstants.AttachmentType.OTHERS, "others"),
)
