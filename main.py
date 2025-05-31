# ver.0.1-beta

import random
import sys
import json
import os
import interface


def load_game_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        interface.display_message(f"Error: {filename} not found. The game cannot run.",
                                  interface.Colors.BRIGHT_RED, wait_for_key=True)
        sys.exit(1)
    except json.JSONDecodeError:
        interface.display_message(f"Error: {filename} is corrupted. Please check the file.",
                                  interface.Colors.BRIGHT_RED, wait_for_key=True)
        sys.exit(1)


QUEST_DEFINITIONS = load_game_data('defins/quests.json')
ITEM_DEFINITIONS = load_game_data('defins/items.json')

EDIBLE_ITEMS = [item_name for item_name, props in ITEM_DEFINITIONS.items() if props.get('edible')]
ALL_POSSIBLE_ITEMS = list(ITEM_DEFINITIONS.keys())
ALL_POSSIBLE_ENEMIES = ["Goblin", "Ghost", "Wolf", "Bandit", "Skeleton", "Spider", "Ogre", "Dragonling"]


class Player:
    def __init__(self, name="Adventurer"):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.inventory = []
        self.skills = {"Strength": 3, "Agility": 3, "Wisdom": 3}
        self.location = "Mystic Forest"
        self.current_quests = []
        self.completed_quests = []
        self.enemies_defeated = {}
        self.items_gathered = {}

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
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        player = cls(data['name'])
        player.__dict__.update(data)
        return player


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
        heal_amount = random.randint(item_props.get('heal_min', 0), item_props.get('heal_max', 0))

        player.hp = min(player.max_hp, player.hp + heal_amount)
        player.inventory.remove(item_to_eat)
        interface.display_message(f"You ate {item_to_eat} and restored {heal_amount} HP!",
                                  interface.Colors.BRIGHT_GREEN, wait_for_key=True)


def explore(player):
    location = generate_location()
    player.location = location.name

    check_and_complete_quests(player)

    # 20% chance to offer a quest in a new area
    if random.random() < 0.2:
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
            enemy = location.enemies.pop(random.randrange(len(location.enemies)))
            damage = random.randint(5, 20)
            player.hp -= damage
            player.enemies_defeated[enemy] = player.enemies_defeated.get(enemy, 0) + 1
            interface.display_message(f"You fought a {enemy} and lost {damage} HP!",
                                      interface.Colors.BRIGHT_RED, wait_for_key=True)
            check_and_complete_quests(player)
            if player.hp <= 0:
                interface.display_header("!!! You have fallen !!!")
                interface.display_message("Game Over", interface.Colors.BRIGHT_RED, wait_for_key=True)
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

    while True:
        explore(player)


if __name__ == "__main__":
    main()
