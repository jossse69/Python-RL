from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory
from entity import Actor, Item

player = Actor(
    char="@",
    color=(255, 255, 0),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
    inventory=Inventory(capacity=26),
    inspect_message="It's yourself. What would you ask for?",
)

smile_mold = Actor(
    char="m", 
    color=(255, 80, 80), 
    name="Slime Mold", 
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
    inventory=Inventory(capacity=0),
    inspect_message="It's a slime mold... That is alive! It looks hungry for your flesh.",
)
rusty_automaton = Actor(
    char="a",
    color=(200, 174, 137),
    name="Rusty Automaton",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
    inventory=Inventory(capacity=0),
    inspect_message="He looks like he's been here a while. I Won't say he's having a great time existing.",
)

healing_gel = Item(
    char="!",
    color=(102, 255, 102),
    name="Healing Gel",
    consumable=consumable.HealingConsumable(amount=4),
    inspect_message="A Small, green-glowing piece of smile. It has a some-what apple taste.",
)
taser = Item(
    char="~",
    color=(255, 255, 0),
    name="Taser",
    consumable=consumable.EletricDamageConsumable(damage=20, maximum_range=5),
    inspect_message="It's a bit old, and it's bolts go to whatever they want, but it's still effective.",
)
stun_gun = Item(
    char="~",
    color=(153, 0, 255),
    name="Stun Gun",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
    inspect_message="Bright flashes always makes everyone disoriented. I'd get confused if i were to look at it.",
)
fireball_Gun = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Gun",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
    inspect_message="It's a gun that shoots fireballs. Like the ones from fantasy games. It's pretty effective!",
)