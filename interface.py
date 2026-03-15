# Game Interface
# Connects the game logic (main.py) with the TUI library (tui.py).

import libraries.tui as tui
from libraries.tui import Colors
import textwrap
import shutil
import re

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


def get_dynamic_width():
    term_width = shutil.get_terminal_size((80, 24)).columns
    return max(50, min(term_width - 4, 80))


def get_vis_len(text):
    return len(ANSI_ESCAPE.sub('', text))


def pad_string(text, width, align='left'):
    vis_len = get_vis_len(text)
    total_pad = width - vis_len

    if total_pad <= 0:
        return text

    if align == 'left':
        return text + (' ' * total_pad)
    elif align == 'right':
        return (' ' * total_pad) + text
    elif align == 'center':
        pad_left = total_pad // 2
        pad_right = total_pad - pad_left
        return (' ' * pad_left) + text + (' ' * pad_right)
    return None


def format_list_lines(prefix, items, color, inner_width):
    """Wraps lists (like items or enemies) dynamically so they don't break borders."""
    lines = []
    current_line = f"{Colors.WHITE}{prefix}{color}"
    current_vis_len = len(prefix)

    for i, item in enumerate(items):
        item_str = item + (", " if i < len(items) - 1 else "")
        # If adding this item exceeds the width, wrap to a new line
        if current_vis_len + len(item_str) > inner_width and current_vis_len > len(prefix):
            lines.append(current_line + Colors.ENDC)
            indent = " " * len(prefix)
            current_line = f"{Colors.WHITE}{indent}{color}{item_str}"
            current_vis_len = len(prefix) + len(item_str)
        else:
            current_line += item_str
            current_vis_len += len(item_str)

    if current_vis_len > 0:
        lines.append(current_line + Colors.ENDC)
    return lines


# --- Formatting and Display Functions ---

def display_header(text):
    tui.clear_screen()
    WIDTH = get_dynamic_width()
    border = f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╔{'═' * (WIDTH - 2)}╗{Colors.ENDC}"
    bottom = f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╚{'═' * (WIDTH - 2)}╝{Colors.ENDC}"
    print(border)

    padded_text = pad_string(text, WIDTH - 2, 'center')
    print(
        f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║{Colors.BRIGHT_YELLOW}{padded_text}"
        f"{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")
    print(bottom + "\n")


def display_message(message, color=Colors.WHITE, wait_for_key=False):
    if message:
        print(f"{color}{message}{Colors.ENDC}")
    if wait_for_key:
        print(f"\n{Colors.BRIGHT_CYAN}➤ Press any key to continue...{Colors.ENDC}")
        tui.get_key()


def format_location(location):
    WIDTH = get_dynamic_width()
    inner_width = WIDTH - 4

    title = f"🌲 {location.name} 🌲"
    title_padded = pad_string(title, WIDTH, 'center')

    lines = [
        f"{Colors.BOLD}{Colors.BRIGHT_GREEN}{title_padded}{Colors.ENDC}",
        f"{Colors.GREEN}╭{'─' * (WIDTH - 2)}╮{Colors.ENDC}"
    ]

    # Wrap description
    wrapped_desc = textwrap.wrap(location.description, width=inner_width)
    for line in wrapped_desc:
        padded_line = pad_string(line, inner_width, 'center')
        lines.append(f"{Colors.GREEN}│ {Colors.WHITE}{padded_line}{Colors.GREEN} │{Colors.ENDC}")

    lines.append(f"{Colors.GREEN}├{'─' * (WIDTH - 2)}┤{Colors.ENDC}")

    # Items
    if location.items:
        for item_line in format_list_lines("Loot: ", location.items, Colors.BRIGHT_GREEN, inner_width):
            padded_item_line = pad_string(item_line, inner_width, 'left')
            lines.append(f"{Colors.GREEN}│ {padded_item_line} {Colors.GREEN}│{Colors.ENDC}")
    else:
        padded_none = pad_string(f"{Colors.WHITE}Loot: None{Colors.ENDC}", inner_width, 'left')
        lines.append(f"{Colors.GREEN}│ {padded_none} {Colors.GREEN}│{Colors.ENDC}")

    # Enemies
    if location.enemies:
        for enemy_line in format_list_lines("Danger: ", location.enemies, Colors.BRIGHT_RED, inner_width):
            padded_enemy_line = pad_string(enemy_line, inner_width, 'left')
            lines.append(f"{Colors.GREEN}│ {padded_enemy_line} {Colors.GREEN}│{Colors.ENDC}")

    lines.append(f"{Colors.GREEN}╰{'─' * (WIDTH - 2)}╯{Colors.ENDC}")
    return "\n".join(lines)


