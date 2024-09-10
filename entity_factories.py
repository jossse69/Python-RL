

from components.ai import HostileEnemy, SpawnerEnemy, ZoneSpawnerEnemy, InvisblePouncerEnemy
from components import consumable, equippable
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import NPC, Actor, Item, Zone
from components.equipment import Equipment
from input_handlers import ShopkeepMenuEventHandler
from status_effect import Poisoned, Bleeding, Spored
from components.zone import HydrogenSulfideGas, NitrousOxideGas, SporeAir
from npc_handler import ShopKeeperHandler

ALL_ENTITIES = []

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
ALL_ENTITIES.append(player)
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
ALL_ENTITIES.append(slime_mold)
rusty_automaton = Actor(
    char="a",
    color=(200, 174, 137),
    name="Rusty Automaton",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, base_defence=1, base_power=4, base_dodge=4, immune_effects=[Poisoned, Bleeding]),
    inventory=Inventory(capacity=0),
    inspect_message="He looks like he's been here a while. I Won't say he's having a great time existing.",
    level=Level(xp_given=100),
    equipment=Equipment(),
)
ALL_ENTITIES.append(rusty_automaton)
hunter_humanoid = Actor(
    char="h",
    color=(244, 227, 210),
    name="Hunter Humanoid",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=20, base_defence=1, base_power=7, base_dodge=10),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=150),
    equipment=Equipment(),
    inspect_message="It's a mutated human, probably due to being exposed to irradiated places. It's now a reckless hunter, with sharp claws and skinny body, it wants to eat fresh flesh.",
    effect=Bleeding(duration=6, value=1),
)
ALL_ENTITIES.append(hunter_humanoid)
acid_mold = Actor(
    char="m",
    color=(0, 204, 102),
    name="Acid Mold",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=19, base_defence=2, base_power=6, base_dodge=5, immune_effects=[Poisoned]),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=50),
    equipment=Equipment(),
    inspect_message="It's a slime mold, but it's acidic. Don't touch it! It's hurts to the touch.",
    effect=Poisoned(duration=4, value=1),
)
ALL_ENTITIES.append(acid_mold)
mama_mold = Actor(
    char="M",
    color=(0, 204, 102),
    name="Mama Mold",
    ai_cls=SpawnerEnemy,
    fighter=Fighter(hp=30, base_defence=0, base_power=0, base_dodge=0, immune_effects=[Poisoned]),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=200),
    equipment=Equipment(),
    inspect_message="It's a big slime mold. It's trying to reproduce, and use its offspring to defend itself from you."
)
mama_mold.ai.setup(acid_mold, 8)
ALL_ENTITIES.append(mama_mold)
healing_gel = Item(
    char="!",
    color=(102, 255, 102),
    name="Healing Gel",
    consumable=consumable.HealingConsumable(amount=7),
    inspect_message="A Small, green-glowing piece of smile. It has a some-what apple taste.",
    value=10,
)
ALL_ENTITIES.append(healing_gel)
xl_healing_gel = Item(
    char="!",
    color=(0, 255, 0),
    name="XL Healing Gel",
    consumable=consumable.HealingConsumable(amount=18),
    inspect_message="A Extra Large healing Gel. Don't choke while gobbling it up!",
    value=25,
)
ALL_ENTITIES.append(xl_healing_gel)
taser = Item(
    char="~",
    color=(255, 255, 0),
    name="Taser",
    consumable=consumable.EletricDamageConsumable(damage=20, maximum_range=5),
    inspect_message="It's a bit old, and it's bolts go to whatever they want, but it's still effective.",
    value=30,
)
ALL_ENTITIES.append(taser)
stun_gun = Item(
    char="~",
    color=(153, 0, 255),
    name="Stun Gun",
    consumable=consumable.ConfusionConsumable(number_of_turns=10),
    inspect_message="Bright flashes always makes everyone disoriented. I'd get confused if i were to look at it.",
    value=10,
)
ALL_ENTITIES.append(stun_gun)
fireball_gun = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Gun",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
    inspect_message="It's a gun that shoots fireballs. Like the ones from fantasy games. It's pretty effective!",
    value=50,
)
ALL_ENTITIES.append(fireball_gun)
pocket_kinfe = Item(    char="/", color=(102, 255, 255), name="Pocket kinfe", equippable=equippable.PocketKinfe(),
    inspect_message="The most pesonal kinfe you'll ever find. Use it if you're in a pinch.",
    value=10,
)
ALL_ENTITIES.append(pocket_kinfe)
old_kinfe = Item(
    char="/", color=(102, 255, 255), name="Old kinfe", equippable=equippable.OldKinfe(),
    inspect_message="It's a old rusty kitchen kinfe. It's not very sharp, but it's still effective.",
    value=50,
)
ALL_ENTITIES.append(old_kinfe)
acid_kinfe = Item(
    char="/", color=(102, 255, 255), name="Acid kinfe", equippable=equippable.AcidKinfe(),
    inspect_message="It's kinfe that's acidic. Be careful when holding it!",
    value=75,
)
ALL_ENTITIES.append(acid_kinfe)
sharp_kinfe = Item(char="/", color=(102, 255, 255), name="Sharp kinfe", equippable=equippable.SharpKinfe(),
    inspect_message="It's a kitchen kinfe that was not let outside at least.",
    value=100,
)
ALL_ENTITIES.append(sharp_kinfe)
professional_acid_kinfe = Item(
    char="/",
    color=(102, 255, 255),
    name="Professional acid kinfe",
    equippable=equippable.ProfessionalAcidKinfe(),
    inspect_message="It's a acid kinfe that's been professionally made, for all kinds of industries. Very useful!",
    value=150,
)
ALL_ENTITIES.append(professional_acid_kinfe)
scrap_chest_plate = Item(
    char="[",
    color=(102, 255, 255),
    name="Scrap chest plate",
    equippable=equippable.ScrapChestPlate(),
    inspect_message="It's a chest plate made of scrap metal. It's not very strong, but it's still effective.",
    value=25,
)
ALL_ENTITIES.append(scrap_chest_plate)
iron_chest_plate = Item(
    char="[",
    color=(102, 255, 255),
    name="Iron chest plate",
    equippable=equippable.IronChestPlate(),
    inspect_message="It's a chest plate made of iron. Put it on and you'll be able to take a beating.",
    value=50,
)
ALL_ENTITIES.append(iron_chest_plate)
spikey_chest_plate = Item(
    char="[", color=(102, 255, 255), name="Spikey chest plate", equippable=equippable.SpikeyChestPlate(),
    inspect_message="It's a iron chest plate, but it's covered in spikes. Anyone that tries to attack you with it will be bleeding heavily!",
    value=80,
)
ALL_ENTITIES.append(spikey_chest_plate)
steel_chest_plate  = Item(
    char="[", color=(102, 255, 255), name="Steel chest plate", equippable=equippable.SteelChestPlate(),
    inspect_message="It's a chest plate, now made of steel. You'll be able to take quite the beating!",
    value=100,
)
ALL_ENTITIES.append(steel_chest_plate)
steelpike_chest_plate = Item(
    char="[",
    color=(102, 255, 255),
    name="Steelpike chest plate",
    equippable=equippable.SteelPikeChestPlate(),
    inspect_message="Steel chest plate + spikes = this. Quite a good one if i say so myself!",
    value=140,
)
ALL_ENTITIES.append(steelpike_chest_plate)
acid_metal_chest_plate = Item(
    char="[",
    color=(102, 255, 255),
    name="Acid metal chest plate",
    equippable=equippable.AcidMetalChestPlate(),
    inspect_message="It's a chest plate made of acid metal. I don't know the chemistry of this material, but it's corrosive on touch, like a lot of acid.",
    value=185,
)
ALL_ENTITIES.append(acid_metal_chest_plate)
shopkeep_npc = NPC(
    char="@",
    color=(102, 255, 102),
    name="Shop Keeper",
    npc_handler_cls=ShopKeeperHandler,
    input_handler_cls=ShopkeepMenuEventHandler,
    inspect_message="It's a shop keeper. He's a friendly humanoid robot. He's selling some items. At least some freind in this world.",
)
ALL_ENTITIES.append(shopkeep_npc)
hydrogen_sulfide_gas = Zone(
    char="▒",
    color=(204, 204, 0),
    name="Hydrogen Sulfide Gas",
    inspect_message="It's a gas that's made of hydrogen sulfide. It's very toxic!",
    duration=10,
    is_permanent=False,
    zone_component=HydrogenSulfideGas,
    moves_around=True
)
ALL_ENTITIES.append(hydrogen_sulfide_gas)
poison_gas_granade = Item(
    char="*",
    color=(204, 204, 0),
    name="Poison gas granade",
    consumable=consumable.GasGranadeConsumable(radius=5, zone=hydrogen_sulfide_gas),
    inspect_message="It's a granade that has toxic gas in it. It's very effective at killing stuff at masses.",
    value=50,
)
ALL_ENTITIES.append(poison_gas_granade)
nitrous_oxide_gas = Zone(
    char="▒",
    color=(153, 0, 255),
    name="Nitrous Oxide Gas",
    inspect_message="It's a gas that's made of nitrous oxide. It makes creatures dizzy, so don't fool around in there!",
    duration=10,
    is_permanent=False,
    zone_component=NitrousOxideGas,
    moves_around=True
)
ALL_ENTITIES.append(nitrous_oxide_gas)
stun_gas_granade = Item(
    char="*",
    color=(153, 0, 255),
    name="Stun gas granade",
    consumable=consumable.GasGranadeConsumable(radius=5, zone=nitrous_oxide_gas),
    inspect_message="It's a granade that has a gas that makes you dizzy. Just, don't inhale it to test if it's effective.",
    value=50,
)
ALL_ENTITIES.append(stun_gas_granade)
baby_shroom = Actor(
    char="s",
    color=(255, 153, 0),
    name="Baby Shroom",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=20, base_power=4, base_dodge=0, immune_effects=[Spored], base_defence=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
    equipment=Equipment(),
    inspect_message="It's a small walking fungi with a orange cap. It appears to be part of a great linage of mushrooms. It's very cute, but it's also very dangerous.",
)
ALL_ENTITIES.append(baby_shroom)
spore_filled_air = Zone(
    char="▒",
    color=(255, 153, 0),
    name="Spore filled air",
    inspect_message="It's a cloud full of spores. They look sticky, and they will probably crawl under your skin for a while... Yikes...",
    duration=10,
    is_permanent=False,
    zone_component=SporeAir,
    moves_around=True
)
ALL_ENTITIES.append(spore_filled_air)
bloom_shroom = Actor(
    char="S",
    color=(255, 153, 0),
    name="Bloom Shroom",
    ai_cls=ZoneSpawnerEnemy,
    fighter=Fighter(hp=30, base_power=6, base_dodge=0, immune_effects=[Spored], base_defence=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=200),
    equipment=Equipment(),
    inspect_message="It's a large mushroom, like the little baby ones. It's releasing spores like it's a breeding season! Is that a bad thing?",
)
bloom_shroom.ai.setup(spore_filled_air, 3)
ALL_ENTITIES.append(bloom_shroom)
wild_hunter_humanoid = Actor(
    char="h",
    color=(51, 0, 51),
    name="Wild Hunter Humanoid",
    ai_cls=InvisblePouncerEnemy,
    fighter=Fighter(hp=30, base_power=4, base_dodge=15, base_defence=2),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=250),
    equipment=Equipment(),
    inspect_message="It's a hunter humanoid that looks a lot more scarier! Dark fur, red blood eyes and long fangs make it look like a monster.",
)
wild_hunter_humanoid.ai.setup(HostileEnemy, 5)
ALL_ENTITIES.append(wild_hunter_humanoid)