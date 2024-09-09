from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from status_effect import Poisoned, Spored
from components.ai import ConfusedEnemy

if TYPE_CHECKING:
    from entity import Actor, Zone


class ZoneComponent(BaseComponent):
    parent: Zone

    def __init__(self, zone: Zone):
        self.zone = zone

    def on_actor_tick(self, actor: Actor) -> None:
        """
        Called when an actor is updated while in this zone.

        This method must be implemented by subclasses.
        """
        raise NotImplementedError()
    
class HydrogenSulfideGas(ZoneComponent):
    def on_actor_tick(self, actor: Actor) -> None:
        # Poison the actor
        if actor.fighter:
            actor.fighter.apply_status_effect(Poisoned(7, 2))

class NitrousOxideGas(ZoneComponent):
    def on_actor_tick(self, actor: Actor) -> None:
        if actor is self.engine.player:
            self.engine.game_world.player_confused_turns = 10
        # Change the actor's AI to confused, if its not already confused.
        elif actor.ai and not isinstance(actor.ai, ConfusedEnemy):
            actor.ai = ConfusedEnemy(actor, actor.ai, 10)

class SporeAir(ZoneComponent):
    def on_actor_tick(self, actor: Actor) -> None:
        if actor.fighter:
            actor.fighter.apply_status_effect(Spored(15, 1))