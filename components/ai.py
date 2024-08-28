from __future__ import annotations

import random
from typing import List, Optional, Tuple, TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction


if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action):

    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        # Copy the walkable array.
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            # Check that an enitiy blocks movement and the cost isn't zero (blocking.)
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Add to the cost of a blocked position.
                # A lower number means more enemies will crowd behind each other in
                # hallways.  A higher number means enemies will take longer paths in
                # order to surround the player.
                cost[entity.x, entity.y] += 10

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Start position.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]
    
class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Chebyshev distance.

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()
    
class ConfusedEnemy(BaseAI):
    """
    A confused enemy will stumble around aimlessly for a given number of turns, then revert back to its previous AI.
    If an actor occupies a tile it is randomly moving into, it will attack.
    """

    def __init__(
        self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int
    ):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Revert the AI back to the original state if the effect has run its course.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(
                f"The {self.entity.name} is no longer confused."
            )
            self.entity.ai = self.previous_ai
        else:
            # Pick a random direction
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

            self.turns_remaining -= 1

            # The actor will either try to move or attack in the chosen random direction.
            # Its possible the actor will just bump into the wall, wasting a turn.
            return BumpAction(self.entity, direction_x, direction_y,).perform()
    

class SpawnerEnemy(BaseAI):
    """
    A spawner enemy will spawn a new enemy (of the selected type) in a random location around it self. while trying to get distanced from the player.
    """

    def __init__(
        self, entity: Actor
    ):
        super().__init__(entity)

        self.is_setup = False
        self.flee_position = None

    def setup(self,spawned_entity: Actor, spawn_rate: int):
        self.spawned_entity = spawned_entity
        self.spawn_rate = spawn_rate
        self.spawn_timer = 0
        self.is_setup = True

    def perform(self) -> None:
        # Do not perform if this AI is not setup or the spawner is not visible.
        if not self.is_setup or not self.engine.game_map.visible[self.entity.x, self.entity.y]:
            return WaitAction(self.entity).perform()

        # If we are on the flee position, set it to none
        if self.flee_position and self.entity.x == self.flee_position[0] and self.entity.y == self.flee_position[1]:
            self.flee_position = None

        # If the spawn timer is greater than the spawn rate, spawn a new enemy.
        if self.spawn_timer >= self.spawn_rate:
            # Reset the spawn timer.
            self.spawn_timer = 0

            # Get a random location near the spawner.
            x = self.entity.x + random.randint(-3, 3)
            y = self.entity.y + random.randint(-3, 3)

            tries = 0
            while not self.engine.game_map.in_bounds(x, y) or not self.engine.game_map.get_blocking_entity_at_location(x, y):
                x = self.entity.x + random.randint(-3, 3)
                y = self.entity.y + random.randint(-3, 3)
                tries += 1
                if tries > 10:
                    return WaitAction(self.entity).perform() # If the spawner is not able to find a valid location, it will wait.
            
            # Spawn the new enemy.
            self.spawned_entity.spawn(self.engine.game_map, x, y)
            # Add a message to the message log.
            self.engine.message_log.add_message(
                f"The {self.entity.name} spawned a new {self.spawned_entity.name}!"
            )

        # Get the distance between the player and the spawner.
        distance = self.entity.distance(self.engine.player.x, self.engine.player.y)

        # If the distance is less than 5, move away from the player.
        if distance < 5:
            if not self.flee_position:
                # Get a flee position, that is around 20 tiles away.
                self.flee_position = (
                    self.entity.x + random.randint(-20, 20),
                    self.entity.y + random.randint(-20, 20),
                )

                while not self.engine.game_map.in_bounds(*self.flee_position) or self.engine.game_map.get_blocking_entity_at_location(*self.flee_position) or self.engine.game_map.tiles["walkable"][self.flee_position[0], self.flee_position[1]] == False:
                    self.flee_position = (
                        self.entity.x + random.randint(-20, 20),
                        self.entity.y + random.randint(-20, 20),
                    )
            
            # Get the direction to the flee position.
            self.path = self.get_path_to(self.flee_position[0], self.flee_position[1])

            if self.path:
                dest_x, dest_y = self.path.pop(0)
                return MovementAction(
                    self.entity, dest_x - self.entity.x, dest_y - self.entity.y,
                ).perform()

        # Add 1 to the spawn timer.
        self.spawn_timer += 1

        # Return a wait action.
        return WaitAction(self.entity).perform()