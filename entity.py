from __future__ import annotations

import copy
import math
import random
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from engine import Engine
from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from components.consumable import Consumable
    from components.equipment import Equipment
    from components.equippable import Equippable
    from components.inventory import Inventory
    from components.level import Level
    from components.zone import ZoneComponent

    from game_map import GameMap
    from input_handlers import EventHandler
    from status_effect import StatusEffect
    from npc_handler import NPCHandler


T = TypeVar("T", bound="Entity")

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[GameMap, Inventory]

    def __init__(
        self,
        parent: Optional[GameMap] = None,
        inspect_message: Optional[str] = "I don't know what this thing is.",
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: RenderOrder = RenderOrder.CORPSE,
    ):
        """
        Create a new entity with the given properties.
        """
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        self.inspect_message = inspect_message
        self.is_swarm = False
        self.last_position = (x, y)
        self.visible = True

        # Create a internal_name for the entity. Internal names are allways lowercase and have spaces replaced with underscores.
        self.internal_name = name.lower().replace(" ", "_")

        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

    @property
    def gamemap(self) -> GameMap:
        return self.parent.gamemap
    
    def spawn(self: T, gamemap: GameMap, x: int, y: int, is_swarm: Optional[bool] = False) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.is_swarm = is_swarm
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)


    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None, is_swarm: Optional[bool] = False) -> None:
        """Place this entity at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Possibly uninitialized.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            self.is_swarm = is_swarm # If this is a swarm, then it will not give XP when it dies.
            gamemap.entities.add(self)
            self.is_swarm = False

    def move(self, dx: int, dy: int) -> None:
        """
        Moves the entity by a given amount
        """
        self.last_position = (self.x, self.y)
        self.x += dx
        self.y += dy


class Actor(Entity):
    """
    A generic object to that can take damage, do turns, etc. for things like enemies, the player, etc.
    """

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        inspect_message: Optional[str] = "I don't know what this thing is.",
        ai_cls: Type[BaseAI],
        equipment: Equipment,
        fighter: Fighter,
        inventory: Inventory,
        level: Level,
        effect: Optional[StatusEffect] = None,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
            inspect_message=inspect_message,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)
        self.ai.set_effect(effect)

        self.equipment: Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.inventory = inventory
        self.inventory.parent = self

        self.level = level
        self.level.parent = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)
    
class NPC(Entity):
    """
    A NPC (Non-player character) is used for freindly npcs the player can interact with. Such as merchants, quest givers, etc.
    """

    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        inspect_message: Optional[str] = "I don't know what this thing is.",
        npc_handler_cls: Type[NPCHandler],
        input_handler_cls: Type[EventHandler],
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
            inspect_message=inspect_message,
        )
        self.is_npc = True
        self.npc_handler_class = npc_handler_cls
        self.input_handler_class = input_handler_cls

    def init_handler(self, engine: Engine) -> None:
        self.npc_handler = self.npc_handler_class(engine, self.input_handler_class, self)
        self.npc_handler.init_handler()

    @property
    def input_handler(self) -> EventHandler:
        return self.npc_handler.input_handler

    def interact(self) -> EventHandler:
        """
        Interact with this NPC.
        """
        self.parent.engine.message_log.add_message(f"You interact with the {self.name}.")

        return self.input_handler




class Item(Entity):
    """
    An item that can be picked up and used, uuses item especific components.
    """
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        inspect_message: Optional[str] = "I don't know what this thing is.",
        consumable: Optional[Consumable] = None,
        equippable: Optional[Equippable] = None,
        value: int = 0,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ITEM,
            inspect_message=inspect_message,
        )

        self.value = value
        self.consumable = consumable
        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self

class Zone(Entity):
    """
    A walkable enity that can inflict a status effect to any actors steping on it, and can also disapear after some time. Used for water, gases, etc.
    """
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        inspect_message: Optional[str] = "I don't know what this thing is.",
        duration: int = 0,
        is_permanent: bool = False,
        moves_around: bool = False,
        zone_component: type[ZoneComponent],
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=RenderOrder.ZONE,
            inspect_message=inspect_message,
        )

        self.duration = duration
        self.is_permanent = is_permanent
        self.zone_component = zone_component(self)
        self.zone_component.parent = self
        self.moves_around = moves_around

    def on_tick_actor(self, actor: Actor) -> None:
        self.zone_component.on_actor_tick(actor)
    def on_update(self) -> None:
        if self.moves_around:
            # Pick a random direction to move to
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Northwest
                    (0, -1),  # North
                    (1, -1),  # Northeast
                    (-1, 0),  # West
                    (1, 0),  # East
                    (-1, 1),  # Southwest
                    (0, 1),  # South
                    (1, 1),  # Southeast
                ]
            )

            # Check if there's a walkble tile in the random direction
            if self.gamemap.is_walkable_tile(self.x + direction_x, self.y + direction_y):
                # Check if there's not anoder zone in the random direction.
                if not any(
                    entity
                    for entity in self.gamemap.zones
                    if entity.x == self.x + direction_x and entity.y == self.y + direction_y
                ):
                    self.move(direction_x, direction_y)