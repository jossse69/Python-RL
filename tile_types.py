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
        ("autotile", bool) # If the Tile will  be set to this symbols to make boders: ─│┌┐└┘
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    autotile: bool,
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, autotile), dtype=tile_dt)


floor = new_tile(
    walkable=True, transparent=True, dark=(ord("."), (102, 0, 51), (0, 0, 0)), autotile=False
)
wall = new_tile(
    walkable=False, transparent=False, dark=(ord(" "), (153, 0, 153), (0,0,0)), autotile=True
)