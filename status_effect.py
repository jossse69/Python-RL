from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entity import Actor

class StatusEffect:
    """
    A class to represent a status effect. Such as "poisoned", "stunned", etc.
    """
    def __init__(self, name: str, duration: int, value: int):
        self.name = name
        self.duration = duration
        self.value = value

    def on_tick(self, parent: Actor) -> None:
        """
        Called every turn for the duration of the status effect.

        This method must be overridden by subclasses.
        """
        raise NotImplementedError()
    
class Poisoned(StatusEffect):
    """
    A class to represent a poisoned status effect.

    Actors will take damage every turn, based on the value of the status effect.

    """
    def __init__(self, duration: int, value: int):
        super().__init__("Poisoned", duration, value)

    def on_tick(self, parent: Actor) -> None:
        parent.fighter.take_damage(self.value)
        self.duration -= 1

class bleeding(StatusEffect):
    """
    A class to represent a bleeding status effect.

    If the actor moved this turn, they will take damage based on the value of the status effect.
    """
    def __init__(self, duration: int, value: int):
        super().__init__("Bleeding", duration, value)
        self.last_pos = (0, 0)

    def on_tick(self, parent: Actor) -> None:
        self.last_pos = (parent.last_position[0], parent.last_position[1])

        if parent.last_position != (parent.x, parent.y):
            parent.fighter.take_damage(self.value)
        self.duration -= 1