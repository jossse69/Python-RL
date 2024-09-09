from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

import color
import copy

from components.base_component import BaseComponent
from render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor
    from status_effect import StatusEffect

class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, base_dodge: int, base_defence, base_power: int, immune_effects: Optional[list[type[StatusEffect]]] = None):
        self.max_hp = hp
        self._hp = hp
        self.base_dodge = base_dodge
        self.base_defence = base_defence
        self.base_power = base_power
        self.status_effects = []
        self.immune_effects = immune_effects if immune_effects else []
        self.last_actor_hurt_by = ""


    @property
    def dodge(self) -> int:
        return self.base_dodge + self.dodge_bonus

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus
    
    @property	
    def defense(self) -> int:
        return self.base_defence + self.defense_bonus

    @property
    def dodge_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.dodge_bonus
        else:
            return 0

    @property
    def power_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.power_bonus
        else:
            return 0
        
    @property
    def defense_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.defense_bonus
        else:
            return 0

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def apply_status_effect(self, effect: StatusEffect) -> None:

        # If the fighter is immune to the effect, then don't apply it.
        for immune_effect in self.immune_effects:
            if isinstance(effect, immune_effect):
                return

        for status_effect in self.status_effects:
            if status_effect.name == effect.name:
                status_effect.duration += effect.duration
                return
        self.status_effects.append(copy.deepcopy(effect))

        self.engine.message_log.add_message(f"{self.parent.name} is now {effect.name}!", color.status_effect_applied)

    def update_status_effects(self) -> None:
        for status_effect in self.status_effects:
            status_effect.on_tick(self.parent, self.engine)
            if status_effect.duration <= 0 and status_effect in self.status_effects:
                self.status_effects.remove(status_effect)
                self.engine.message_log.add_message(f"{self.parent.name} is no longer {status_effect.name}.")

    def has_status_effect(self, effect: StatusEffect) -> bool:
        for status_effect in self.status_effects:
            if status_effect.name == effect.name:
                return True
        return False

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
        else:
            death_message = f"{self.parent.name} died!"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"Corpse of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE
        self.parent.inspect_message = "It's a dead corpse."

        self.engine.message_log.add_message(death_message, death_message_color)

        # Remove all status effects.
        self.status_effects = []

        if self.last_actor_hurt_by == self.engine.player.internal_name and not self.parent.is_swarm: # If this is a swarm, then it will not give XP or Credits when it dies.
            self.engine.player.level.add_xp(self.parent.level.xp_given)

            # Have a chance to find credits when the enemy dies.
            roll = random.randint(1, 100)
            if roll <= 45:
                amount = self.max_hp // 4 # Give 25% of the entity's max HP as credits (rounded down).
                self.engine.game_world.credits += amount
                self.engine.message_log.add_message(f"You found {amount} credits!", color.health_recovered)
