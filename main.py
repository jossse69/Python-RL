#!/usr/bin/env python3
import tcod

from actions import EscapeAction, MovementAction
from input_handlers import EventHandler

def main():
    screen_width = 80
    screen_height = 50

    player_x = int(screen_width / 2)
    player_y = int(screen_height / 2)

    tileset = tcod.tileset.load_tilesheet("data/zaratustra_msx.png", 16, 16, tcod.tileset.CHARMAP_CP437)

    event_handler = EventHandler()

    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="Python RL",
        vsync=True,
    ) as context:
        root_console = tcod.console.Console(screen_width, screen_height, order="F")
        while True:
            root_console.print(x=player_x, y=player_y, string="@")

            context.present(root_console)

            root_console.clear()

            for event in tcod.event.wait():
                action = event_handler.dispatch(event)

                if action is None:
                    continue

                if isinstance(action, MovementAction):
                    player_x += action.dx
                    player_y += action.dy

                elif isinstance(action, EscapeAction):
                    raise SystemExit()



if __name__ == "__main__":
    main()