from enum import Enum


class FieldConstants:
    PHONE_NUMBER_LENGTH = 16
    ADDRESS_LENGTH = 200
    NAME_LENGTH = 200
    FULL_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_TIME_FORMAT = "%Y-%m-%d %H:%M"
    DATE_FORMAT = "%Y-%m-%d"
    FULL_TIME_FORMAT = "%H:%M:%S"
    TIME_FORMAT = "%H:%M"
    MULTIPLE_DATE_FORMATS = ("%m/%d/%Y", "%m-%d-%Y", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d")


class SystemRoles:
    SYS_ADMIN = "System Administrator"
    DRIVER = "Driver"
    SUPPORT = "Support"


class PermissionModels(Enum):
    """
    Class that defines which models to be used for User Permissions
    """

    USER = "user"
    ROLE = "role"

    @classmethod
    def all(cls):
        return [model.value for model in list(cls)]


class ProjectStatus:
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class ServiceType:
    B2B = "B2B"
    B2C = "B2C"


class StatusConstants:
    TRIP = "trip"
    ORDER = "order"
    DRIVER = "driver"
    VEHICLE = "vehicle"


class ItemUnits:
    KG = "kg"
    CASE = "case"
    EACH = "each"


class DriverStatus:
    ON_DUTY = "on_duty"
    OFF_DUTY = "off_duty"
    ON_TRIP = "on_trip"
    ON_BREAK = "break"
    DEACTIVATED = "deactivated"


class OrderConstants:
    class AttachmentType:
        POD = "pod"
        ORDER = "order"
        OTHERS = "others"

    class StorageTypes:
        FROZEN = "F"
        CHILLED = "C"
        DRY = "D"

    class OrderType:
        DELIVERY = "delivery"
        PICK_UP = "pickup"

    class PaymentMethod:
        COD = "cod"
        PREPAID = "prepaid"
        CREDIT = "credit"

    class OrderStatus:
        UNASSIGNED = "unassigned"
        ASSIGNED = "assigned"
        PICKED_UP = "pickedup"
        ENROUTE = "enroute"
        PARTIAL = "partially_delivered"
        SUCCESSFUL = "successful"
        FAILED = "failed"
        CANCELLED = "cancelled"


class OrderStatusLogs:
    assigned = "Order is Assigned"
    picked_up = "Order is Picked Up"
    completed = "Order has been Delivered"
    failed = "Order has been Returned"
    enroute = "Order is Enroute"
    cancelled = "Order is Cancelled"
    unassigned = "Order is Unassigned"
    pod_upload = "POD Uploaded"
    add_line_item = "Items Added to Order"
    order_notification_sent = "order_notification_sent"
