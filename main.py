import random
import sys
import json
import os


class Colors:
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_RED = '\033[91m'

    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_game_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Colors.BRIGHT_RED}Error: {filename} not found. Please create it.{Colors.ENDC}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{Colors.BRIGHT_RED}Error: {filename} is corrupted or not valid JSON.{Colors.ENDC}")
        sys.exit(1)


def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


QUEST_DEFINITIONS = load_game_data('quests.json')
ITEM_DEFINITIONS = load_game_data('items.json')

EDIBLE_ITEMS = [item_name for item_name, props in ITEM_DEFINITIONS.items() if props.get('edible')]
ALL_POSSIBLE_ITEMS = list(ITEM_DEFINITIONS.keys())

ALL_POSSIBLE_ENEMIES = ["Goblin", "Ghost", "Wolf", "Bandit", "Skeleton", "Spider", "Ogre", "Dragonling"]


class Player:
    def __init__(self, name="Adventurer"):
        self.name = name
        self.hp = 100
        self.max_hp = 100
        self.inventory = []
        self.skills = {"Strength": 5, "Agility": 5, "Wisdom": 5}
        self.location = "Mystic Forest"
        self.current_quests = []
        self.completed_quests = []
        self.enemies_defeated = {}
        self.items_gathered = {}

    def status(self):
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}--- {self.name}'s Status ---{Colors.ENDC}")
        print(f"  HP: {Colors.BRIGHT_GREEN}{self.hp}/{self.max_hp}{Colors.ENDC}")
        print(f"  Inventory: {Colors.BRIGHT_BLUE}{', '.join(self.inventory) or 'Empty'}{Colors.ENDC}")
        print(f"  Skills:")
        for skill, value in self.skills.items():
            print(f"    - {skill}: {Colors.BRIGHT_CYAN}{value}{Colors.ENDC}")
        print(f"  Location: {Colors.BRIGHT_BLUE}{self.location}{Colors.ENDC}")
        print(f"  {Colors.BOLD}Active Quests:{Colors.ENDC}")
        if self.current_quests:
            for quest_name in self.current_quests:
                quest_def = QUEST_DEFINITIONS.get(quest_name)
                if not quest_def:
                    print(f"    - {Colors.BRIGHT_RED}Unknown Quest: {quest_name}{Colors.ENDC}")
                    continue

                desc = quest_def.get('description', 'No description available.')
                progress = ""
                if quest_def['type'] == "defeat_enemies":
                    current = self.enemies_defeated.get(quest_def['target_enemy'], 0)
                    progress = f" ({current}/{quest_def['target_count']})"
                elif quest_def['type'] == "gather_items":
                    current = self.items_gathered.get(quest_def['target_item'], 0)
                    progress = f" ({current}/{quest_def['target_count']})"
                print(f"    - {Colors.BRIGHT_YELLOW}{quest_name}{Colors.ENDC}: {desc}{progress}")
        else:
            print(f"    {Colors.BRIGHT_BLUE}None{Colors.ENDC}")
        print(f"  Completed Quests: {Colors.BRIGHT_GREEN}{', '.join(self.completed_quests) or 'None'}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}--------------------{Colors.ENDC}")

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        player = cls(data['name'])
        player.hp = data.get('hp', 100)
        player.max_hp = data.get('max_hp', 100)
        player.inventory = data.get('inventory', [])
        player.skills = data.get('skills', {"Strength": 5, "Agility": 5, "Wisdom": 5})
        player.location = data.get('location', "Mystic Forest")
        player.current_quests = data.get('current_quests', [])
        player.completed_quests = data.get('completed_quests', [])
        player.enemies_defeated = data.get('enemies_defeated', {})
        player.items_gathered = data.get('items_gathered', {})
        return player


class Location:
    def __init__(self, name, description, items, enemies):
        self.name = name
        self.description = description
        self.items = items
        self.enemies = enemies

    def show(self):
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}--- Entering {self.name} ---{Colors.ENDC}")
        print(f"{Colors.BLUE}{self.description}{Colors.ENDC}\n")
        if self.items:
            print(f"  You see: {Colors.BRIGHT_GREEN}{', '.join(self.items)}{Colors.ENDC}")
        if self.enemies:
            print(f"  Danger nearby: {Colors.BRIGHT_RED}{', '.join(self.enemies)}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}--------------------{Colors.ENDC}")


