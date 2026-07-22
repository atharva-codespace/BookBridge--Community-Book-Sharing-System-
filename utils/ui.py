"""
utils/ui.py
Centralized terminal presentation layer for BookBridge, built on the `rich` library (with `pyfiglet` used only for the
System Entry banner). This module owns ALL visual styling - colors,
panels, tables, banners, prompts, status/spinner indicators, and the AI
chat-bubble look - so every other file imports a small, consistent set of
helpers instead of hand-rolling print() output.

This module is presentation-only: it has no knowledge of the database,
models, or business rules, and none of the functions below change any
return value or control flow that existing code depends on - they only
change what appears on screen. utils/helpers.py (already imported
everywhere in the project) delegates its display-related functions here,
so most existing call sites across every service file are upgraded
automatically with zero changes to their own code.
"""

from contextlib import contextmanager

from rich.align import Align
from rich.box import HEAVY, ROUNDED
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

try:
    import pyfiglet
    _HAS_FIGLET = True
except ImportError:
    _HAS_FIGLET = False

console = Console()

# ==================== THEME (kept consistent across every screen) ====================
BRAND = "bold bright_cyan"
ACCENT = "bright_magenta"
SUCCESS_STYLE = "bold green"
ERROR_STYLE = "bold red"
WARNING_STYLE = "bold yellow"
INFO_STYLE = "bold cyan"
MUTED = "grey62"
BORDER = "bright_cyan"

ICON_SUCCESS = "✓"
ICON_ERROR = "✗"
ICON_WARNING = "⚠"
ICON_INFO = "ℹ"
ICON_AI = "🤖"

# Status/availability values are colored consistently wherever they appear
# in a table (Books, Requests, Reservations, Deliveries, Users, ...).
_POSITIVE_STATUSES = {
    "available", "active", "approved", "delivered", "completed", "yes", "enabled",
}
_NEUTRAL_STATUSES = {"reserved", "pending", "picked up", "assigned"}
_NEGATIVE_STATUSES = {
    "sold", "donated", "exchanged", "inactive", "rejected", "cancelled",
    "expired", "no", "disabled",
}


# ==================== SCREEN / LAYOUT PRIMITIVES ====================
def clear_screen():
    console.clear()


def banner(title: str, subtitle: str = None, figlet: bool = False):
    """Big bordered title screen. `figlet=True` renders ASCII-art text -
    reserved for the System Entry screen only, per 'don't overuse
    animations' - every other screen uses section_header() instead."""
    if figlet and _HAS_FIGLET:
        try:
            art = pyfiglet.figlet_format(title, font="slant")
            body = Text(art.rstrip("\n"), style=BRAND, justify="center")
        except Exception:
            body = Text(title, style=BRAND, justify="center")
    else:
        body = Text(title, style=BRAND, justify="center")

    console.print()
    console.print(
        Panel(
            Align.center(body),
            border_style=BORDER,
            box=HEAVY,
            padding=(1, 4),
            subtitle=f"[{MUTED}]{subtitle}[/{MUTED}]" if subtitle else None,
            subtitle_align="center",
        )
    )


def section_header(title: str, icon: str = ""):
    """Smaller bordered header used for every submenu/screen title. No
    emoji icon is ever shown - only the title text."""
    console.print()
    console.print(
        Panel(Align.center(Text(title, style=BRAND)), border_style=BORDER, box=ROUNDED, padding=(0, 2))
    )


def menu(title: str, options, icon: str = "", footer: str = None):
    """
    Renders a centered, bordered menu.
    `options` is a list of (key, label) tuples - no icons/emojis anywhere.
    """
    section_header(title)
    body = Text()
    for key, label in options:
        body.append(f"  [{key}] ", style=f"bold {ACCENT}")
        body.append(f"{label}\n", style="white")
    console.print(Panel(body, border_style=BORDER, box=ROUNDED, padding=(1, 3)))
    if footer:
        console.print(Align.center(Text(footer, style=f"italic {MUTED}")))


