from app.actions.action import Action


class SwitchSceneAction(Action, prefix="switch"):
    scene: str
