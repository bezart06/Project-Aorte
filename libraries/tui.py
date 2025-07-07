# Text User Interface (TUI) Library for Aorte Project
# Handles low-level console drawing and input.

import os
import sys
import time

# Platform-specific key capture
try:
    import tty
    import termios
    _original_termios = None

    def init_tui():
        """Stores original terminal settings."""
        global _original_termios
        _original_termios = termios.tcgetattr(sys.stdin)

    def cleanup_tui():
        """Restores original terminal settings."""
        if _original_termios:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, _original_termios)

    def get_key():
        """Gets a single key press from the user (Unix)."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
            if key == '\x1b':
                next_key = sys.stdin.read(2)
                if next_key == '[A':
                    return "UP"
                elif next_key == '[B':
                    return "DOWN"
            elif key == '\r':
                return "ENTER"
            return key.upper()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key.upper()

except ImportError:
    import msvcrt

    def init_tui():
        """Placeholder for Windows."""
        pass

    def cleanup_tui():
        """Placeholder for Windows."""
        pass

    def get_key():
        """Gets a single key press from the user (Windows)."""
        key = msvcrt.getch()
        if key == b'\xe0':
            next_key = msvcrt.getch()
            if next_key == b'H':
                return "UP"
            elif next_key == b'P':
                return "DOWN"
            # You could add other arrows like LEFT (b'K') and RIGHT (b'M') here if needed
            return ""
        elif key == b'\r':
            return "ENTER"

        try:
            return key.decode('utf-8').upper()
        except UnicodeDecodeError:
            return ""


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

    BLACK_BG = '\033[40m'
    WHITE_FG = '\033[37m'
    INVERSE = '\033[7m'

    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def render_from_buffer(buffer):
    """Clears the screen and prints content from a list of strings."""
    clear_screen()
    for line in buffer:
        print(line)
    sys.stdout.flush()


def menu(title, options, prompt="Use arrow keys to navigate, Enter to select.", header_text="", add_cancel=True):
    """
    Displays a navigable menu and returns the selected option.

    Args:
        title (str): The title to display above the menu.
        options (list): A list of strings representing the choices.
        prompt (str): A help message displayed below the options.
        header_text (str): Optional multi-line text to display above the title.

    Returns:
        str: The selected option string, or None if the menu is exited.
    """
    if not options:
        return None

    selected_index = 0
    FRAME_RATE = 24
    last_render_time = 0

    while True:
        current_time = time.time()
        if current_time - last_render_time < 1.0 / FRAME_RATE:
            continue
        last_render_time = current_time

        buffer = []
        if header_text:
            buffer.extend(header_text.split('\n'))
            buffer.append("")

        if title:
            buffer.append(f"{Colors.BOLD}{Colors.BRIGHT_MAGENTA}>> {title} <<{Colors.ENDC}\n")

        for i, option in enumerate(options):
            if i == selected_index:
                buffer.append(f"  {Colors.INVERSE} {option} {Colors.ENDC}")
            else:
                buffer.append(f"  {Colors.WHITE}{option}{Colors.ENDC}")

        buffer.append(f"\n{Colors.BRIGHT_CYAN}{prompt}{Colors.ENDC}")

        render_from_buffer(buffer)
        key = get_key()

        if key == "UP":
            selected_index = (selected_index - 1) % len(options)
        elif key == "DOWN":
            selected_index = (selected_index + 1) % len(options)
        elif key == "ENTER":
            clear_screen()
            return options[selected_index]
        elif key in ['Q', '\x03'] and add_cancel:
            clear_screen()
            return None


def create_hp_bar(current, maximum, length, color):
    if maximum == 0:
        percent = 0
    else:
        percent = current / maximum
    filled_length = int(length * percent)
    bar = '█' * filled_length + '-' * (length - filled_length)
    return f"{color}[{bar}]{Colors.ENDC}"
