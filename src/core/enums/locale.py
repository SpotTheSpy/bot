from enum import StrEnum, auto
from typing import Any


class Locale(StrEnum):
    """
    Enum of all supported locales.
    """

    EN = auto()
    """
    English.
    """

    UK = auto()
    """
    Ukrainian.
    """

    RU = auto()
    """
    Russian.
    """

    @classmethod
    def _missing_(
            cls,
            value: Any,
    ) -> "Locale":
        """
        Defaults to EN if the provided locale is not supported.
        """

        return cls.EN