def format_sub_location(city_name, sub_location_name, sub_location_data, quest_statuses):
    WIDTH = get_dynamic_width()
    inner_width = WIDTH - 4

    title = f"⛫ {city_name} - {sub_location_name} ⛫"
    title_padded = pad_string(title, WIDTH, 'center')

    lines = [
        f"{Colors.BOLD}{Colors.BRIGHT_CYAN}{title_padded}{Colors.ENDC}",
        f"{Colors.CYAN}┏{'━' * (WIDTH - 2)}┓{Colors.ENDC}"
    ]

    wrapped_desc = textwrap.wrap(sub_location_data['description'], width=inner_width)
    for line in wrapped_desc:
        padded_line = pad_string(line, inner_width, 'center')
        lines.append(f"{Colors.CYAN}┃ {Colors.WHITE}{padded_line}{Colors.CYAN} ┃{Colors.ENDC}")

    lines.append(f"{Colors.CYAN}┣{'━' * (WIDTH - 2)}┫{Colors.ENDC}")

    if sub_location_data['npcs']:
        padded_header = pad_string(f"{Colors.BRIGHT_YELLOW}Citizens in the area:{Colors.ENDC}", inner_width, 'left')
        lines.append(f"{Colors.CYAN}┃ {padded_header} {Colors.CYAN}┃{Colors.ENDC}")

        for npc in sub_location_data['npcs']:
            status, quest_name = quest_statuses.get(npc, ("talk", None))
            if status == "complete":
                prefix = f"{Colors.BRIGHT_YELLOW}[!] {Colors.ENDC}"
            elif status == "available":
                prefix = f"{Colors.BRIGHT_CYAN}[?] {Colors.ENDC}"
            else:
                prefix = "  "

            npc_line = f"  {prefix}{Colors.WHITE}{npc}{Colors.ENDC}"
            padded_npc = pad_string(npc_line, inner_width, 'left')
            lines.append(f"{Colors.CYAN}┃ {padded_npc} {Colors.CYAN}┃{Colors.ENDC}")
    else:
        padded_quiet = pad_string(f"{Colors.WHITE}The area is quiet...{Colors.ENDC}", inner_width, 'left')
        lines.append(f"{Colors.CYAN}┃ {padded_quiet} {Colors.CYAN}┃{Colors.ENDC}")

    lines.append(f"{Colors.CYAN}┗{'━' * (WIDTH - 2)}┛{Colors.ENDC}")
    return "\n".join(lines)


def format_rare_location(location_name, location_data, item_available):
    WIDTH = get_dynamic_width()
    inner_width = WIDTH - 4

    title = f"✨ {location_name} ✨"
    title_padded = pad_string(title, WIDTH, 'center')

    lines = [
        f"{Colors.BOLD}{Colors.BRIGHT_YELLOW}{title_padded}{Colors.ENDC}",
        f"{Colors.YELLOW}╔{'═' * (WIDTH - 2)}╗{Colors.ENDC}"
    ]

    wrapped_desc = textwrap.wrap(location_data['description'], width=inner_width)
    for line in wrapped_desc:
        padded_line = pad_string(line, inner_width, 'center')
        lines.append(f"{Colors.YELLOW}║ {Colors.WHITE}{padded_line}{Colors.YELLOW} ║{Colors.ENDC}")

    lines.append(f"{Colors.YELLOW}╠{'═' * (WIDTH - 2)}╣{Colors.ENDC}")

    if location_data['npcs']:
        npc = location_data['npcs'][0]
        npc_line = f"{Colors.WHITE}You see: {Colors.BRIGHT_YELLOW}{npc}{Colors.ENDC}"
        padded_npc = pad_string(npc_line, inner_width, 'left')
        lines.append(f"{Colors.YELLOW}║ {padded_npc} {Colors.YELLOW}║{Colors.ENDC}")

    if item_available and location_data['items']:
        item = location_data['items'][0]
        item_line = f"{Colors.WHITE}Resting nearby: {Colors.BRIGHT_GREEN}{item}{Colors.ENDC}"
        padded_item = pad_string(item_line, inner_width, 'left')
        lines.append(f"{Colors.YELLOW}║ {padded_item} {Colors.YELLOW}║{Colors.ENDC}")

    lines.append(f"{Colors.YELLOW}╚{'═' * (WIDTH - 2)}╝{Colors.ENDC}")
    return "\n".join(lines)


