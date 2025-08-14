# Text User Interface (TUI) Library for Aorte Project
# Handles low-level console drawing and input.

import os
import sys
import time
import subprocess

# The TUI now attempts to automatically detect the terminal theme.
# It checks OS-level settings first, then falls back to environment variables.
#
# You can still manually override the theme by setting 'TERMINAL_THEME':
# On Linux:
#   export TERMINAL_THEME='light'
#
# On Windows (CMD):
#   set TERMINAL_THEME=light


def _get_linux_de_theme():
    de_checks = [
        {
            "command": ['gsettings', 'get', 'org.gnome.desktop.interface', 'color-scheme'],
            "parser": lambda out: 'light' if 'light' in out else ('dark' if 'dark' in out else None)
        },
        {
            "command": ['gsettings', 'get', 'org.cinnamon.desktop.interface', 'gtk-theme'],
            "parser": lambda out: 'dark' if 'dark' in out or 'black' in out else None
        },
        {
            "command": ['gsettings', 'get', 'org.mate.interface', 'gtk-theme'],
            "parser": lambda out: 'dark' if 'dark' in out or 'black' in out else None
        },
        {
            "command": ['kreadconfig5', '--group', 'General', '--key', 'ColorScheme'],
            "parser": lambda out: 'dark' if 'dark' in out else None
        },
        {
            "command": ['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'],
            "parser": lambda out: 'dark' if 'dark' in out else None
        }
    ]

    for check in de_checks:
        try:
            result = subprocess.run(check["command"],
                                    capture_output=True, text=True, check=False).stdout.strip().lower()
            if result:
                theme = check["parser"](result)
                if theme:
                    return theme
        except (FileNotFoundError, subprocess.SubprocessError):
            continue

    return None


def _detect_terminal_theme():
    """
    Automatically detect the terminal background theme.
    Returns 'light' or 'dark'.
    Detection Order:
    1. Manual override via TERMINAL_THEME environment variable.
    2. Platform-specific OS settings (Windows, or various Linux DEs).
    3. Fallback to a default of 'dark'.
    """
    # 1. Manual Override (highest priority)
    manual_theme = os.getenv('TERMINAL_THEME', '').lower()
    if manual_theme in ['light', 'dark']:
        return manual_theme

    # 2. Platform-specific detection
    platform = sys.platform
    try:
        if platform == "win32":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
            if winreg.QueryValueEx(key, 'AppsUseLightTheme')[0] == 1:
                return 'light'
        elif platform.startswith("linux"):
            theme = _get_linux_de_theme()
            if theme:
                return theme

    except (ImportError, FileNotFoundError, OSError, subprocess.SubprocessError):
        pass

    return 'dark'


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
            return ""
        elif key == b'\r':
            return "ENTER"

        try:
            return key.decode('utf-8').upper()
        except UnicodeDecodeError:
            return ""


class _ColorScheme:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    INVERSE = '\033[7m'

    def __init__(self, light_mode=False):
        """
        Initialize the color palette based on the selected theme.
        Args:
            light_mode (bool): If True, use colors suitable for light backgrounds.
        """
        if light_mode:
            self.BRIGHT_MAGENTA = '\033[35m'
            self.BRIGHT_BLUE = '\033[34m'
            self.BRIGHT_CYAN = '\033[36m'
            self.BRIGHT_GREEN = '\033[32m'
            self.BRIGHT_YELLOW = '\033[33m'
            self.BRIGHT_RED = '\033[31m'

            self.BLUE = '\033[34m'
            self.GREEN = '\033[32m'
            self.YELLOW = '\033[33m'
            self.RED = '\033[31m'
            self.MAGENTA = '\033[35m'
            self.CYAN = '\033[36m'
            self.WHITE = '\033[30m'

            self.BLACK_BG = '\033[47m'
            self.WHITE_FG = '\033[30m'
        else:
            self.BRIGHT_MAGENTA = '\033[95m'
            self.BRIGHT_BLUE = '\033[94m'
            self.BRIGHT_CYAN = '\033[96m'
            self.BRIGHT_GREEN = '\033[92m'
            self.BRIGHT_YELLOW = '\033[93m'
            self.BRIGHT_RED = '\033[91m'

            self.BLUE = '\033[34m'
            self.GREEN = '\033[32m'
            self.YELLOW = '\033[33m'
            self.RED = '\033[31m'
            self.MAGENTA = '\033[35m'
            self.CYAN = '\033[36m'
            self.WHITE = '\033[37m'

            self.BLACK_BG = '\033[40m'
            self.WHITE_FG = '\033[37m'


Colors = _ColorScheme(light_mode=(_detect_terminal_theme() == 'light'))


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
        add_cancel (bool): If true, adds a 'Q' to quit option.

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
