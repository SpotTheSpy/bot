from enum import IntEnum


class TimeStamp(IntEnum):
    """
    Various time stamps in seconds.
    """

    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
