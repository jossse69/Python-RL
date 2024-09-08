from typing import Tuple


white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# "The labs" tile colors
bg_lab = (0, 0, 45)
wall_lab = (153, 0, 153)
floor_lab = (102, 0, 51)

# "The grotto" tile colors
bg_grotto = (51, 51, 0)
wall_grotto = (0, 153, 51)
floor_grotto = (102, 153, 0)

current_bg = bg_lab
current_wall = wall_lab
current_floor = floor_lab

player_atk = (255, 153, 0)
enemy_atk = (153, 0, 0)
needs_target = (51, 153, 255)
status_effect_applied = (153, 0, 255)

player_die = (255, 0, 0)
enemy_die = (255, 255, 0)

invalid = (255, 255, 0)
impossible = (255, 153, 153)
error = (204, 0, 0)

text_console = (204, 255, 51)

bar_text = white
bar_filled = (255, 0, 0)
bar_empty = (77, 0, 0)

health_recovered = (102, 255, 102)

menu_title = (51, 153, 255)
menu_text = text_console
descend = (255, 204, 102)


def gray_scale_color(color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """Convert a color to grayscale."""
    # Calculate the grayscale value
    gray_value = sum(color) // 3
    
    # Create a new tuple with the grayscale value repeated three times
    gray_color = (gray_value, gray_value, gray_value)
    
    # Return the grayscale color
    return gray_color
