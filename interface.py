# Game Interface
# Connects the game logic (main.py) with the TUI library (tui.py).

import libraries.tui as tui
from libraries.tui import Colors
import textwrap


# --- Formatting and Display Functions ---

def display_header(text):
    tui.clear_screen()
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}======================================{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}{text.center(38)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}======================================{Colors.ENDC}\n")


def display_message(message, color=Colors.WHITE, wait_for_key=False):
    """
    Displays a simple message to the player.

    Args:
        message (str): The text to display.
        color (str): An ANSI color code from the Colors class.
        wait_for_key (bool): If True, pauses until the user presses a key.
    """
    print(f"{color}{message}{Colors.ENDC}")
    if wait_for_key:
        print(f"\n{Colors.BRIGHT_CYAN}Press any key to continue...{Colors.ENDC}")
        tui.get_key()


def format_location(location):
    lines = [f"{Colors.BOLD}{Colors.BRIGHT_CYAN}--- {location.name} ---{Colors.ENDC}"]
    # Wrap the description for better readability on small terminals
    wrapped_desc = textwrap.wrap(location.description, width=60)
    for line in wrapped_desc:
        lines.append(f"{Colors.BLUE}{line}{Colors.ENDC}")

    lines.append("")
    if location.items:
        lines.append(f"  You see: {Colors.BRIGHT_GREEN}{', '.join(location.items)}{Colors.ENDC}")
    if location.enemies:
        lines.append(f"  Danger nearby: {Colors.BRIGHT_RED}{', '.join(location.enemies)}{Colors.ENDC}")

    # Create a consistent underline based on the location name length
    underline = '-' * (len(location.name) + 6)
    lines.append(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{underline}{Colors.ENDC}")
    return "\n".join(lines)


def display_status(player):
    tui.clear_screen()
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}--- {player.name}'s Status ---{Colors.ENDC}")
    print(f"  HP: {Colors.BRIGHT_GREEN}{player.hp}/{player.max_hp}{Colors.ENDC}")
    inventory_str = ', '.join(player.inventory) or 'Empty'
    print(f"  Inventory: {Colors.BRIGHT_BLUE}{inventory_str}{Colors.ENDC}")
    print(f"  Skills:")
    for skill, value in player.skills.items():
        print(f"    - {skill}: {Colors.BRIGHT_CYAN}{value}{Colors.ENDC}")
    print(f"  Location: {Colors.BRIGHT_BLUE}{player.location}{Colors.ENDC}")
    print(f"  {Colors.BOLD}Active Quests:{Colors.ENDC}")
    if player.current_quests:
        for quest_name, quest_def in player.get_current_quest_details():
            desc = quest_def.get('description', 'No description.')
            progress = player.get_quest_progress(quest_name)
            print(f"    - {Colors.BRIGHT_YELLOW}{quest_name}{Colors.ENDC}: {desc}{Colors.WHITE}{progress}{Colors.ENDC}")
    else:
        print(f"    {Colors.BRIGHT_BLUE}None{Colors.ENDC}")

    completed_str = ', '.join(player.completed_quests) or 'None'
    print(f"  Completed Quests: {Colors.BRIGHT_GREEN}{completed_str}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}--------------------------{Colors.ENDC}")
    display_message("", wait_for_key=True)


# --- Prompt & Selection Functions ---

def prompt_new_or_load():
    title = "Welcome to the ASCII RPG Adventure!"
    options = ["New Game", "Load Game"]
    choice = tui.menu(title, options)
    if choice == "New Game":
        return "n"
    elif choice == "Load Game":
        return "l"
    return None


def prompt_for_name():
    tui.clear_screen()
    display_header("Create Your Character")
    name = input(f"Enter your name ({Colors.BRIGHT_BLUE}Adventurer{Colors.ENDC}): {Colors.BRIGHT_BLUE}").strip()
    print(Colors.ENDC, end='')
    return name if name else "Adventurer"


def select_from_list(title, items, prompt="Select an option", add_cancel=True):
    options = list(items)
    if add_cancel:
        options.append("Cancel")

    choice = tui.menu(title, options, prompt)

    if choice == "Cancel" or choice is None:
        return None
    return choice


def prompt_action(player, location):
    # Dynamically generate the list of available actions.
    actions = []
    if location.items:
        actions.append(f"Take an item")
    if location.enemies:
        actions.append(f"Fight an enemy")

    actions.extend(["Move to a new area", "View Status", "Eat an item", "View Quests", "Save Game", "Quit Game"])

    location_header = format_location(location)

    return tui.menu(
        title=f"What will {player.name} do?",
        options=actions,
        header_text=location_header
    )