def rule(label: str = ""):
    console.print(Rule(label, style=BORDER))


# ==================== STATUS MESSAGES ====================
def success(message: str):
    console.print(f"[{SUCCESS_STYLE}]{ICON_SUCCESS}  {message}[/{SUCCESS_STYLE}]")


def error(message: str):
    console.print(Panel(f"[{ERROR_STYLE}]{ICON_ERROR}  {message}[/{ERROR_STYLE}]",
                         border_style="red", box=ROUNDED, padding=(0, 1)))


def warning(message: str):
    console.print(Panel(f"[{WARNING_STYLE}]{ICON_WARNING}  {message}[/{WARNING_STYLE}]",
                         border_style="yellow", box=ROUNDED, padding=(0, 1)))


def info(message: str):
    console.print(f"[{INFO_STYLE}]{message}[/{INFO_STYLE}]")


# ==================== TABLES ====================
def _style_cell(header: str, value) -> str:
    text = "" if value is None else str(value)
    if header.replace(" ", "_").lower() in ("availability", "status", "account_status"):
        v = text.strip().lower()
        if v in _POSITIVE_STATUSES:
            return f"[green]{text}[/green]"
        if v in _NEUTRAL_STATUSES:
            return f"[yellow]{text}[/yellow]"
        if v in _NEGATIVE_STATUSES:
            return f"[red]{text}[/red]"
    return text


def table(rows, headers=None, title: str = None):
    """Drop-in replacement for the old tabulate-based print_table - same
    signature (rows as a list of dicts or a single dict, optional headers
    list, optional title) so every existing call site is unaffected."""
    if title:
        section_header(title)

    if not rows:
        console.print(Align.center(Text("No records found.\n", style=f"italic {MUTED}")))
        return

    if isinstance(rows, dict):
        rows = [rows]

    display_headers = headers or list(rows[0].keys())
    # overflow="ellipsis" + no_wrap keeps every row a single line (truncating
    # long values with "...") instead of Rich's default char-by-char wrap,
    # which turns wide tables (e.g. the 13-column Books table) into tall,
    # hard-to-read cells on a narrow terminal.
    t = Table(box=ROUNDED, border_style=BORDER, header_style=f"bold {ACCENT}",
              show_lines=False, expand=False, pad_edge=True)
    for h in display_headers:
        t.add_column(str(h).replace("_", " "), overflow="ellipsis", no_wrap=True, max_width=18)
    for row in rows:
        t.add_row(*[_style_cell(h, row.get(h, "")) for h in display_headers])

    console.print(t)
    console.print(f"[{MUTED}]Total Records: {len(rows)}[/{MUTED}]\n")


def detail_panel(title: str, fields: dict):
    """Key/value 'card' used for single-record views (View Profile, User
    Details, Book Details, etc.) instead of a loose stack of print() lines."""
    grid = Table.grid(padding=(0, 2))
    grid.add_column(justify="right", style=f"bold {ACCENT}", no_wrap=True)
    grid.add_column(justify="left", style="white")
    for label, value in fields.items():
        grid.add_row(f"{label}:", "" if value is None else str(value))
    console.print(Panel(grid, title=f"[{BRAND}]{title}[/{BRAND}]", border_style=BORDER,
                         box=ROUNDED, padding=(1, 2)))


def stat_panel(title: str, stats: dict):
    """Highlighted key-metric panel used by the Reports screens."""
    grid = Table.grid(padding=(0, 2))
    grid.add_column(justify="right", style=f"bold {ACCENT}", no_wrap=True)
    grid.add_column(justify="left", style="bold white")
    for label, value in stats.items():
        grid.add_row(f"{label}:", str(value))
    console.print(Panel(grid, title=f"[{BRAND}]{title}[/{BRAND}]", border_style=BORDER, box=ROUNDED))


