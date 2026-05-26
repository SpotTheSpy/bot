from enum import StrEnum
from typing import Any


class Locale(StrEnum):
    """
    Enum of all supported locales.
    """

    ENGLISH = "en"

    @classmethod
    def _missing_(
            cls,
            value: Any,
    ) -> "Locale":
        """
        Defaults to ENGLISH if the provided locale is not supported.
        """

        return cls.ENGLISH