def generate_location():
    prefixes = ["Forgotten", "Ancient", "Silent", "Haunted", "Shimmering", "Whispering", "Sunken"]
    places = ["Cavern", "Ruins", "Grove", "Shrine", "Tomb", "Valley", "Dungeon"]

    items_to_add = random.sample(ALL_POSSIBLE_ITEMS, k=random.randint(1, min(3, len(ALL_POSSIBLE_ITEMS))))
    enemies_to_add = random.sample(ALL_POSSIBLE_ENEMIES, k=random.randint(0, min(2, len(ALL_POSSIBLE_ENEMIES))))

    name = f"{random.choice(prefixes)} {random.choice(places)}"
    description = f"This {name} holds secrets lost in time. The air is thick with mystery."
    return Location(name, description, items_to_add, enemies_to_add)


def get_available_quests(player):
    available_quests = []
    for quest_name, quest_data in QUEST_DEFINITIONS.items():
        is_active = quest_name in player.current_quests
        is_completed = quest_name in player.completed_quests

        if not is_active and not is_completed:
            available_quests.append({"name": quest_name, **quest_data})
    return available_quests


def choose_quest(player):
    available_quests = get_available_quests(player)

    if not available_quests:
        print(f"\n{Colors.BRIGHT_BLUE}No new quests available at the moment.{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}--- Available Quests ---{Colors.ENDC}")
    for i, quest in enumerate(available_quests):
        print(f"  {Colors.BRIGHT_YELLOW}{i + 1}. {quest['name']}{Colors.ENDC}: {quest['description']}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}------------------------{Colors.ENDC}")

    while True:
        try:
            choice = input(
                f"Enter the number of the quest to accept (or '{Colors.BRIGHT_RED}0{Colors.ENDC}' to decline):"
                f" {Colors.BRIGHT_BLUE}").strip()
            print(Colors.ENDC, end='')
            if choice == '0':
                print(f"{Colors.BRIGHT_YELLOW}You decided not to take any new quests.{Colors.ENDC}")
                return

            choice_index = int(choice) - 1
            if 0 <= choice_index < len(available_quests):
                selected_quest = available_quests[choice_index]
                player.current_quests.append(selected_quest['name'])
                print(f"\n{Colors.BRIGHT_GREEN}Quest Accepted: {selected_quest['name']}!{Colors.ENDC}")
                print(f"  Description: {selected_quest['description']}")
                break
            else:
                print(f"{Colors.BRIGHT_RED}Invalid number. Please try again.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input. Please enter a number.{Colors.ENDC}")


def check_and_complete_quests(player):
    quests_to_remove = []
    for quest_name in player.current_quests:
        quest_def = QUEST_DEFINITIONS.get(quest_name)
        if not quest_def:
            print(
                f"{Colors.BRIGHT_YELLOW}Warning: Active quest '{quest_name}' not found in quest definitions. "
                f"Removing it.{Colors.ENDC}")
            quests_to_remove.append(quest_name)
            continue

        completed = False
        if quest_def['type'] == "defeat_enemies":
            if player.enemies_defeated.get(quest_def['target_enemy'], 0) >= quest_def['target_count']:
                completed = True
                player.enemies_defeated[quest_def['target_enemy']] = 0
        elif quest_def['type'] == "gather_items":
            if player.items_gathered.get(quest_def['target_item'], 0) >= quest_def['target_count']:
                completed = True
                for _ in range(quest_def['target_count']):
                    if quest_def['target_item'] in player.inventory:
                        player.inventory.remove(quest_def['target_item'])
                player.items_gathered[quest_def['target_item']] = 0
        elif quest_def['type'] == "item_find":
            if quest_def['target_item'] in player.inventory:
                completed = True
                player.inventory.remove(quest_def['target_item'])

        elif quest_def['type'] == "reach_location":
            if player.location == quest_def['target_location']:
                completed = True

        if completed:
            print(f"\n{Colors.BRIGHT_GREEN}{Colors.BOLD}QUEST COMPLETED: {quest_name}!{Colors.ENDC}")
            if 'reward_hp' in quest_def:
                player.hp = min(player.max_hp, player.hp + quest_def['reward_hp'])
                print(f"  You restored {Colors.BRIGHT_GREEN}{quest_def['reward_hp']} HP!{Colors.ENDC}")
            if 'reward_skill' in quest_def:
                for skill, value in quest_def['reward_skill'].items():
                    player.skills[skill] += value
                    print(f"  Your {skill} increased by {Colors.BRIGHT_CYAN}{value}!{Colors.ENDC}")
            if 'reward_item' in quest_def:
                if quest_def['reward_item'] in ITEM_DEFINITIONS:
                    player.inventory.append(quest_def['reward_item'])
                    print(f"  You received {Colors.BRIGHT_GREEN}{quest_def['reward_item']}!{Colors.ENDC}")
                else:
                    print(
                        f"{Colors.BRIGHT_YELLOW}Warning: Reward item '{quest_def['reward_item']}' "
                        f"not found in item definitions.{Colors.ENDC}")

            player.completed_quests.append(quest_name)
            quests_to_remove.append(quest_name)

    for quest_name in quests_to_remove:
        if quest_name in player.current_quests:
            player.current_quests.remove(quest_name)


