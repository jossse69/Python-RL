from __future__ import annotations

import copy
import random
from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from entity import Actor
    from engine import Engine

class StatusEffect:
    """
    A class to represent a status effect. Such as "poisoned", "stunned", etc.
    """
    def __init__(self, name: str, duration: int, value: int):
        self.name = name
        self.duration = duration
        self.value = value

    def on_tick(self, parent: Actor, engine: Engine) -> None:
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

    def on_tick(self, parent: Actor, engine: Engine) -> None:
        parent.fighter.take_damage(self.value)
        self.duration -= 1

class Bleeding(StatusEffect):
    """
    A class to represent a bleeding status effect.

    If the actor moved this turn, they will take damage based on the value of the status effect.
    """
    def __init__(self, duration: int, value: int):
        super().__init__("Bleeding", duration, value)
        self.last_pos = (0, 0)

    def on_tick(self, parent: Actor, engine: Engine) -> None:
        self.last_pos = (parent.last_position[0], parent.last_position[1])

        if parent.last_position != (parent.x, parent.y):
            parent.fighter.take_damage(self.value)
        self.duration -= 1

class Spored(StatusEffect):
    """
    A class to represent a 'full of spores' status effect.

    The actor takes damage each turn, slimilar to poisoned, but if the actor dies by it, spawn a Baby Shroom monster near were it died.
    """
    def __init__(self, duration: int, value: int):
        super().__init__("full of spores", duration, value)
        from entity_factories import baby_shroom
        self.baby_shroom = copy.deepcopy(baby_shroom)


    def on_tick(self, parent: Actor, engine: Engine) -> None:
        old_name = parent.name
        parent.fighter.take_damage(self.value)

        # Spawn a baby shroom if the actor dies by it.
        if parent.fighter.hp <= 0:
            pos = (parent.x + random.randint(-1, 1), parent.y + random.randint(-1, 1))

            while not engine.game_map.get_blocking_entity_at_location(pos[0], pos[1]) and not engine.game_map.is_walkable_tile(pos[0], pos[1]):
                pos = (parent.x + random.randint(-1, 1), parent.x + random.randint(-1, 1))

            self.baby_shroom.spawn(engine.game_map, pos[0], pos[1])

            # Add a message of the enemy spawning from the actor's body!
            engine.message_log.add_message(f"A baby shroom bursts right open from {old_name}'s body!", color.status_effect_applied)

        self.duration -= 1