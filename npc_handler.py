from __future__ import annotations


import random
from typing import List, Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from engine import Engine

from render_order import RenderOrder

if TYPE_CHECKING:
    from input_handlers import EventHandler
    from entity import NPC, Item

shop_item_chances: List[Tuple[int, int]] = [
    ("healing_gel", 15),
    ("stun_gun", 15),
    ("old_kinfe", 15),
    ("iron_chest_plate", 15),
    ("xl_healing_gel", 5),
    ("taser", 10),
    ("sharp_kinfe", 10),
    ("stun_gas_granade", 5),
    ("poison_gas_granade", 5),
    ("acid_kinfe", 5),
    ("spikey_chest_plate", 5),
    ("fireball_gun", 5),
    ("hazmat_suit", 5),
    ("lead_hazmat_suit", 5),
    ("silver_kinfe", 5),
]


def get_weighted_elements_at_random(
    weighted_chances: List[Tuple[int, int]],
    amount: int,
) -> List[int]:
    chosen_weights = random.choices(
        population=[element for element, weight in weighted_chances for i in range(weight)],
        k=amount,
    )

    return chosen_weights

class NPCHandler:
    """
    A class used in NPCs to setup their input handler with more data that is sorted in this class.
    """
    def __init__(self, engine: Engine, input_handler_cls: Type[EventHandler], npc: NPC):
        self.engine = engine
        self.input_handler_cls = input_handler_cls
        self.npc = npc
        self.input_handler = None

    def init_handler(self) -> None:
        """
        Initialize the input handler for the NPC. This method can be overridden to add more data to the input handler.
        """
        self.input_handler = self.input_handler_cls(self.engine, self.npc)

class ShopKeeperHandler(NPCHandler):
    """
    Used to handler diferent kinds of shops. Along with tracking the inventory of the shop.
    """
    def __init__(self, engine: Engine, input_handler_cls: Type[EventHandler], npc: NPC):
        super().__init__(engine, input_handler_cls, npc)
        items = get_weighted_elements_at_random(shop_item_chances, random.randint(3, 8))
        self.shop_items = []
        for item in items:
            # Check for repeats and do not add if there is a repeat.
            if item in self.shop_items:
                continue
            self.shop_items.append(item)
    
    def init_handler(self) -> None:
        self.input_handler = self.input_handler_cls(self.engine, self.npc, self.shop_items)