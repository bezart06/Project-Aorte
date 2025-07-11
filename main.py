# ver.0.2.0-beta2

import random
import sys
import json
import os
import interface
import time
import updater


def handle_updates():
    latest_version = updater.check_for_updates()
    if latest_version:
        if interface.prompt_update(updater.CURRENT_VERSION, latest_version):
            interface.display_message("Downloading update... The application will restart.", wait_for_key=False)
            updater.download_and_apply_update(latest_version)
            interface.display_message("Update failed. Please try again later.", wait_for_key=True)


def load_game_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        interface.display_message(f"Error: Data file {filename} not found. The game cannot run.",
                                  interface.Colors.BRIGHT_RED, wait_for_key=True)
        sys.exit(1)
    except json.JSONDecodeError:
        interface.display_message(f"Error: Data file {filename} is corrupted. Please check the file.",
                                  interface.Colors.BRIGHT_RED, wait_for_key=True)
        sys.exit(1)


QUEST_DEFINITIONS = load_game_data(os.path.join('defins', 'quests.json'))
ITEM_DEFINITIONS = load_game_data(os.path.join('defins', 'items.json'))
ENEMY_DEFINITIONS = load_game_data(os.path.join('defins', 'enemies.json'))

EDIBLE_ITEMS = [item_name for item_name, props in ITEM_DEFINITIONS.items() if props.get('edible')]
ALL_POSSIBLE_ITEMS = list(ITEM_DEFINITIONS.keys())
ALL_POSSIBLE_ENEMIES = list(ENEMY_DEFINITIONS.keys())


class Player:
    def __init__(self, name="Adventurer"):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.inventory = []
        self.skills = {"Strength": 5, "Agility": 4, "Wisdom": 3}
        self.location = "Mystic Forest"
        self.current_quests = []
        self.completed_quests = []
        self.enemies_defeated = {}
        self.items_gathered = {}
        self.has_wisdom_buff = False
        self.combat_buffs = {}

    def get_combat_items(self):
        combat_items = []
        for item_name in self.inventory:
            if ITEM_DEFINITIONS.get(item_name, {}).get('combat_usable'):
                combat_items.append(item_name)
        return list(set(combat_items))

    def apply_combat_buffs(self, item_effect):
        skill = item_effect.get('skill')
        amount = item_effect.get('amount')
        if skill and amount and skill in self.skills:
            if skill not in self.combat_buffs:
                self.combat_buffs[skill] = 0
            self.skills[skill] += amount
            self.combat_buffs[skill] += amount
            return f"Your {skill} was increased by {amount}!"
        return ""

    def clear_combat_buffs(self):
        for skill, amount in self.combat_buffs.items():
            self.skills[skill] -= amount
        self.combat_buffs = {}

    def get_current_quest_details(self):
        details = []
        for q_name in self.current_quests:
            if q_name in QUEST_DEFINITIONS:
                details.append((q_name, QUEST_DEFINITIONS[q_name]))
        return details

    def get_quest_progress(self, quest_name):
        quest_def = QUEST_DEFINITIONS.get(quest_name)
        if not quest_def:
            return ""

        progress = ""
        if quest_def['type'] == "defeat_enemies":
            current = self.enemies_defeated.get(quest_def['target_enemy'], 0)
            progress = f" ({current}/{quest_def['target_count']})"
        elif quest_def['type'] == "gather_items":
            current = self.items_gathered.get(quest_def['target_item'], 0)
            progress = f" ({current}/{quest_def['target_count']})"
        return progress

    def to_dict(self):
        # Don't save temporary buffs
        data = self.__dict__.copy()
        del data['combat_buffs']
        return data

    @classmethod
    def from_dict(cls, data):
        player = cls(data['name'])
        player.__dict__.update(data)
        if 'Strength' not in player.skills:
            player.skills['Strength'] = 5
        if 'Agility' not in player.skills:
            player.skills['Agility'] = 4
        if 'Wisdom' not in player.skills:
            player.skills['Wisdom'] = 3
        if 'has_wisdom_buff' not in data:
            player.has_wisdom_buff = False
        player.combat_buffs = {}
        return player


class Enemy:
    def __init__(self, name):
        enemy_data = ENEMY_DEFINITIONS.get(name, {"hp": 10, "attack": 3})
        self.name = name
        self.hp = enemy_data['hp']
        self.max_hp = enemy_data['hp']
        self.attack = enemy_data['attack']


