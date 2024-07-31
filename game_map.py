from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

from entity import Actor
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.entities = set(entities)
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors."""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_blocking_entity_at_location(
        self, location_x: int, location_y: int,
    ) -> Optional[Entity]:
        """Return the blocking entity at a given location, if any."""
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity

        return None

    def set_tile(self, x: int, y: int, tile: str) -> None:
        # if the tile has autotile then set the autotile'
        self.tiles[x, y] = tile
        # Update the 8 tiles around the position were the tile was placed
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                self.update_tile_at(x + dx, y + dy, self.tiles[x + dx, y + dy])

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor

        return None

    def update_tile_at(self, x: int, y: int, tile: str) -> None:
        if tile["autotile"]:
            # get the neighbors
            top_tile = self.tiles[x, y - 1] if y > 0 else None
            bottom_tile = self.tiles[x, y + 1] if y < self.height - 1 else None
            left_tile = self.tiles[x - 1, y] if x > 0 else None
            right_tile = self.tiles[x + 1, y] if x < self.width - 1 else None
            top_right_tile = self.tiles[x + 1, y - 1] if x < self.width - 1 and y > 0 else None
            top_left_tile = self.tiles[x - 1, y - 1] if x > 0 and y > 0 else None
            bottom_right_tile = self.tiles[x + 1, y + 1] if x < self.width - 1 and y < self.height - 1 else None
            bottom_left_tile = self.tiles[x - 1, y + 1] if x > 0 and y < self.height - 1 else None

            top = False
            bottom = False
            left = False
            right = False
            top_right = False
            top_left = False
            bottom_right = False
            bottom_left = False
            if top_tile and top_tile["autotile"]:
                top = True
            if bottom_tile and bottom_tile["autotile"]:
                bottom = True
            if left_tile and left_tile["autotile"]:
                left = True
            if right_tile and right_tile["autotile"]:
                right = True
            if top_right_tile and top_right_tile["autotile"]:
                top_right = True
            if top_left_tile and top_left_tile["autotile"]:
                top_left = True
            if bottom_right_tile and bottom_right_tile["autotile"]:
                bottom_right = True
            if bottom_left_tile and bottom_left_tile["autotile"]:
                bottom_left = True

            # set the autotile based on the flags
                   
            ch = " "
            if (top and bottom) and not (left and right):
                ch = "║"
            elif (left and right) and not (top and bottom):
                ch = "═"
            elif top and left and not top_left:
                ch = "╝"
            elif top and right and not top_right:
                ch = "╚"
            elif bottom and right and not bottom_right:
                ch = "╔"
            elif bottom and left and not bottom_left:
                ch = "╗"
            elif top and left:
                ch = "╝"
            elif top and right:
                ch = "╚"
            elif bottom and right:
                ch = "╔"
            elif bottom and left:
                ch = "╗"
            elif left and right and bottom:
                ch = "╦"
            elif left and right and top:
                ch = "╩"
            elif right and top and bottom:
                ch = "╠"
            elif left and top and bottom:
                ch = "╣"
            elif left and top and right and bottom:
                ch = "╬"
            elif left:
                ch = "■"
            elif right:
                ch = "■"
            elif top:
                ch = "■"
            elif bottom:
                ch = "■"

            # Set the first int if the "dark" nparray with the unicode of the ch
            tile["dark"]["ch"] = ord(ch)
            tile["light"]["ch"] = ord(ch)
            
    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x, y=entity.y, string=entity.char, fg=entity.color
                )