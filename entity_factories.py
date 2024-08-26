from components.ai import HostileEnemy, SpawnerEnemy
from components import consumable, equippable
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item
from components.equipment import Equipment

player = Actor(
    char="@",
    color=(255, 255, 0),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, base_dodge=5, base_power=2, base_defence=1),
    inventory=Inventory(capacity=26),
    inspect_message="It's yourself. What would you ask for?",
    level=Level(level_up_base=200),
    equipment=Equipment(),
)

slime_mold = Actor(
    char="m", 
    color=(255, 80, 80), 
    name="Slime Mold", 
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, base_dodge=0, base_power=3, base_defence=0),
    inventory=Inventory(capacity=0),
    inspect_message="It's a slime mold... That is alive! It looks hungry for your flesh.",
    level=Level(xp_given=35),
    equipment=Equipment(),
)
rusty_automaton = Actor(
    char="a",
    color=(200, 174, 137),
    name="Rusty Automaton",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, base_defence=1, base_power=4, base_dodge=4),
    inventory=Inventory(capacity=0),
    inspect_message="He looks like he's been here a while. I Won't say he's having a great time existing.",
    level=Level(xp_given=100),
    equipment=Equipment(),
)
hunter_humanoid = Actor(
    char="h",
    color=(244, 227, 210),
    name="Hunter Humanoid",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=20, base_defence=1, base_power=7, base_dodge=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=150),
    equipment=Equipment(),
    inspect_message="It's a mutated human, probably due to being exposed to irradiated places. It's now a reckless hunter, with sharp claws and skinny body, it wants to eat fresh flesh."
)
acid_mold = Actor(
    char="m",
    color=(0, 204, 102),
    name="Acid Mold",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=19, base_defence=2, base_power=6, base_dodge=5),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=50),
    equipment=Equipment(),
    inspect_message="It's a slime mold, but it's acidic. Don't touch it! It's pains to the touch."
)
mama_mold = Actor(
    char="M",
    color=(0, 204, 102),
    name="Mama Mold",
    ai_cls=SpawnerEnemy,
    fighter=Fighter(hp=30, base_defence=0, base_power=0, base_dodge=0),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=200),
    equipment=Equipment(),
    inspect_message="It's a big slime mold. It's trying to reproduce, and use its offspring to defend itself from you."
)
mama_mold.ai.setup(acid_mold, 8)

healing_gel = Item(
    char="!",
    color=(102, 255, 102),
    name="Healing Gel",
    consumable=consumable.HealingConsumable(amount=7),
    inspect_message="A Small, green-glowing piece of smile. It has a some-what apple taste.",
)
XL_healing_gel = Item(
    char="!",
    color=(0, 255, 0),
    name="XL Healing Gel",
    consumable=consumable.HealingConsumable(amount=18),
    inspect_message="A Extra Large healing Gel. Don't choke while gobbling it up!",
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
fireball_gun = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Gun",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
    inspect_message="It's a gun that shoots fireballs. Like the ones from fantasy games. It's pretty effective!",
)

pocket_kinfe = Item(    char="/", color=(102, 255, 255), name="Pocket kinfe", equippable=equippable.PocketKinfe(),
    inspect_message="The most pesonal kinfe you'll ever find. Use it if you're in a pinch."
)

old_kinfe = Item(
    char="/", color=(102, 255, 255), name="Old kinfe", equippable=equippable.OldKinfe(),
    inspect_message="It's a old rusty kitchen kinfe. It's not very sharp, but it's still effective."
)
sharp_kinfe = Item(char="/", color=(102, 255, 255), name="Sharp kinfe", equippable=equippable.SharpKinfe(),
    inspect_message="It's a kitchen kinfe that was not let outside at least."
)

scrap_chest_plate = Item(
    char="[",
    color=(102, 255, 255),
    name="Scrap chest plate",
    equippable=equippable.ScrapChestPlate(),
    inspect_message="It's a chest plate made of scrap metal. It's not very strong, but it's still effective.",
)
iron_chest_plate = Item(
    char="[",
    color=(102, 255, 255),
    name="Iron chest plate",
    equippable=equippable.IronChestPlate(),
    inspect_message="It's a chest plate made of iron. Put it on and you'll be able to take a beating.")

steel_chest_plate  = Item(
    char="[", color=(102, 255, 255), name="Steel chest plate", equippable=equippable.SteelChestPlate(),
    inspect_message="It's a chest plate, now made of steel. You'll be able to take quite the beating!"
)