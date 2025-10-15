from app.actions.action import Action


class MenuAction(Action, prefix="menu"):
    """
    Callback action for returning to the menu.
    """
