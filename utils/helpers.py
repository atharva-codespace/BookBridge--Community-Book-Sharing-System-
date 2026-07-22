"""
utils/helpers.py
General-purpose helper functions used across the application (screen
handling, safe input readers, confirmations, date/time helpers).

These keep their exact original names and signatures - every existing
service file already imports from here (`from utils.helpers import
get_non_empty_input, print_table, ...`), so NONE of those call sites need
to change. Only the presentation underneath has been upgraded to the
Rich-based utils/ui.py toolkit (see that module for the actual styling).
"""

from datetime import datetime

from utils import ui

BOOK_CONDITIONS = ["New", "Like New", "Good", "Fair", "Used"]
LISTING_TYPES = ["Sale", "Donation", "Exchange"]


def clear_screen():
    """Clears the terminal screen (cross-platform, handled by Rich's Console)."""
    ui.clear_screen()


def print_header(title: str):
    """Prints a formatted, bordered section header."""
    ui.section_header(title)


def pause():
    """Pauses execution until the user presses Enter."""
    ui.pause()


def get_current_date():
    """Returns today's date as a date object."""
    return datetime.now().date()


def get_current_time():
    """Returns the current time formatted as HH:MM:SS."""
    return datetime.now().time().strftime("%H:%M:%S")


def _clean_label(prompt_text: str) -> str:
    """Old call sites pass prompts like 'Book Title: ' (trailing colon/space
    for plain input()) - strip that so the Rich prompt doesn't double it up."""
    return prompt_text.strip().rstrip(":").strip()


def get_int_input(prompt: str):
    """Safely reads an integer from the user, re-prompting on invalid input."""
    label = _clean_label(prompt)
    while True:
        value = ui.prompt(label).strip()
        if value.isdigit():
            return int(value)
        ui.error("Invalid input. Please enter a number.")


def get_non_empty_input(prompt: str):
    """Safely reads a non-empty string from the user, re-prompting if blank."""
    label = _clean_label(prompt)
    while True:
        value = ui.prompt(label).strip()
        if value:
            return value
        ui.error("This field cannot be empty. Please try again.")


def confirm_action(prompt: str) -> bool:
    """Asks the user a YES/NO question and returns True/False."""
    return ui.confirm(_clean_label(prompt))


def get_float_input(prompt: str):
    """Safely reads a non-negative float from the user, re-prompting on invalid input."""
    label = _clean_label(prompt)
    while True:
        value = ui.prompt(label).strip()
        try:
            number = float(value)
            if number < 0:
                ui.error("Value cannot be negative. Please try again.")
                continue
            return number
        except ValueError:
            ui.error("Invalid input. Please enter a number.")


def print_table(rows, headers=None, title=None):
    """
    Renders a list of dict rows (as returned by Database.fetch_all/fetch_one)
    as a formatted, colorized Rich table. Used everywhere instead of ad-hoc
    print() loops so every module's output looks consistent.
    """
    ui.table(rows, headers=headers, title=title)


def choose_book_condition() -> str:
    """Prompts for a book condition from the fixed list, returns the chosen value."""
    ui.console.print("\n[bold]Book Condition[/bold]")
    for idx, condition in enumerate(BOOK_CONDITIONS, start=1):
        ui.console.print(f"  [bright_magenta]{idx}[/bright_magenta]. {condition}")
    while True:
        choice = ui.prompt(f"Choose (1-{len(BOOK_CONDITIONS)})").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(BOOK_CONDITIONS):
            return BOOK_CONDITIONS[int(choice) - 1]
        ui.error("Invalid choice. Please try again.")


def choose_listing_type() -> str:
    """Prompts for a listing type from the fixed list, returns the chosen value."""
    ui.console.print("\n[bold]Listing Type[/bold]")
    for idx, listing_type in enumerate(LISTING_TYPES, start=1):
        ui.console.print(f"  [bright_magenta]{idx}[/bright_magenta]. {listing_type}")
    while True:
        choice = ui.prompt(f"Choose (1-{len(LISTING_TYPES)})").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(LISTING_TYPES):
            return LISTING_TYPES[int(choice) - 1]
        ui.error("Invalid choice. Please try again.")
