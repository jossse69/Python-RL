from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

player = Actor(
    char="@",
    color=(255, 255, 0),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=30, defense=2, power=5),
)

smile_mold = Actor(
    char="m", 
    color=(255, 80, 80), 
    name="Slime Mold", 
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
)
rusty_automaton = Actor(
    char="a",
    color=(200, 174, 137),
    name="Rusty Automaton",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
)