from lib.constants import (
    OrderConstants,
    NotificationPriority,
    CustomerNotificationStatus,
    VehicleFuelType,
    VehicleStatus,
    ServiceType,
    TripStatus,
    StatusConstants,
    DriverStatus,
    ChatMessageFormat,
    ProjectStatus,
    ItemUnits,
    DriverExpenseCategory,
    TripPlanning,
    NotificationType,
    NotificationCategory,
    HSMRequestStatus,
    SensorReadingLogStatus,
    VehicleDocumentType,
    DriverDocumentType,
    TripTemperatureFileStatus,
    TagType,
)

ATTACHMENT_FORMATS = [
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "aac",
    "mp3",
    "pdf",
    "xls",
    "doc",
    "docx",
    "xlsx",
    "mp4",
    "mkv",
    "avi",
    "wmv",
    "mov",
    "wav",
    "webm",
]
MESSAGE_FORMATS = (
    (ChatMessageFormat.AUDIO, "Audio"),
    (ChatMessageFormat.TEXT, "Text"),
    (ChatMessageFormat.IMAGE, "Image"),
    (ChatMessageFormat.DOCUMENT, "Document"),
    (ChatMessageFormat.VIDEO, "Video"),
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

NOTIFICATION_TYPE_CHOICES = (
    (NotificationType.INFO, "Info"),
    (NotificationType.WARNING, "Warning"),
    (NotificationType.ERROR, "Error"),
    (NotificationType.SUCCESS, "Success"),
)

NOTIFICATION_CATEGORY_CHOICES = (
    (NotificationCategory.ORDER, "Order"),
    (NotificationCategory.DRIVER, "Driver"),
    (NotificationCategory.LOCATION, "Location"),
    (NotificationCategory.TRIP_PLANNING, "Trip Planning"),
    (NotificationCategory.CUSTOMER, "Customer"),
    (NotificationCategory.VEHICLE, "Vehicle"),
    (NotificationCategory.REPORT, "Report"),
)

NOTIFICATION_PRIORITY_CHOICES = (
    (NotificationPriority.HIGH, "High"),
    (NotificationPriority.MEDIUM, "Medium"),
    (NotificationPriority.LOW, "Low"),
)

CUSTOMER_NOTIFICATION_STATUSES = (
    (CustomerNotificationStatus.SCHEDULED, "Scheduled"),
    (CustomerNotificationStatus.SUCCESSFUL, "Successful"),
    (CustomerNotificationStatus.FAILED, "Failed"),
)

VEHICLE_FUEL_TYPES = (
    (VehicleFuelType.DIESEL, "Diesel"),
    (VehicleFuelType.PETROL, "Petrol"),
    (VehicleFuelType.OTHER, "Other"),
)

VEHICLE_STATUS_CHOICES = (
    (VehicleStatus.IDLE, "Idle"),
    (VehicleStatus.ON_TRIP, "On Trip"),
    (VehicleStatus.DEACTIVATED, "Deactivated"),
)

VEHICLE_DOCUMENT_TYPE_CHOICES = (
    (VehicleDocumentType.VEHICLE_PHOTO, "Vehicle Photo"),
    (VehicleDocumentType.VEHICLE_RC_PHOTO, "Mulkiya"),
    (VehicleDocumentType.FOOD_DELIVERY_PERMITS, "Food Delivery Permits"),
    (VehicleDocumentType.CALIBRATION_CERTIFICATE, "Calibration Certificate"),
    (VehicleDocumentType.INSURANCE_CERTIFICATE, "Insurance Certificate"),
    (VehicleDocumentType.OTHERS, "Other Documents"),
)

DRIVER_DOCUMENT_TYPE_CHOICES = (
    (DriverDocumentType.DRIVER_PHOTO, "Driver Photo"),
    (DriverDocumentType.LICENSE_PHOTO, "License Photo"),
    (DriverDocumentType.FOOD_SAFETY_PERMITS, "Food Safety Permits"),
    (DriverDocumentType.EMIRATES_ID, "Emirates ID"),
    (DriverDocumentType.VACCINATION_CARD, "Vaccination ID"),
    (DriverDocumentType.HEALTH_CARD, "Health ID"),
    (DriverDocumentType.NATIONAL_ID_CARD, "National ID Card"),
    (DriverDocumentType.VISA, "Visa ID"),
    (DriverDocumentType.OTHERS, "Other Documents"),
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

TAG_TYPE_CHOICES = (
    (TagType.DRIVER_TAG, "Driver"),
    (TagType.VEHICLE_TAG, "Vehicle"),
)

TRIP_STATUS_CHOICES = (
    (TripStatus.COMPLETED, "Completed"),
    (TripStatus.ACTIVE, "Active"),
    (TripStatus.SCHEDULED, "Scheduled"),
    (TripStatus.PAUSED, "Paused"),
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

PROJECT_STATUS_CHOICES = (
    (ProjectStatus.ACTIVE, "Active"),
    (ProjectStatus.DEACTIVATED, "Deactivated"),
)

DRIVER_EXPENSE_CATEGORY = (
    (DriverExpenseCategory.FUEL_FILL_RECEIPT, "Fuel Fill Receipt"),
    (DriverExpenseCategory.TOLL_RECEIPT, "Toll Receipt"),
    (DriverExpenseCategory.PARKING_TICKETS, "Parking Tickets"),
    (DriverExpenseCategory.OTHER_RECEIPT, "Other Receipt"),
)

TRIP_PLAN_STATUS_CHOICES = (
    (TripPlanning.PENDING, "Pending"),
    (TripPlanning.IN_PROGRESS, "In Progress"),
    (TripPlanning.POST_PROCESSING, "Post Processing"),
    (TripPlanning.COMPLETED, "Completed"),
    (TripPlanning.CANCELED, "Canceled"),
    (TripPlanning.FAILED, "Failed"),
)

PLAN_STATUS_CHOICES = (
    (TripPlanning.PENDING, "Pending"),
    (TripPlanning.WAITING, "waiting"),
    (TripPlanning.IN_PROGRESS, "In Progress"),
    (TripPlanning.FINISHED_IN_TIME, "Finished In Time"),
    (TripPlanning.FINISHED_OUT_OF_TIME, "Finished Out Of Time"),
    (TripPlanning.CANCELED, "Canceled"),
    (TripPlanning.FAILED, "Failed"),
)

PLAN_LOCATION_TYPE_CHOICES = (
    (TripPlanning.WAREHOUSE, "Warehouse"),
    (TripPlanning.CUSTOMER, "Customer"),
)

PLAN_DEMAND_TYPE_CHOICES = ((TripPlanning.PICKUP, "Pickup"), (TripPlanning.DROP, "Drop"))

SHIFT_TYPE_CHOICES = (("PERFORMER", "PERFORMER"), ("TRANSPORT", "TRANSPORT"))

OPTIMIZATION_CHOICES = (
    (TripPlanning.OPTIMIZE_DISTANCE, "optimize distance"),
    (TripPlanning.VISUAL_GROUPING, "visual grouping"),
    (TripPlanning.OPTIMIZE_TRANSPORTS, "optimize transports"),
    (TripPlanning.OPTIMIZE_LOCALITY_GROUPING, "optimize locality grouping"),
    (TripPlanning.OPTIMIZE_CARS_THEN_DISTANCE, "optimize cars then distance"),
    (TripPlanning.OPTIMIZE_TIME, "optimize_time"),
    (TripPlanning.OPTIMIZE_CARS_THEN_TIME, "optimize cars then time"),
    (TripPlanning.OPTIMIZE_VISUAL_GROUPING, "optimize visual grouping"),
    (TripPlanning.OPTIMIZE_CARS_THEN_LOCALITY_GROUPING, "optimize cars then locality grouping"),
    (TripPlanning.OPTIMIZE_MONEY, "optimize money"),
)

TRANSPORT_CARGO_MEASUREMENT_CHOICES = (
    (TripPlanning.VOLUME, "Consider Volume"),
    (TripPlanning.MASS, "Consider Mass"),
    (TripPlanning.VOLUME_MASS, "Consider both"),
)

TRANSPORT_TYPE_CHOICES = (
    (TripPlanning.TRUCK, "TRUCK"),
    (TripPlanning.CAR, "CAR"),
    (TripPlanning.CAR_GT, "CAR_GT"),
)

HSM_REQUEST_STATUS = (
    (HSMRequestStatus.PENDING_ENROUTE, "PENDING ENROUTE"),
    (HSMRequestStatus.DELIVERED_TO_OPERATOR, "DELIVERED TO OPERATOR"),
    (HSMRequestStatus.DELIVERED_TO_HANDSET, "DELIVERED TO HANDSET"),
    (HSMRequestStatus.EXPIRED_EXPIRED, "EXPIRED"),
    (HSMRequestStatus.EC_UNKNOWN_USER, "USER NOT FOUND"),
    (HSMRequestStatus.REJECTED_NETWORK, "REJECTED NETWORK"),
    (HSMRequestStatus.UNDELIVERABLE_REJECTED_OPERATOR, "UNDELIVERABLE"),
    (HSMRequestStatus.REJECTED_PREFIX_MISSING, "REJECTED"),
)

SENSOR_READING_LOG_STATUS = (
    (SensorReadingLogStatus.SUCCESSFUL, "SUCCESSFUL"),
    (SensorReadingLogStatus.FAILED, "FAILED"),
)

TRIP_TEMPERATURE_FILE_STATUS = (
    (TripTemperatureFileStatus.NOT_PROCESSED, "Not Processed"),
    (TripTemperatureFileStatus.PROCESSING, "Processing"),
    (TripTemperatureFileStatus.SUCCESSFUL, "Successful"),
    (TripTemperatureFileStatus.FAILED, "Failed"),
)
