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


class StatusConstants:
    TRIP = "trip"
    ORDER = "order"
    DRIVER = "driver"
    VEHICLE = "vehicle"


class VehicleFuelType:
    DIESEL = "diesel"
    PETROL = "petrol"
    OTHER = "other"


class VehicleStatus:
    IDLE = "idle"
    ON_TRIP = "on_trip"
    DEACTIVATED = "deactivated"


class VehicleDocumentType:
    VEHICLE_PHOTO = "vehicle_photo"
    VEHICLE_RC_PHOTO = "vehicle_rc_photo"
    FOOD_DELIVERY_PERMITS = "food_delivery_permits"
    CALIBRATION_CERTIFICATE = "calibration_certificate"
    INSURANCE_CERTIFICATE = "insurance_certificate"
    OTHERS = "other"


class DriverDocumentType:
    DRIVER_PHOTO = "driver_photo"
    LICENSE_PHOTO = "license_photo"
    FOOD_SAFETY_PERMITS = "food_safety_permits"
    EMIRATES_ID = "emirates_id"
    VACCINATION_CARD = "vaccination_card"
    HEALTH_CARD = "health_card"
    NATIONAL_ID_CARD = "national_id_card"
    VISA = "visa"
    OTHERS = "other"


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


class TagType:
    DRIVER_TAG = "driver_tag"
    VEHICLE_TAG = "vehicle_tag"


class TripStatus:
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"


class DriverExpenseCategory:
    FUEL_FILL_RECEIPT = "FuelFillReceipt"
    TOLL_RECEIPT = "TollReceipt"
    PARKING_TICKETS = "ParkingTickets"
    OTHER_RECEIPT = "OtherReceipt"


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


class NotificationPriority:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NotificationType:
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class NotificationCategory:
    ORDER = "order"
    DRIVER = "driver"
    LOCATION = "location"
    TRIP_PLANNING = "trip_planning"
    CUSTOMER = "customer"
    VEHICLE = "vehicle"
    REPORT = "report"


class CustomerNotificationStatus:
    SCHEDULED = "Scheduled"
    SUCCESSFUL = "Successful"
    FAILED = "Failed"


class ServiceType:
    B2B = "B2B"
    B2C = "B2C"


class ChatMessageFormat:
    AUDIO = "audio"
    DOCUMENT = "document"
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


class ProjectStatus:
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class TripStatusLogs:
    schedule = "Trip is Scheduled"
    start = "Trip is Started"
    pause = "Trip is Paused"
    resume = "Trip is Resumed."
    end = "Trip is Completed"
    on_break = "Driver is On Break"
    break_complete = "Driver is back from Break"
    on_duty = "Driver is On Duty"
    off_duty = "Driver is Off Duty"
    add_orders = "Orders are Added"
    remove_orders = "Orders are Removed"


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


class PermissionModels(Enum):
    """
    Class that defines which models to be used for User Permissions
    """

    ITEMMASTER = "itemmaster"
    ORDER = "order"
    TRIP = "trip"
    DRIVER = "driver"
    VEHICLE = "vehicle"
    DASHUSER = "dashuser"
    PROJECT = "project"
    ZONE = "zone"
    ROLE = "role"
    CUSTOMERADDRESS = "customeraddress"
    TICKET = "ticket"

    @classmethod
    def all(module):
        return [model.value for model in list(module)]


class TripPlanning:
    PENDING = "PENDING"
    WAITING = "WAITING"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED_IN_TIME = "FINISHED_IN_TIME"
    FINISHED_OUT_OF_TIME = "FINISHED_OUT_OF_TIME"
    CANCELED = "CANCELED"
    FAILED = "FAILED"

    POST_PROCESSING = "POST_PROCESSING"
    COMPLETED = "COMPLETED"

    WAREHOUSE = "warehouse"
    CUSTOMER = "customer"

    PICKUP = "PICKUP"
    DROP = "DROP"

    VOLUME = "Volume"
    MASS = "Mass"

    VOLUME_MASS = "Volume_Mass"

    TRUCK = "TRUCK"
    CAR = "CAR"
    CAR_GT = "CAR_GT"

    OPTIMIZE_DISTANCE = "optimize_distance"
    VISUAL_GROUPING = "visual_grouping"
    OPTIMIZE_TRANSPORTS = "optimize_transports"
    OPTIMIZE_LOCALITY_GROUPING = "optimize_locality_grouping"
    OPTIMIZE_CARS_THEN_DISTANCE = "optimize_cars_then_distance"
    OPTIMIZE_TIME = "optimize_time"
    OPTIMIZE_CARS_THEN_TIME = "optimize_cars_then_time"
    OPTIMIZE_VISUAL_GROUPING = "optimize_visual_grouping"
    OPTIMIZE_CARS_THEN_LOCALITY_GROUPING = "optimize_cars_then_locality_grouping"
    OPTIMIZE_MONEY = "optimize_money"

    # Vee route Settings
    vee_route_settings = {
        "configuration": "optimize_cars_then_single_location_grouping",
        "planning_time": 78,
        "result_ttl": 25,
        "result_timezone": 0,
        "predict_slots": 0,
        "assumptions": {
            "traffic_jams": True,
            "toll_roads": True,
            "ferry_crossing": True,
            "flight_distance": False,
            "disable_compatibility": False,
            "disable_capacity": False,
            "same_order_time_window": False,
            "expand_shift_time_window": False,
        },
        "precision": 2,
    }


class HSMRequestStatus:
    PENDING_ENROUTE = "PENDING_ENROUTE"
    DELIVERED_TO_OPERATOR = "DELIVERED_TO_OPERATOR"
    DELIVERED_TO_HANDSET = "DELIVERED_TO_HANDSET"
    EXPIRED_EXPIRED = "EXPIRED_EXPIRED"
    EC_UNKNOWN_USER = "EC_UNKNOWN_USER"
    REJECTED_NETWORK = "REJECTED_NETWORK"
    UNDELIVERABLE_REJECTED_OPERATOR = "UNDELIVERABLE_REJECTED_OPERATOR"
    REJECTED_PREFIX_MISSING = "REJECTED_PREFIX_MISSING"


class SensorReadingLogStatus:
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


class TripTemperatureFileStatus:
    NOT_PROCESSED = "not_processed"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
