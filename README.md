# Project Aorte

[![Windows-Terminal-wg-Q9-YPJg-Hh.png](https://i.postimg.cc/XYfvcVs5/Windows-Terminal-wg-Q9-YPJg-Hh.png)](https://postimg.cc/YvSktwK2) 
*A classic terminal-based RPG experience.*

---

## About The Project

Project Aorte is a lightweight, turn-based role-playing game that runs entirely in your terminal. It is built with Python and harks back to the classic text-based RPGs of the 80s and 90s, focusing on exploration, quests, and simple combat.

The game features:
* **Dynamic World:** Procedurally generated locations make every journey unique.
* **Quest System:** Accept and complete quests to earn rewards and advance your character.
* **Simple Inventory:** Find and use a variety of items, including healing herbs and powerful artifacts.
* **Modular Codebase:** A separated interface and game logic make it easy to modify and expand.
* **Cross-Platform:** Runs on any system with Python 3, including Windows, macOS, and Linux.

This project was built to be straightforward, fun, and easily extensible. All game data (items, quests) is stored in easy-to-edit `.json` files.

---

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

You only need Python 3 installed on your system. No external libraries are required.
* [Python 3](https://www.python.org/downloads/)

### Installation

1.  Clone the repo:
    ```sh
    git clone https://github.com/bezart06/Project_Aorte.git
    ```
2.  Navigate to the project directory:
    ```sh
    cd Project_Aorte
    ```
3.  Run the game:
    ```sh
    python main.py
    ```

---

## Usage

Navigate the game menus using the **arrow keys** (Up/Down) and make selections with the **Enter** key.

The game loop is based on exploring new areas. In each area, you can choose from a list of actions:
* **Take an item:** If items are present, you can add one to your inventory.
* **Fight an enemy:** If enemies are nearby, you can engage in combat. This is currently a simple exchange of damage.
* **Move to a new area:** This will generate a new location and is the primary way to explore.
* **View Status:** Check your current HP, skills, and active quests.
* **Eat an item:** Consume an edible item from your inventory to restore health.
* **View Quests:** See a list of available quests and accept new ones.
* **Save/Quit:** Save your progress or exit the game.

---

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also open an issue with the tag "enhancement".

1.  **Fork the Project**
2.  **Create your Feature Branch** (`git checkout -b feature/AmazingFeature`)
3.  **Commit your Changes** (`git commit -m 'Add some AmazingFeature'`)
4.  **Push to the Branch** (`git push origin feature/AmazingFeature`)
5.  **Open a Pull Request**

You can also contribute by expanding the `items.json` and `quests.json` files with new content!

---

## License

Distributed under the MIT Licence. See `LICENSE.txt` for more information.

## Wiki

*(Currently in developing...)*

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/bezart06/Project_Aorte)