def display_status(player):
    tui.clear_screen()
    WIDTH = get_dynamic_width()
    half_width = (WIDTH - 2) // 2
    other_half = (WIDTH - 2) - half_width

    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╔{'═' * (WIDTH - 2)}╗{Colors.ENDC}")
    title_padded = pad_string("CHARACTER SHEET", WIDTH - 2, 'center')
    print(
        f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}║{Colors.BRIGHT_YELLOW}{title_padded}"
        f"{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╠{'═' * (WIDTH - 2)}╣{Colors.ENDC}")

    # Basic Info Row
    name_str = pad_string(f" Name: {player.name}", half_width, 'left')
    loc_text = f"Location: {player.location}"
    if player.current_sub_location:
        loc_text += f" ({player.current_sub_location})"
    loc_str = pad_string(loc_text + " ", other_half, 'right')
    print(f"{Colors.BRIGHT_MAGENTA}║{Colors.WHITE}{name_str}{loc_str}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")

    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╠{'═' * (WIDTH - 2)}╣{Colors.ENDC}")

    # Stats Row
    hp_str = pad_string(f" HP: {Colors.BRIGHT_GREEN}{player.hp}/{player.max_hp}{Colors.ENDC}", half_width, 'left')
    silver_str = pad_string(f"Silver: {Colors.BRIGHT_YELLOW}{player.silver}S{Colors.ENDC} ", other_half, 'right')
    print(f"{Colors.BRIGHT_MAGENTA}║{hp_str}{silver_str}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")

    # Skills Row
    skills_title = pad_string(" [ SKILLS ]", WIDTH - 2, 'left')
    print(f"{Colors.BRIGHT_MAGENTA}║{Colors.BRIGHT_CYAN}{skills_title}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")
    skill_text = "  " + " | ".join([f"{k}: {v}" for k, v in player.skills.items()])
    skill_padded = pad_string(skill_text, WIDTH - 2, 'left')
    print(f"{Colors.BRIGHT_MAGENTA}║{Colors.WHITE}{skill_padded}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")

    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╠{'═' * (WIDTH - 2)}╣{Colors.ENDC}")

    # Inventory
    inv_title = pad_string(" [ INVENTORY ]", WIDTH - 2, 'left')
    print(f"{Colors.BRIGHT_MAGENTA}║{Colors.BRIGHT_BLUE}{inv_title}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")
    inventory_str = ', '.join(player.inventory) or 'Empty'
    inv_wrapped = textwrap.wrap(inventory_str, width=WIDTH - 6)
    for line in inv_wrapped:
        line_padded = pad_string(f"  {line}", WIDTH - 2, 'left')
        print(f"{Colors.BRIGHT_MAGENTA}║{Colors.WHITE}{line_padded}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")

    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╠{'═' * (WIDTH - 2)}╣{Colors.ENDC}")

    # Quests
    quest_title = pad_string(" [ ACTIVE QUESTS ]", WIDTH - 2, 'left')
    print(f"{Colors.BRIGHT_MAGENTA}║{Colors.BRIGHT_YELLOW}{quest_title}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")

    if player.current_quests:
        for quest_name, quest_def in player.get_current_quest_details():
            desc = quest_def.get('description', 'No description.')
            progress = player.get_quest_progress(quest_name)
            if quest_def.get('turn_in_npc'):
                desc += f" (Return to {quest_def.get('turn_in_npc')})"

            q_str = f" {quest_name}: {desc} {progress}"
            q_wrapped = textwrap.wrap(q_str, width=WIDTH - 6)
            for i, line in enumerate(q_wrapped):
                bullet = "•" if i == 0 else " "
                q_line_pad = pad_string(f" {bullet} {line}", WIDTH - 2, 'left')
                print(f"{Colors.BRIGHT_MAGENTA}║{Colors.WHITE}{q_line_pad}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")
    else:
        none_pad = pad_string("   None", WIDTH - 2, 'left')
        print(f"{Colors.BRIGHT_MAGENTA}║{Colors.WHITE}{none_pad}{Colors.BRIGHT_MAGENTA}║{Colors.ENDC}")

    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}╚{'═' * (WIDTH - 2)}╝{Colors.ENDC}")
    display_message("", wait_for_key=True)


# --- Prompt & Selection Functions ---