class Location:
    def __init__(self, name, description, items, enemies):
        self.name = name
        self.description = description
        self.items = items
        self.enemies = enemies


def generate_location():
    prefixes = ["Forgotten", "Ancient", "Silent", "Haunted", "Shimmering"]
    places = ["Cavern", "Ruins", "Grove", "Shrine", "Tomb", "Valley"]
    name = f"{random.choice(prefixes)} {random.choice(places)}"
    description = f"This {name} holds secrets lost in time. The air is thick with mystery and the scent of damp earth."

    items_to_add = random.sample(ALL_POSSIBLE_ITEMS, k=random.randint(1, min(3, len(ALL_POSSIBLE_ITEMS))))
    enemies_to_add = random.sample(ALL_POSSIBLE_ENEMIES, k=random.randint(0, min(2, len(ALL_POSSIBLE_ENEMIES))))

    return Location(name, description, items_to_add, enemies_to_add)


def combat(player, enemy_name):
    """
    Manages the step-by-step battle between the player and the enemy.
    True returns if the player won and false if lost.
    """
    enemy = Enemy(enemy_name)
    player.has_wisdom_buff = False
    combat_log = [""] * 5
    actions = ["Attack", "Use Item", "Flee"]
    selected_action_index = 0

    def add_log(message):
        combat_log.pop(0)
        combat_log.append(message)

    add_log(f"A wild {enemy.name} appears!")

    insight_chance = player.skills.get('Wisdom', 3) * 2  # 2% a chance per unit of wisdom
    if random.randint(1, 100) <= insight_chance:
        player.has_wisdom_buff = True
        add_log("Your wisdom gives critical insight! Your next attack is amplified.")

    try:
        while player.hp > 0 and enemy.hp > 0:
            action_chosen = False
            while not action_chosen:
                interface.render_combat_ui(player, enemy, combat_log, actions, selected_action_index)
                key = interface.tui.get_key()

                if key == "UP":
                    selected_action_index = (selected_action_index - 1) % len(actions)
                elif key == "DOWN":
                    selected_action_index = (selected_action_index + 1) % len(actions)
                elif key == "ENTER":
                    action = actions[selected_action_index]
                    action_chosen = True

            turn_ended = False

            if action == "Attack":
                player_damage = player.skills['Strength'] + random.randint(1, 6)
                if player.has_wisdom_buff:
                    player_damage += player.skills.get('Wisdom', 3) // 2 + 2
                    add_log("You hit a vulnerable spot revealed by an epiphany!")
                    player.has_wisdom_buff = False
                enemy.hp -= player_damage
                add_log(f"You attack the {enemy.name}, dealing {player_damage} damage.")
                turn_ended = True

            elif action == "Use Item":
                combat_items = player.get_combat_items()
                if not combat_items:
                    add_log("You have no usable items in combat.")
                    continue

                interface.tui.clear_screen()
                item_to_use = interface.select_from_list("Use Item", combat_items, "Select an item")

                if item_to_use:
                    player.inventory.remove(item_to_use)
                    item_def = ITEM_DEFINITIONS[item_to_use]
                    effect = item_def.get('effect', {})

                    if effect.get('type') == 'damage_enemy':
                        damage = random.randint(effect['min'], effect['max'])
                        enemy.hp -= damage
                        add_log(f"You used {item_to_use}, dealing {damage} damage!")
                    elif effect.get('type') == 'buff_player':
                        log_msg = player.apply_combat_buffs(effect)
                        add_log(f"You used {item_to_use}. {log_msg}")

                    turn_ended = True
                else:
                    add_log("You decided not to use an item.")
                    continue

            elif action == "Flee":
                flee_chance = player.skills.get('Agility', 4) * 4
                if random.randint(1, 100) <= flee_chance:
                    add_log("You successfully escaped!")
                    return "fled"
                else:
                    add_log("You failed to escape! You lose your turn.")
                    turn_ended = True

            if enemy.hp <= 0:
                add_log(f"The {enemy.name} is defeated!")
                return True

            if not turn_ended:
                continue

            interface.render_combat_ui(player, enemy, combat_log, actions, selected_action_index)
            time.sleep(1)

            agility = player.skills.get('Agility', 4)
            dodge_chance = (agility / (agility + 20)) * 100
            if random.randint(1, 100) <= dodge_chance:
                add_log(f"You deftly dodge the {enemy.name}'s attack!")
                continue

            enemy_damage = max(0, enemy.attack + random.randint(-1, 2))
            player.hp -= enemy_damage
            add_log(f"The {enemy.name} attacks you, dealing {enemy_damage} damage.")

            if player.hp <= 0:
                break

        return player.hp > 0

    finally:
        player.clear_combat_buffs()