def save_game(player):
    while True:
        filename = input(
            f"Enter a save file name (e.g., {Colors.BRIGHT_BLUE}my_game{Colors.ENDC}): {Colors.BRIGHT_BLUE}").strip()
        print(Colors.ENDC, end='')
        if not filename:
            print(f"{Colors.BRIGHT_RED}File name cannot be empty. Please try again.{Colors.ENDC}")
            continue
        full_filename = f"save_{filename}.json"
        try:
            with open(full_filename, "w") as f:
                json.dump(player.to_dict(), f, indent=2)
            print(f"{Colors.BRIGHT_GREEN}Game saved successfully to {full_filename}{Colors.ENDC}")
            break
        except IOError:
            print(f"{Colors.BRIGHT_RED}Error saving game to {full_filename}. Please try a different name.{Colors.ENDC}")


def load_game():
    files = [f for f in os.listdir() if f.startswith("save_") and f.endswith(".json")]
    if not files:
        print(f"{Colors.BRIGHT_YELLOW}No saved games found.{Colors.ENDC}")
        return None

    print(f"\n{Colors.BOLD}{Colors.BRIGHT_CYAN}--- Available Saved Games ---{Colors.ENDC}")
    for i, f in enumerate(files):
        print(f"  {Colors.BRIGHT_YELLOW}{i + 1}. {f[5:-5]}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_CYAN}----------------------------{Colors.ENDC}")

    while True:
        try:
            choice_input = input(
                f"Enter the number of the save file to load (or '{Colors.BRIGHT_RED}c{Colors.ENDC}' to cancel):"
                f" {Colors.BRIGHT_BLUE}").strip().lower()
            print(Colors.ENDC, end='')

            if choice_input == 'c':
                return None
            index = int(choice_input) - 1
            if 0 <= index < len(files):
                filename = files[index]
                try:
                    with open(filename, "r") as f:
                        data = json.load(f)
                    loaded_player = Player.from_dict(data)
                    loaded_player._loaded_from_filename = filename
                    return loaded_player
                except FileNotFoundError:
                    print(f"{Colors.BRIGHT_RED}Error: Save file {filename} not found.{Colors.ENDC}")
                    return None
                except json.JSONDecodeError:
                    print(f"{Colors.BRIGHT_RED}Error reading save file {filename}. It might be corrupted.{Colors.ENDC}")
                    return None
            else:
                print(f"{Colors.BRIGHT_RED}Invalid number. Please try again.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input. Please enter a number or 'c'.{Colors.ENDC}")


def heal_player(player):
    player_edible_items = [item for item in player.inventory if item in EDIBLE_ITEMS]

    if not player_edible_items:
        print(f"{Colors.BRIGHT_YELLOW}You have no edible items in your inventory.{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}--- Edible Items in Inventory ---{Colors.ENDC}")
    for i, item in enumerate(player_edible_items):
        print(f"  {Colors.BRIGHT_YELLOW}{i + 1}. {item}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}---------------------------------{Colors.ENDC}")

    while True:
        try:
            choice = input(
                f"Enter the number of the item to eat (or '{Colors.BRIGHT_RED}0{Colors.ENDC}' to cancel):"
                f" {Colors.BRIGHT_BLUE}").strip()
            print(Colors.ENDC, end='')

            if choice == '0':
                print(f"{Colors.BRIGHT_YELLOW}You decided not to eat anything.{Colors.ENDC}")
                return

            choice_index = int(choice) - 1
            if 0 <= choice_index < len(player_edible_items):
                item_to_eat = player_edible_items[choice_index]
                item_props = ITEM_DEFINITIONS.get(item_to_eat)

                if item_props and item_props.get('edible'):
                    heal_amount = random.randint(item_props.get('heal_min', 0), item_props.get('heal_max', 0))

                    player.hp = min(player.max_hp, player.hp + heal_amount)
                    player.inventory.remove(item_to_eat)
                    print(f"{Colors.BRIGHT_GREEN}You ate the {item_to_eat} and restored {heal_amount} HP!{Colors.ENDC}")
                    player.status()
                    break
                else:
                    print(f"{Colors.BRIGHT_RED}This item cannot be eaten. Please choose an edible item.{Colors.ENDC}")
            else:
                print(f"{Colors.BRIGHT_RED}Invalid number. Please try again.{Colors.ENDC}")
        except ValueError:
            print(f"{Colors.BRIGHT_RED}Invalid input. Please enter a number.{Colors.ENDC}")