def prompt_update(current_version, new_version):
    title = "Update Available!"
    header = (f"A new version of the game is available.\n\n"
              f"  Current Version: {current_version}\n"
              f"  Latest Version:  {new_version}\n")
    options = ["Update Now", "Later"]
    choice = tui.menu(title, options, header_text=header, add_cancel=False)
    return choice == "Update Now"


def prompt_new_or_load():
    title = "MAIN MENU"
    header = (f"{Colors.BOLD}{Colors.BRIGHT_RED}  ___         _        {Colors.BRIGHT_YELLOW}   _            _       \n"
              f"{Colors.BRIGHT_RED} | _ \\_ _ ___(_)___ ___{Colors.BRIGHT_YELLOW}  /_\\  ___ _ _| |_ ___ \n"
              f"{Colors.BRIGHT_RED} |  _/ '_/ _ \\ | -_) _ \\{Colors.BRIGHT_YELLOW} / _ \\/ _ \\ '_|  _/ -_)\n"
              f"{Colors.BRIGHT_RED} |_| |_| \\___// \\___\\___/{Colors.BRIGHT_YELLOW}/_/ \\_\\___/_|  \\__\\___|\n"
              f"{Colors.BRIGHT_RED}            |__/       {Colors.ENDC}\n\n"
              f"{Colors.WHITE}A classic terminal-based RPG experience.{Colors.ENDC}\n")

    options = ["New Game", "Load Game"]
    choice = tui.menu(title, options, header_text=header)
    if choice == "New Game":
        return "n"
    elif choice == "Load Game":
        return "l"
    return None


def prompt_for_name():
    tui.clear_screen()
    display_header("Create Your Character")
    name = input(f" {Colors.BRIGHT_CYAN}➤ Enter your name ({Colors.BRIGHT_BLUE}Adventurer{Colors.BRIGHT_CYAN}): "
                 f"{Colors.BRIGHT_BLUE}").strip()
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


def prompt_safe_action(player, city_name, city_data, sub_location_name, merchant_npcs, innkeeper_npcs, quest_statuses):
    sub_location = city_data["sub_locations"][sub_location_name]
    header = format_sub_location(city_name, sub_location_name, sub_location, quest_statuses)
    option_map = {}
    options = []

    # NPC-specific actions
    for npc_name in sub_location.get("npcs", []):
        status, quest_name = quest_statuses.get(npc_name, ("talk", None))
        if status == "complete":
            option_text = f"[!] Complete Quest with {npc_name}"
            option_map[option_text] = ("complete_quest", npc_name)
        elif status == "available":
            option_text = f"[?] Accept Quest from {npc_name}"
            option_map[option_text] = ("accept_quest", npc_name)
        else:
            option_text = f"Talk to {npc_name}"
            option_map[option_text] = ("talk", npc_name)
        options.append(option_text)

        if npc_name in merchant_npcs:
            trade_text = f"Trade with {npc_name}"
            options.append(trade_text)
            option_map[trade_text] = ("trade", npc_name)
        if npc_name in innkeeper_npcs:
            rest_text = f"Rest at the inn (15 Silver)"
            options.append(rest_text)
            option_map[rest_text] = ("rest", npc_name)

    # Move actions
    for other_sub_loc in city_data["sub_locations"]:
        if other_sub_loc != sub_location_name:
            option_text = f"Go to the {other_sub_loc}"
            options.append(option_text)
            option_map[option_text] = ("move", other_sub_loc)

    # General actions
    general_actions = ["View Status", "Eat an item", "View Quests", "Save Game"]
    for action in general_actions:
        options.append(action)
        option_map[action] = (action.lower().replace(" ", "_"), None)

    # Leave action
    leave_text = f"Leave {city_name}"
    options.append(leave_text)
    option_map[leave_text] = ("leave", city_name)

    choice = tui.menu(title=f"What will {player.name} do? ({player.silver}S)",
                      options=options,
                      header_text=header)

    if choice is None:
        return None, None

    return option_map.get(choice)


def prompt_rare_action(player, location_name, location_data, item_available):
    header = format_rare_location(location_name, location_data, item_available)
    option_map = {}
    options = []

    # Talk action
    npc_name = location_data["npcs"][0]
    talk_text = f"Talk to the {npc_name}"
    options.append(talk_text)
    option_map[talk_text] = ("talk", npc_name)

    # Take item action
    if item_available and location_data["items"]:
        item_name = location_data["items"][0]
        take_text = f"Take the {item_name}"
        options.append(take_text)
        option_map[take_text] = ("take_item", item_name)

    # Leave action
    leave_text = "Leave the campfire"
    options.append(leave_text)
    option_map[leave_text] = ("leave", None)

    choice = tui.menu(title=f"What will {player.name} do?",
                      options=options,
                      header_text=header)

    if choice is None:
        return None, None

    return option_map.get(choice)