def choose_quest(player):
    available_quests = [q for q in QUEST_DEFINITIONS if
                        q not in player.current_quests and q not in player.completed_quests]

    if not available_quests:
        interface.display_message("No new quests available at the moment.", interface.Colors.BRIGHT_BLUE,
                                  wait_for_key=True)
        return

    quest_descriptions = [f"{q}: {QUEST_DEFINITIONS[q]['description']}" for q in available_quests]
    choice_desc = interface.select_from_list("Available Quests", quest_descriptions,
                                             "Select a quest to accept")

    if choice_desc:
        quest_name = choice_desc.split(':')[0]
        player.current_quests.append(quest_name)
        interface.display_message(f"Quest Accepted: {quest_name}!", interface.Colors.BRIGHT_GREEN,
                                  wait_for_key=True)


def check_and_complete_quests(player):
    quests_to_remove = []
    for quest_name in player.current_quests:
        quest_def = QUEST_DEFINITIONS.get(quest_name)
        if not quest_def:
            continue

        completed = False
        if quest_def['type'] == "defeat_enemies" and player.enemies_defeated.get(quest_def['target_enemy'], 0) >= \
            quest_def['target_count']:
            completed = True
        elif quest_def['type'] == "gather_items" and player.items_gathered.get(quest_def['target_item'], 0) >= \
            quest_def['target_count']:
            completed = True
        elif quest_def['type'] == "item_find" and quest_def['target_item'] in player.inventory:
            completed = True
        elif quest_def['type'] == "reach_location" and player.location == quest_def['target_location']:
            completed = True

        if completed:
            interface.tui.clear_screen()
            interface.display_message(f"QUEST COMPLETED: {quest_name}!",
                                      f"{interface.Colors.BOLD}{interface.Colors.BRIGHT_GREEN}")

            if 'reward_hp' in quest_def:
                player.hp = min(player.max_hp, player.hp + quest_def['reward_hp'])
                interface.display_message(f"  You restored {quest_def['reward_hp']} HP!",
                                          interface.Colors.BRIGHT_GREEN)
            if 'reward_skill' in quest_def:
                for skill, value in quest_def['reward_skill'].items():
                    if skill in player.skills:
                        player.skills[skill] += value
                        interface.display_message(f"  Your {skill} increased by {value}!",
                                                  interface.Colors.BRIGHT_CYAN)
            if 'reward_item' in quest_def:
                player.inventory.append(quest_def['reward_item'])
                interface.display_message(f"  You received {quest_def['reward_item']}!",
                                          interface.Colors.BRIGHT_GREEN)

            player.completed_quests.append(quest_name)
            quests_to_remove.append(quest_name)

            if quest_def['type'] == "defeat_enemies":
                player.enemies_defeated[quest_def['target_enemy']] = 0
            elif quest_def['type'] == "gather_items":
                player.items_gathered[quest_def['target_item']] = 0
                for _ in range(quest_def['target_count']):
                    if quest_def['target_item'] in player.inventory:
                        player.inventory.remove(quest_def['target_item'])

            interface.display_message("", wait_for_key=True)

    for quest_name in quests_to_remove:
        if quest_name in player.current_quests:
            player.current_quests.remove(quest_name)


def save_game(player):
    interface.tui.clear_screen()
    filename_input = input(f"Enter save file name: {interface.Colors.BRIGHT_BLUE}").strip()
    print(interface.Colors.ENDC, end='')
    if not filename_input:
        interface.display_message("Save cancelled. No filename provided.", interface.Colors.BRIGHT_YELLOW,
                                  wait_for_key=True)
        return

    full_filename = f"save_{filename_input}.json"
    try:
        with open(full_filename, "w") as f:
            json.dump(player.to_dict(), f, indent=2)
        interface.display_message(f"Game saved to {full_filename}", interface.Colors.BRIGHT_GREEN,
                                  wait_for_key=True)
    except IOError:
        interface.display_message(f"Error saving game to {full_filename}", interface.Colors.BRIGHT_RED,
                                  wait_for_key=True)


