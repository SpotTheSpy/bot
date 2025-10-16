from abc import ABC

from aiogram.filters.callback_data import CallbackData


class Action(CallbackData, ABC, prefix="action"):
    """
    Abstract class for all callback actions.
    """
