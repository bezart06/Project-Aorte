# Project Aorte

[![Windows-Terminal-wg-Q9-YPJg-Hh.png](https://i.postimg.cc/XYfvcVs5/Windows-Terminal-wg-Q9-YPJg-Hh.png)](https://postimg.cc/YvSktwK2) 
*A classic terminal-based RPG experience.*

---

## About The Project

Project Aorte is a lightweight, turn-based role-playing game that runs entirely in your terminal. It is built with Python and harks back to the classic text-based RPGs, focusing on exploration, quests, and tactical combat.

The project was built to be straightforward, fun, and easily extensible. All game data (items, quests, enemies) is stored in easy-to-edit `.json` files.

## Key Features

* **Turn-Based Tactical Combat:** Engage enemies in a strategic combat system where your core skills (`Strength`, `Agility`, `Wisdom`) directly impact damage, evasion, and special insights.
* **Dynamic World:** Explore procedurally generated locations that make every journey unique.
* **Quest System:** Accept and complete quests to earn rewards and advance your character.
* **Automatic Updates:** The game automatically checks for new versions on startup and allows you to download and apply them seamlessly.
* **Smart Theming:** The user interface automatically detects your terminal's light or dark theme for optimal readability.
* **Zero Dependencies:** Runs on any system with Python 3, including Windows and Linux, with no external libraries required.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

You only need Python 3 installed on your system. No external libraries are required.
* [Python 3](https://www.python.org/downloads/)

### Installation

1.  Clone the repo:
    ```sh
    git clone https://github.com/bezart06/Project-Aorte.git
    ```
2.  Navigate to the project directory:
    ```sh
    cd Project-Aorte
    ```
3.  Run the game:
    ```sh
    python main.py
    ```
    ... or `python3 main.py` on some Linux systems.

## Usage

Navigate the game menus using the **arrow keys** (Up/Down) and make selections with the **Enter** key.

In each area, you can choose from a list of actions:
* **Take an item:** Add a present item to your inventory (if available).
* **Fight an enemy:** Engage a nearby enemy in combat (if available).
* **Move to a new area:** Generate a new location and continue your exploration.
* **View Status:** Check your current HP, skills, inventory, and active quests.
* **Eat an item:** Consume an edible item from your inventory to restore health.
* **View Quests:** See a list of available quests and accept new ones.
* **Save Game:** Save your progress to a file.
* **Quit Game:** Exit the game.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also open an issue with the tag "enhancement".

1.  **Fork the Project**
2.  **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3.  **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4.  **Push to the Branch** (`git push origin feature/AmazingFeature`)
5.  **Open a Pull Request**

You can also contribute by expanding the `items.json`, `quests.json` and `enemies.json` files with new content!

## License

Distributed under the MIT Licence. See `LICENSE.txt` for more information.

## Wiki

*(Currently in developing...)*

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/bezart06/Project_Aorte)
