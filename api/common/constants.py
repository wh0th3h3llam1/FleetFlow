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