# --- Combat Interface ---

def render_combat_ui(player, enemy, log, actions, selected_action_index):
    WIDTH = get_dynamic_width()
    inner_width = WIDTH - 4
    half_width = (WIDTH - 2) // 2
    other_half = (WIDTH - 2) - half_width

    buffer = [
        f"{Colors.BOLD}{Colors.BRIGHT_RED}╔{'═' * (WIDTH - 2)}╗{Colors.ENDC}",
        f"{Colors.BOLD}{Colors.BRIGHT_RED}║{Colors.WHITE}"
        f"{pad_string('⚔️  COMBAT INITIATED ⚔️', WIDTH - 2, 'center')}{Colors.BRIGHT_RED}║{Colors.ENDC}",
        f"{Colors.BOLD}{Colors.BRIGHT_RED}╠{'═' * (WIDTH - 2)}╣{Colors.ENDC}"
    ]

    BAR_LEN = max(10, (WIDTH - 30) // 2)

    player_hp_bar = tui.create_hp_bar(player.hp, player.max_hp, BAR_LEN, Colors.BRIGHT_GREEN)
    enemy_hp_bar = tui.create_hp_bar(enemy.hp, enemy.max_hp, BAR_LEN, Colors.BRIGHT_RED)

    # Names Row
    p_name_pad = pad_string(f" {Colors.BOLD}{Colors.BRIGHT_CYAN}{player.name}{Colors.ENDC}", half_width, 'left')
    e_name_pad = pad_string(f"{Colors.BRIGHT_YELLOW}{enemy.name}{Colors.ENDC} ", other_half, 'right')
    buffer.append(f"{Colors.BRIGHT_RED}║{p_name_pad}{e_name_pad}{Colors.BRIGHT_RED}║{Colors.ENDC}")

    # HP Bars Row
    p_hp_pad = pad_string(f" HP: {player_hp_bar}", half_width, 'left')
    e_hp_pad = pad_string(f"HP: {enemy_hp_bar} ", other_half, 'right')
    buffer.append(f"{Colors.BRIGHT_RED}║{p_hp_pad}{e_hp_pad}{Colors.BRIGHT_RED}║{Colors.ENDC}")

    # Numeric HP Row
    p_num_pad = pad_string(f" {player.hp}/{player.max_hp}", half_width, 'left')
    e_num_pad = pad_string(f"{max(0, enemy.hp)}/{enemy.max_hp} ", other_half, 'right')
    buffer.append(f"{Colors.BRIGHT_RED}║{Colors.WHITE}{p_num_pad}{e_num_pad}{Colors.BRIGHT_RED}║{Colors.ENDC}")

    buffer.append(f"{Colors.BOLD}{Colors.BRIGHT_RED}╠{'═' * (WIDTH - 2)}╣{Colors.ENDC}")

    # Combat Log
    log_title = pad_string(f" {Colors.BRIGHT_YELLOW}Combat Log:{Colors.ENDC}", inner_width + 2, 'left')
    buffer.append(f"{Colors.BRIGHT_RED}║{log_title}{Colors.BRIGHT_RED}║{Colors.ENDC}")

    for msg in log:
        msg_str = msg if msg else ""
        wrapped_log = textwrap.wrap(msg_str, width=inner_width) or [""]
        for w_log in wrapped_log:
            log_pad = pad_string(f" › {w_log}", inner_width + 2, 'left')
            buffer.append(f"{Colors.BRIGHT_RED}║{Colors.WHITE}{log_pad}{Colors.BRIGHT_RED}║{Colors.ENDC}")

    buffer.append(f"{Colors.BOLD}{Colors.BRIGHT_RED}╚{'═' * (WIDTH - 2)}╝{Colors.ENDC}")
    buffer.append(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}  [ CHOOSE ACTION ]{Colors.ENDC}")

    # Actions
    for i, action in enumerate(actions):
        if i == selected_action_index:
            buffer.append(f"    {Colors.INVERSE} {action} {Colors.ENDC}")
        else:
            buffer.append(f"    {Colors.WHITE} {action} {Colors.ENDC}")

    buffer.append("")
    tui.render_from_buffer(buffer)
