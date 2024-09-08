from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from entity import Actor
from equipment_types import EquipmentType
from status_effect import Poisoned, Bleeding

if TYPE_CHECKING:
    from entity import Item
    from entity import Actor



class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        power_bonus: int = 0,
        defense_bonus: int = 0,
        dodge_bonus: int = 0,
    ):
        self.equipment_type = equipment_type

        self.power_bonus = power_bonus
        self.defense_bonus = defense_bonus
        self.dodge_bonus = dodge_bonus


    def on_equip(self, parent: Actor) -> None:
        """
        Called when this equippable is equipped.

        This method must be overridden by subclasses.
        """
        pass

    def on_unequip(self, parent: Actor) -> None:
        """
        Called when this equippable is unequipped.

        This method must be overridden by subclasses.
        """
        pass

    def on_attack(self, target: Actor):
        """
        Called when this weapon is used to attack a target.

        This method must be overridden by subclasses.
        """
        pass

    def on_hit(self, target: Actor, damage: int):
        """
        Called when this armor's parent is attacked by a target.

        This method must be overridden by subclasses.
        """
        pass

class PocketKinfe(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=1)

class OldKinfe(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=2)

class AcidKinfe(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=3)

    def on_attack(self, target: Actor):
        # Add the poisoned status effect to the target.
        target.fighter.apply_status_effect(Poisoned(duration=6, value=1))

class SharpKinfe(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=4)

class ProfessionalAcidKinfe(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.WEAPON, power_bonus=5)

    def on_attack(self, target: Actor):
        # Add the poisoned status effect to the target.
        target.fighter.apply_status_effect(Poisoned(duration=8, value=2))

class ScrapChestPlate(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=1)

class IronChestPlate(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=2)

class SpikeyChestPlate(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=2)
    
    def on_hit(self, target: Actor, damage: int):
        # Add the bleeding status effect to the target.
        target.fighter.apply_status_effect(Bleeding(duration=6, value=damage // 2))
        # make the target take 2 damage
        target.fighter.take_damage(2)
        
class SteelChestPlate(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=3)

class SteelPikeChestPlate(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=4)

    def on_hit(self, target: Actor, damage: int):
        # Add the bleeding status effect to the target.
        target.fighter.apply_status_effect(Bleeding(duration=6, value=damage // 2))
        # make the target take 4 damage
        target.fighter.take_damage(4)

class AcidMetalChestPlate(Equippable):
    def __init__(self) -> None:
        super().__init__(equipment_type=EquipmentType.ARMOR, defense_bonus=5)

    def on_hit(self, target: Actor, damage: int):
        # Add the poisoned status effect to the target.
        target.fighter.apply_status_effect(Poisoned(duration=6, value=2))