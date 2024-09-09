from __future__ import annotations

import random
from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union

import tcod.event
from tcod import libtcodpy
from tcod.console import Console
import copy

import actions
from actions import (
    Action,
    BumpAction,
    PickupAction,
    WaitAction,
    MovementAction
)
import color
import exceptions
import os
import threading
from debug_commands import run_command

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item


MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys.
    tcod.event.KeySym.h: (-1, 0),
    tcod.event.KeySym.j: (0, 1),
    tcod.event.KeySym.k: (0, -1),
    tcod.event.KeySym.l: (1, 0),
    tcod.event.KeySym.y: (-1, -1),
    tcod.event.KeySym.u: (1, -1),
    tcod.event.KeySym.b: (-1, 1),
    tcod.event.KeySym.n: (1, 1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
}

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.rgb["fg"] //= 4
        console.rgb["bg"] //= 4

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.text_console,
            bg=color.black,
            alignment=libtcodpy.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler."""
        return self.parent

class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            
            # Did the action set the future_event_handler attribute? If so, change the current handler.
            if self.engine.future_event_handler is not None:
                handler = self.engine.future_event_handler
                self.engine.future_event_handler = None
                return handler

            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False  # Skip enemy turn on exceptions.


        self.engine.handle_enemy_turns()
        self.engine.handle_status_effects()
        self.engine.handle_zones()
        self.engine.update_fov()
        return True

    
    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod

        player = self.engine.player

        if key == tcod.event.KeySym.PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)
        
        if self.engine.game_world.player_confused_turns > 0:
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
            if self.engine.game_map.is_walkable_tile(player.x + direction_x, player.y + direction_y):
                action = MovementAction(player, direction_x, direction_y)

            self.engine.game_world.player_confused_turns = max(0, self.engine.game_world.player_confused_turns - 1)

            if self.engine.game_world.player_confused_turns == 0:
                self.engine.message_log.add_message(
                    "You get back to your sences.",
                )


            return action # Make the player be unable to move or do anything else while confused.

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
        elif key == tcod.event.KeySym.v:
            return HistoryViewer(self.engine)
        elif key == tcod.event.KeySym.g:
            action = PickupAction(player)
        elif key == tcod.event.KeySym.i:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.KeySym.SLASH:
            return LookHandler(self.engine)
        elif key == tcod.event.KeySym.c:
            return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.KeySym.N0:
            return DebugCommandLineEventHandler(self.engine, self)


        # No valid key was pressed
        return action
    
    def on_render(self, console: Console) -> None:
        super().on_render(console)

        if self.engine.game_world.player_confused_turns > 0:
            # Draw a "YOU ARE CONFUSED!" message at the center of the screen.
            console.rgb["fg"] //= 4
            console.rgb["bg"] //= 4
            console.print(
                console.width // 2,
                console.height // 2,
                "YOU ARE CONFUSED!",
                fg=color.status_effect_applied,
                bg=color.black,
                alignment=libtcodpy.CENTER,
            )
            console.print(
                console.width // 2,
                (console.height // 2) + 1,
                "(press any key to continue a turn)",
                fg=color.status_effect_applied,
                bg=color.black,
                alignment=libtcodpy.CENTER,
            )
    
class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            self.on_quit()
    
CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.console.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height, fg=color.text_console)
        log_console.print_box(
            0, 0, log_console.width, 1, "MESSAGE LOG HISTORY", alignment=libtcodpy.CENTER,bg=color.text_console, fg=color.black
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None

class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)
    
class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """

    TITLE = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE.upper(),
            clear=True,
            fg=color.text_console,
            bg=(0, 0, 0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f"({item_key}) {item.name}"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                console.print(x + 1, y + i + 1, item_string.upper(), fg=color.text_console)

        else:
            console.print(x + 1, y + 1, "(EMPTY)", fg=color.text_console)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()
    
class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return actions.EquipAction(self.engine.player, item)
        else:
            return None


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return actions.DropItem(self.engine.player, item)
    
class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = color.white
        console.rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler, and inspect the enity at this location, if any."""

        for entity in self.engine.game_map.entities:
            if entity.x == x and entity.y == y:
                self.engine.message_log.add_message(entity.inspect_message.upper(), color.text_console)
                return MainGameEventHandler(self.engine)
        self.engine.message_log.add_message("THERE'S NOTHING HERE THAT I CAN INSPECT.", color.error)
        return MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))
    
class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x=x - self.radius,
            y=y - self.radius,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))
    
class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "LEVEL++!"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=color.text_console,
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=1, fg=color.text_console, string="Congratulations!".upper())
        console.print(x=x + 1, y=2, fg=color.text_console, string="Select an attribute to increase.".upper())


        console.print(
            x=x + 1,
            y=4,
            fg=color.text_console,
            string=f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})".upper(),
        )
        console.print(
            x=x + 1,
            y=5,
            fg=color.text_console,
            string=f"b) Strength (+1 attack, from {self.engine.player.fighter.power})".upper(),
        )
        console.print(
            x=x + 1,
            y=6,
            fg=color.text_console,
            string=f"c) Agility (+5% dodge chance, from {self.engine.player.fighter.dodge}%)".upper(),
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 2:
            if index == 0:
                player.level.increase_max_hp()
            elif index == 1:
                player.level.increase_power()
            else:
                player.level.increase_dodge(5)
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)

            return None

        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """
        Don't allow the player to click to exit the menu, like normal.
        """
        return None
    
class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "CHARACTER STATUS"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=color.text_console,
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 1, fg=color.text_console, string=f"Level: {self.engine.player.level.current_level}".upper()
        )
        console.print(
            x=x + 1, y=y + 2, fg=color.text_console, string=f"XP: {self.engine.player.level.current_xp}".upper()
        )
        console.print(
            x=x + 1,
            y=y + 3,
            fg=color.text_console,
            string=f"XP for next Level: {self.engine.player.level.experience_to_next_level}".upper(),
        )

        console.print(
            x=x + 1, y=y + 4, fg=color.text_console, string=f"Attack: {self.engine.player.fighter.power}".upper()
        )
        console.print(
            x=x + 1, y=y + 5, fg=color.text_console, string=f"Defense: {self.engine.player.fighter.defense}".upper()
        )
        console.print(
            x=x + 1, y=y + 6,  fg=color.text_console, string=f"Dodge chance: {self.engine.player.fighter.dodge}%".upper()
            )
        

class SellItemsEventHandler(InventoryEventHandler):
    TITLE = "WHAT TO SELL?"

    def __init__(self, engine: actions.Engine, previous_handler: EventHandler):
        super().__init__(engine)

        self.previous_handler = previous_handler

    def on_exit(self) -> Action | BaseEventHandler | None:
        return self.previous_handler
    
    def on_item_selected(self, item: actions.Item) -> Action | BaseEventHandler | None:
        # TODO: Sell the item.
        self.engine.player.inventory.remove(item)
        # If the player is eqiupping the item, then remove it from the equipment.
        if self.engine.player.equipment.weapon == item:
            self.engine.player.equipment.toggle_equip(item)
        elif self.engine.player.equipment.armor == item:
            self.engine.player.equipment.toggle_equip(item)

        self.engine.message_log.add_message(f"You sold the {item.name} for {item.value} Credits.", color.health_recovered)

        # Add the credits to the player.
        self.engine.game_world.credits += item.value

        return self.previous_handler # Return to the previous handler.


class BuyItemsEventHandler(AskUserEventHandler):
    TITLE = "WHAT TO BUY?"

    def __init__(self, engine: actions.Engine, previous_handler: EventHandler):
        super().__init__(engine)

        from entity_factories import healing_gel, XL_healing_gel, taser
        self.previous_handler = previous_handler
        self.items = [
            copy.deepcopy(healing_gel),
            copy.deepcopy(XL_healing_gel),
            copy.deepcopy(taser) 
        ]

    def on_exit(self) -> Action | BaseEventHandler | None:
        return self.previous_handler
    
    def on_render(self, console: tcod.event.Any) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 19

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=16,
            title=self.TITLE,
            clear=True,
            fg=color.text_console,
            bg=(0, 0, 0),
        )

        # Draw the avaible items in a list, similar to the inventory menu.
        # TODO: Add the items in, for now its placeholder items.
        for i, item in enumerate(self.items):
            item_key = chr(ord("a") + i)
            console.print(
                x=x + 1,
                y=y + 1 + i,
                fg=color.text_console,
                string=f"{item_key}) {item.name} - {item.value} Credit".upper(),
            )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 2:
            item = copy.deepcopy(self.items[index])

            if self.engine.game_world.credits >= item.value:
                player.inventory.add(item)
                self.engine.message_log.add_message(f"You bought the {item.name} for {item.value} Credits.", color.health_recovered)
                self.engine.game_world.credits -= item.value
            else:
                self.engine.message_log.add_message("You don't have enough credits.", color.invalid)
            

        elif key != tcod.event.KeySym.ESCAPE:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)

        
        return super().ev_keydown(event)
                


class ShopkeepMenuEventHandler(AskUserEventHandler):
    TITLE = "SHOP"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width + 29,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=color.text_console,
            bg=(0, 0, 0),
        )

        # Draw a text wellcome text.
        console.print(x=x + 1, y=y + 1, fg=color.text_console, string="'What can i do to ya, Human?'")

        # Draw options. (Sell or Buy items)
        console.print(x=x + 1, y=y + 3, fg=color.text_console, string="a) Sell items".upper())
        console.print(x=x + 1, y=y + 4, fg=color.text_console, string="b) Buy items".upper())

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 1:
            if index == 0:
                return SellItemsEventHandler(self.engine, self)
            else:
                return BuyItemsEventHandler(self.engine, self)
        elif key != tcod.event.KeySym.ESCAPE:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
        else:
            self.engine.message_log.add_message("You leave the shop.")


        return super().ev_keydown(event)
    

class DebugCommandLineEventHandler(AskUserEventHandler):
    def __init__(self, engine: actions.Engine, previous_handler: EventHandler):
        super().__init__(engine)
        self.text = ""
        self.frist_input = True
        self.previous_handler = previous_handler
        self.message = "Hello! Welcome to this not-so-secret debug command line! \n Type 'help' for a list of commands."

    def on_exit(self) -> Action | BaseEventHandler | None:
        return self.previous_handler

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        if key == tcod.event.KeySym.ESCAPE:
            return self.on_exit()
        elif key == tcod.event.KeySym.RETURN:
            self.message = run_command(self.text, self.engine)
            self.text = ""
        elif key == tcod.event.KeySym.BACKSPACE:
            self.text = self.text[:-1]
        return None
    
    def ev_textinput(self, event: tcod.event.TextInput) -> Optional[ActionOrHandler]:
        if self.frist_input:
            self.frist_input = False
            return None
        self.text += event.text
        return None

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        console.clear()

        x = 2
        y = 2

        display_text = f"> {self.text}"

        console.print(x=x, y=y, fg=color.text_console, string=display_text)

        # Print the message one character at a time. And also handling line breaks.
        y += 2
        for i, line in enumerate(self.message.split("\n")):
            console.print(x=x, y=y + i, fg=color.text_console, string=line)