def explore(player):
    location = generate_location()
    player.location = location.name
    location.show()

    if random.random() < 0.25:  # 25% chance to offer a quest
        choose_quest(player)

    check_and_complete_quests(player)

    while True:
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}--- What's next? ---{Colors.ENDC}")
        action = input(
            f"Actions: {Colors.BRIGHT_CYAN}(take, fight, move, status, eat, quest, save, quit){Colors.ENDC}:"
            f" {Colors.BRIGHT_BLUE}").strip().lower()
        print(Colors.ENDC, end='')
        print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}--------------------{Colors.ENDC}")

        if action == "take":
            if location.items:
                item_name = location.items.pop(random.randrange(len(location.items)))
                if item_name in ITEM_DEFINITIONS:
                    player.inventory.append(item_name)
                    print(f"{Colors.BRIGHT_GREEN}You picked up: {item_name}{Colors.ENDC}")

                    player.items_gathered[item_name] = player.items_gathered.get(item_name, 0) + 1
                    check_and_complete_quests(player)
                else:
                    print(
                        f"{Colors.BRIGHT_YELLOW}You found an unknown item: {item_name}."
                        f" It's probably useless.{Colors.ENDC}")
            else:
                print(f"{Colors.BRIGHT_YELLOW}Nothing left to take here.{Colors.ENDC}")
        elif action == "fight":
            if location.enemies:
                enemy = location.enemies.pop(random.randrange(len(location.enemies)))
                damage = random.randint(5, 20)
                player.hp -= damage
                print(f"{Colors.BRIGHT_RED}You fought the {enemy} and lost {damage} HP!{Colors.ENDC}")

                player.enemies_defeated[enemy] = player.enemies_defeated.get(enemy, 0) + 1

                check_and_complete_quests(player)
                if player.hp <= 0:
                    print(
                        f"\n{Colors.BRIGHT_RED}{Colors.BOLD}!!! You have fallen in battle..."
                        f" Game Over !!!{Colors.ENDC}")
                    sys.exit()
            else:
                print(f"{Colors.BRIGHT_BLUE}No enemies here to fight.{Colors.ENDC}")
        elif action == "move":
            print(f"{Colors.BRIGHT_BLUE}You move to a new mysterious location...{Colors.ENDC}")
            check_and_complete_quests(player)
            return
        elif action == "status":
            player.status()
        elif action == "eat":
            heal_player(player)
        elif action == "quest":
            choose_quest(player)
        elif action == "save":
            save_game(player)
        elif action == "quit":
            print(f"{Colors.BRIGHT_BLUE}Farewell, brave adventurer! Hope to see you again soon.{Colors.ENDC}")
            sys.exit()
        else:
            print(
                f"{Colors.BRIGHT_RED}Invalid action. "
                f"Please choose from (take, fight, move, status, eat, quest, save, quit).{Colors.ENDC}")


def main():
    print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}======================================{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}  Welcome to the ASCII RPG Adventure! {Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}======================================{Colors.ENDC}\n")

    player = None
    game_loaded_successfully = False

    while player is None:
        choice = input(
            f"Do you want to ({Colors.BRIGHT_GREEN}n{Colors.ENDC})ew game or"
            f" ({Colors.BRIGHT_BLUE}l{Colors.ENDC})oad game? {Colors.BRIGHT_BLUE}").strip().lower()
        print(Colors.ENDC, end='')

        if choice == 'l':
            temp_player = load_game()
            if temp_player:
                player = temp_player
                game_loaded_successfully = True
            else:
                print(
                    f"{Colors.BRIGHT_YELLOW}Could not load game or load cancelled."
                    f" Please choose to start a new game or try again.{Colors.ENDC}")

        elif choice == 'n':
            name_input = input(
                f"Enter your name ({Colors.BRIGHT_BLUE}Adventurer{Colors.ENDC}): {Colors.BRIGHT_BLUE}").strip()
            print(Colors.ENDC, end='')
            if not name_input:
                name_input = "Adventurer"
            player = Player(name_input)

        else:
            print(
                f"{Colors.BRIGHT_RED}Invalid choice. Please enter 'n' for new game or 'l' for load game.{Colors.ENDC}")

    clear_screen()

    if game_loaded_successfully:
        filename_msg = f" from {player._loaded_from_filename}" if hasattr(player, '_loaded_from_filename') else ""
        print(f"{Colors.BRIGHT_GREEN}Game loaded successfully{filename_msg}.{Colors.ENDC}")
        print(f"\n{Colors.BRIGHT_GREEN}Welcome back, {player.name}!{Colors.ENDC}")
        player.status()
    else:
        print(f"\n{Colors.BRIGHT_GREEN}Greetings, {player.name}! Your journey begins...{Colors.ENDC}")

    first_location_has_been_displayed = False

    while True:
        if first_location_has_been_displayed:
            clear_screen()

        explore(player)

        first_location_has_been_displayed = True


if __name__ == "__main__":
    main()
