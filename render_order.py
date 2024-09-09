from enum import auto, Enum


class RenderOrder(Enum):
    CORPSE = auto()
    ZONE = auto()
    ITEM = auto()
    ACTOR = auto()