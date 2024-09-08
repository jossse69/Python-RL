from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import color
from entity import Actor
import exceptions
import random

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item, NPC
    from status_effect import StatusEffect


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to."""
        return self.entity.parent.engine
    
    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()

class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    def perform(self, engine: Engine, entity: Entity) -> None:
        raise NotImplementedError()
    
    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)
    
    @property
    def target_NPC(self) -> Optional[NPC]:
        """Return the NPC at this actions destination."""
        return self.engine.game_map.get_NPC_at_location(*self.dest_xy)

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)

class MeleeAction(ActionWithDirection):

    def __init__(self, entity: Actor, dx: int, dy: int, effect: Optional[StatusEffect] = None):
        super().__init__(entity, dx, dy)
        self.effect = effect

    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")

        # Chance for the attacker to dodge, based on his dodge chance
        roll = random.randint(1, 100)
        if roll <= target.fighter.dodge:
            self.engine.message_log.add_message(
                f"{self.entity.name.capitalize()} Tries to attack, but {target.name.capitalize()} dodges the attack!",
                color.status_effect_applied
            )
            return

        damage = self.entity.fighter.power - target.fighter.defense

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name.capitalize()}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk
        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points!",
                attack_color
            )
            target.fighter.hp -= damage

            # trigger any on_attack of the equipment of the attacker, if any.
            if self.entity.equipment and self.entity.equipment.weapon:
                self.entity.equipment.weapon.equippable.on_attack(target)

            # trigger any on_hit of the equipment of the target, if any.
            if target.equipment and target.equipment.armor:
                target.equipment.armor.equippable.on_hit(self.entity, damage)


            # Apply the status effect to the target, if any.
            if self.effect is not None:
                target.fighter.apply_status_effect(self.effect)
        else:
            self.engine.message_log.add_message(
                f"{attack_desc}, but does no damage.",
                attack_color
            )

class MovementAction(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("There's something blocking the way!")


        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
                self.entity.last_position = (self.entity.x, self.entity.y)
                return MeleeAction(self.entity, self.dx, self.dy).perform()
        elif self.target_NPC:
                self.entity.last_position = (self.entity.x, self.entity.y)
                return InteractNPCAction(self.entity, self.dx, self.dy).perform()
        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()
        
class InteractNPCAction(ActionWithDirection):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity, dx, dy)

    def perform(self) -> None:
        if self.target_NPC:
            input_handler = self.target_NPC.interact()
            if input_handler:
                self.engine.future_event_handler = input_handler
        else:
            raise exceptions.Impossible("There's nothing to interact with.")

class WaitAction(Action):
    def perform(self) -> None:
        self.entity.last_position = (self.entity.x, self.entity.y)

class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")

class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")
        
class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)

class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)