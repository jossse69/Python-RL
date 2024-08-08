#!/usr/bin/env python3
import tcod
import copy
import traceback
import color
from engine import Engine
from procgen import generate_dungeon
import entity_factories

def main():
    screen_width = 80
    screen_height = 50

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    map_width = 80
    map_height = 43

    max_monsters_per_room = 2
    max_items_per_room = 2

    tileset = tcod.tileset.load_tilesheet("data/zaratustra_msx.png", 16, 16, tcod.tileset.CHARMAP_CP437)

    player = copy.deepcopy(entity_factories.player)
    engine = Engine(player=player)
    
    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
        engine=engine,
    )
    engine.update_fov()

    engine.message_log.add_message(
        "ALL SYSTEMS RECONNECTED: AWAKENING USER.", color.text_console
    )
    engine.message_log.add_message(
        "WARNING: DANGEROUS LIFEFORMS SIGNALS DETECTED.", color.text_console
    )
    engine.message_log.add_message(
        "TASK: GET OUT OF THIS PLACE!", color.text_console
    )

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Python RL",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console)
            context.present(root_console)

            try:
                for event in tcod.event.wait():
                    context.convert_event(event)
                    engine.event_handler.handle_events(event)
            except Exception:  # Handle exceptions in game.
                traceback.print_exc()  # Print error to stderr.
                # Then print the error to the message log.
                engine.message_log.add_message(traceback.format_exc(), color.error)

if __name__ == "__main__":
    main()