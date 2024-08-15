from typing import Tuple

import numpy as np  # type: ignore

# Tile graphics structured type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", bool),  # True if this tile can be walked over.
        ("transparent", bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when the tile is in FOV.
        ("autotile", bool), # If the Tile will  be set to this symbols to make boders: ─│┌┐└┘
    ]
)

# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    autotile: bool,
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light, autotile), dtype=tile_dt)


floor = new_tile(
    walkable=True, transparent=True, light=(ord("."), (102, 0, 51), (0, 0, 0)), dark=(ord("."), (51, 51, 51), (0, 0, 0)), autotile=False
)
wall = new_tile(
    walkable=False, transparent=False, light=(ord(" "), (153, 0, 153), (0,0,0)), dark=(ord(" "), (51, 51, 51), (0, 0, 0)), autotile=True
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (0, 100, 100), (0, 0 ,0)),
    light=(ord(">"), (255, 204, 102), (0, 0, 0)),
    autotile=False
)