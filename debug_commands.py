import random
from engine import Engine
import entity_factories
registered_commands = {}
last_command = ""

def run_command(text: str, engine: Engine) -> str:
    """
    Run a command from the command line.
    """
    global last_command  # Declare last_command as a global variable

    # Split the command into its name and arguments.
    command, *args = text.lower().split()
    # Clear whitespace from the arguments and command
    command = command.strip()
    args = [arg.strip() for arg in args]

    # Check if the command is registered.
    if command in registered_commands.keys():
        message = registered_commands[command](engine, args)
        last_command = text.lower()
        return message
    else:
        return f"Invalid command: {command}"

    

class Command:
    """
    A command that can be run from the command line.
    """
    def __init__(self, name: str, help_text: str):
        self.name = name
        self.help_text = help_text
        registered_commands[name] = self

    def __call__(self, engine: Engine, args: list[str]) -> str:
        """
        Method once the command is run.

        This method must be overridden by subclasses.
        """
        raise NotImplementedError()
    

class HelpCommand(Command):
    """
    A command that lists all the commands.
    """
    def __init__(self):
        super().__init__("help", "List all the commands. Or list the help for a specific command.")

    def __call__(self, engine: Engine, args: list[str]) -> str:
        """
        List all the commands.
        """
        if not args:
            text = "Commands:\n"
            for command in registered_commands.values():
                text += f"{command.name}: {command.help_text}\n"
            return text
        else:
            command = args[0]
            if command in registered_commands:
                return registered_commands[command].help_text
            else:
                return f"Invalid command: {command}"
            
class SpawnCommand(Command):
    """
        spawns the selected entity near the player.
    """
    def __init__(self):
        super().__init__("spawn", "Spawns the selected entity near the player.")

    def __call__(self, engine: Engine, args: list[str]) -> str:
        """
        Spawns the selected entity near the player.
        """
        if not args:
            return "Usage: spawn <entity_name>"
        else:
            entity_type = args[0]
            # For each entity in entity_factories.ALL_ENTITIES, if the entity's name is the same as the entity_type, then spawn it.
            for entity in entity_factories.ALL_ENTITIES:
                if entity.internal_name == entity_type:
                    player_pos = (engine.player.x, engine.player.y)

                    # Get a free tile around 5 tiles away from the player.
                    pos = (player_pos[0] + random.randint(-5, 5), player_pos[1] + random.randint(-5, 5))

                    while not engine.game_map.get_blocking_entity_at_location(pos[0], pos[1]) and not engine.game_map.is_walkable_tile(pos[0], pos[1]):
                        pos = (player_pos[0] + random.randint(-5, 5), player_pos[1] + random.randint(-5, 5))

                    entity.spawn(engine.game_map, x=pos[0], y=pos[1])
                    return f"Spawned {entity_type} at ({engine.player.x}, {engine.player.y})."
            return f"Invalid entity: {entity_type}"

class RepeatCommand(Command):
    """
    Repeats the last command a number of times.
    """
    def __init__(self):
        super().__init__("repeat", "Repeats the last command a number of times.")

    def __call__(self, engine: Engine, args: list[str]) -> str:
        """
        Repeats the last command a number of times.
        """
        if not args:
            return "Usage: repeat <number_of_times>"
        else:
            try:
                number_of_times = int(args[0])
            except ValueError:
                return f"Invalid number of times: {args[0]}"
            if number_of_times < 1:
                return "Number of times must be at least 1."
            else:
                # Check if the last command was a repeat command.
                if last_command.startswith("repeat"):
                    return "Cannot repeat a repeat command."
                # Repeat the last command a number of times.
                for _ in range(number_of_times):
                    run_command(last_command, engine)
                return f"Repeating {last_command} {number_of_times} times."

class GodmodeCommand(Command):
    """
    Toggles godmode on or off.
    """
    def __init__(self):
        super().__init__("godmode", "Toggles godmode on or off.")

    def __call__(self, engine: Engine, args: list[str]) -> str:
        """
        Toggles godmode on or off.
        """
        if engine.game_world.godmode:
            engine.game_world.godmode = False
            return "Godmode off."
        else:
            engine.game_world.godmode = True
            return "Godmode on."

class GotoFloorCommand(Command):
    """
    Teleports the player to a specific floor. (Regenerates the map as well)
    """
    def __init__(self):
        super().__init__("goto", "Teleports the player to a specific floor. (Regenerates the map as well)")

    def __call__(self, engine: Engine, args: list[str]) -> str:
        """
        Teleports the player to a specific floor. (Regenerates the map as well)
        """
        if not args:
            return "Usage: goto <floor_number>"
        else:
            try:
                floor_number = int(args[0])
            except ValueError:
                return f"Invalid floor number: {args[0]}"
            if floor_number < 1:
                return "Floor number must be at least 1."
            else:
                engine.game_world.current_floor = floor_number
                engine.game_world.generate_floor()
                return f"Teleported to floor {floor_number}."

# Initialize all the commands.
HelpCommand()
SpawnCommand()
RepeatCommand()
GodmodeCommand()
GotoFloorCommand()