# ==================== PROMPTS ====================
def prompt(label: str, default: str = None, password: bool = False) -> str:
    """Styled replacement for input(). If `default` is given, pressing Enter
    keeps it (Rich shows it in brackets) - this replaces the old
    `input(f"Field [{current}]: ").strip() or current` pattern project-wide.
    `password=True` masks each typed character with '*' (see _masked_input)
    instead of showing nothing at all."""
    if password:
        return _masked_input(label, default=default)
    return Prompt.ask(f"[bold]{label}[/bold]", default=default, console=console)


def _masked_input(label: str, default: str = None) -> str:
    """Reads a line of input character-by-character, echoing '*' for every
    character typed (instead of Rich/getpass's default of echoing nothing),
    so the user gets visual feedback while typing a password. Falls back to
    a silent hidden prompt if raw terminal control isn't available (e.g.
    piped/non-interactive stdin, such as in automated tests)."""
    import sys

    console.print(f"[bold]{label}[/bold]: ", end="")
    sys.stdout.flush()

    try:
        if sys.platform.startswith("win"):
            import msvcrt

            chars = []
            while True:
                ch = msvcrt.getwch()
                if ch in ("\r", "\n"):
                    break
                if ch == "\x03":
                    raise KeyboardInterrupt
                if ch in ("\x08", "\x7f"):  # Backspace
                    if chars:
                        chars.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    continue
                chars.append(ch)
                sys.stdout.write("*")
                sys.stdout.flush()
            console.print()
            result = "".join(chars)
            return result if result else (default if default is not None else "")

        else:
            import termios
            import tty

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            chars = []
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in ("\r", "\n"):
                        break
                    if ch == "\x03":
                        raise KeyboardInterrupt
                    if ch in ("\x7f", "\x08"):  # Backspace
                        if chars:
                            chars.pop()
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                        continue
                    chars.append(ch)
                    sys.stdout.write("*")
                    sys.stdout.flush()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            console.print()
            result = "".join(chars)
            return result if result else (default if default is not None else "")

    except Exception:
        # Raw terminal control isn't available (non-interactive stdin, some
        # IDE consoles, etc.) - fall back to a plain hidden-input prompt
        # rather than crashing the whole login/registration flow.
        import getpass

        try:
            result = getpass.getpass("")
        except Exception:
            result = input()
        return result if result else (default if default is not None else "")


def confirm(label: str) -> bool:
    return Confirm.ask(f"[bold]{label}[/bold]", console=console)


def pause(message: str = "Press Enter to continue..."):
    console.input(f"\n[{MUTED}]{message}[/{MUTED}]")


@contextmanager
def spinner(message: str):
    """Tasteful loading indicator for operations that take a moment: login,
    AI responses, report generation, database setup. Used sparingly."""
    with console.status(f"[bold cyan]{message}...[/bold cyan]", spinner="dots"):
        yield


# ==================== AI CHAT INTERFACE ====================
def chat_user(message: str):
    console.print(Padding(f"[bold bright_white]You[/bold bright_white]  {message}", (0, 0, 0, 2)))


def chat_ai(message: str):
    console.print(Panel(message, title=f"{ICON_AI} AI Assistant", title_align="left",
                         border_style=ACCENT, box=ROUNDED, padding=(0, 1)))


def chat_system(message: str):
    console.print(Align.center(Text(message, style=f"italic {MUTED}")))


def recommendation_panel(title: str, items):
    """
    `items` is a list of (heading, reason) tuples, rendered as a single
    panel with a numbered list - used by AI Book Recommendation.
    """
    body = Text()
    for idx, (heading, reason) in enumerate(items, start=1):
        body.append(f"{idx}. ", style=f"bold {ACCENT}")
        body.append(f"{heading}\n", style="bold white")
        body.append(f"   Reason: ", style=f"italic {MUTED}")
        body.append(f"{reason}\n\n", style=f"italic {MUTED}")
    console.print(Panel(body, title=f"[{BRAND}]{title}[/{BRAND}]", border_style=ACCENT, box=ROUNDED, padding=(1, 2)))