def load_game():
    files = [f for f in os.listdir() if f.startswith("save_") and f.endswith(".json")]
    if not files:
        interface.display_message("No saved games found.", interface.Colors.BRIGHT_YELLOW, wait_for_key=True)
        return None

    filenames_clean = [f[5:-5] for f in files]
    choice = interface.select_from_list("Load Game", filenames_clean, "Select a save file to load")

    if choice:
        try:
            with open(f"save_{choice}.json", "r") as f:
                data = json.load(f)
            return Player.from_dict(data)
        except (IOError, json.JSONDecodeError):
            interface.display_message(f"Error loading save file {choice}.", interface.Colors.BRIGHT_RED,
                                      wait_for_key=True)
    return None


def heal_player(player):
    player_edible_items = [item for item in player.inventory if item in EDIBLE_ITEMS]
    if not player_edible_items:
        interface.display_message("You have no edible items.", interface.Colors.BRIGHT_YELLOW,
                                  wait_for_key=True)
        return

    item_to_eat = interface.select_from_list("Eat an Item", player_edible_items, "Select an item to consume")

    if item_to_eat:
        item_props = ITEM_DEFINITIONS[item_to_eat]
        base_heal_amount = random.randint(item_props.get('heal_min', 0), item_props.get('heal_max', 0))

        wisdom_bonus = player.skills.get('Wisdom', 0) // 2
        total_heal = base_heal_amount + wisdom_bonus

        player.hp = min(player.max_hp, player.hp + total_heal)
        player.inventory.remove(item_to_eat)

        if wisdom_bonus > 0:
            heal_message = (f"You ate {item_to_eat}, restoring {base_heal_amount} HP + "
                            f"{wisdom_bonus} HP from wisdom!")
        else:
            heal_message = f"You ate {item_to_eat} and restored {total_heal} HP!"

        interface.display_message(heal_message, interface.Colors.BRIGHT_GREEN, wait_for_key=True)


def explore(player):
    location = generate_location()
    player.location = location.name

    check_and_complete_quests(player)

    # 15% chance to offer a quest in a new area
    if random.random() < 0.15:
        choose_quest(player)

    while True:
        action = interface.prompt_action(player, location)

        if not action or action == "Quit Game":
            interface.display_header("Farewell, Adventurer!")
            sys.exit()

        if action == "Take an item":
            item_name = location.items.pop(random.randrange(len(location.items)))
            player.inventory.append(item_name)
            player.items_gathered[item_name] = player.items_gathered.get(item_name, 0) + 1
            interface.display_message(f"You picked up: {item_name}", interface.Colors.BRIGHT_GREEN,
                                      wait_for_key=True)
            check_and_complete_quests(player)

        elif action == "Fight an enemy":
            enemy_name = location.enemies.pop(random.randrange(len(location.enemies)))
            combat_result = combat(player, enemy_name)

            if combat_result is True:
                player.enemies_defeated[enemy_name] = player.enemies_defeated.get(enemy_name, 0) + 1
                check_and_complete_quests(player)
            elif combat_result is False:
                interface.display_header("!!! You have fallen !!!")
                interface.display_message("This is Game Over...",
                                          interface.Colors.BRIGHT_RED, wait_for_key=True)
                sys.exit()

        elif action == "Move to a new area":
            return

        elif action == "View Status":
            interface.display_status(player)

        elif action == "Eat an item":
            heal_player(player)

        elif action == "View Quests":
            choose_quest(player)

        elif action == "Save Game":
            save_game(player)


def main():
    player = None
    interface.tui.clear_screen()

    while player is None:
        choice = interface.prompt_new_or_load()
        if choice == 'l':
            player = load_game()
        elif choice == 'n':
            name = interface.prompt_for_name()
            player = Player(name)
        elif choice is None:
            interface.display_header("Farewell!")
            sys.exit()

    interface.display_header(f"Welcome, {player.name}!")
    interface.display_message("Your journey begins...", wait_for_key=True)

    try:
        while True:
            explore(player)
    finally:
        interface.tui.cleanup_tui()


if __name__ == "__main__":
    main()
