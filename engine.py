from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.console import Console
from tcod.map import compute_fov
import tcod.constants

import exceptions
from message_log import MessageLog
import render_functions

import lzma
import pickle

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld

class Engine:
     
    game_map: GameMap
    game_world: GameWorld


    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self.future_event_handler = None # Use this to set the next event handler of the engine once the next player turn is started.

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

    def handle_status_effects(self) -> None:
        for entity in set(self.game_map.actors):
            entity.fighter.update_status_effects()

    def handle_zones(self) -> None:
        zones_to_remove = []
        for zone in self.game_map.zones:
            zone.on_update()
            # Check if there's a actor in the zone.
            for actor in self.game_map.actors:
                if zone.x == actor.x and zone.y == actor.y:
                    if actor.fighter and actor.fighter.hp > 0:
                        zone.on_tick_actor(actor)

            # If the zone is not permanent, then tick down its countdown.
            if not zone.is_permanent:
                zone.duration -= 1
                if zone.duration <= 0:
                    zones_to_remove.append(zone)

        # Remove the zones that are done.
        for zone in zones_to_remove:
            self.game_map.entities.remove(zone)
            

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""

        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
            light_walls=True,
            algorithm=tcod.constants.FOV_SHADOW
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible


    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)

        render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )
        render_functions.render_credit_amount(
            console=console,
            credit_amount=self.game_world.credits,
            location=(0, 48),
        )

        render_functions.render_names_at_mouse_location(
            console=console, x=21, y=44, engine=self
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)