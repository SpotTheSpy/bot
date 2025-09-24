from app.actions.action import Action
from app.enums.page_turn import PageTurn


class PageTurnAction(Action, prefix="page_turn"):
    turn: PageTurn
