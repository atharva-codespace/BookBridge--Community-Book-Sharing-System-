"""
utils/helpers.py
General-purpose helper functions used across the application
(screen handling, safe input readers, confirmations, date/time helpers).
"""

import os
from datetime import datetime

from tabulate import tabulate

BOOK_CONDITIONS = ["New", "Like New", "Good", "Fair", "Used"]
LISTING_TYPES = ["Sale", "Donation", "Exchange"]


def clear_screen():
    """Clears the terminal screen (cross-platform: Windows/Linux/Mac)."""
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str):
    """Prints a formatted section header."""
    width = max(30, len(title) + 4)
    print("=" * width)
    print(title.center(width))
    print("=" * width)


def pause():
    """Pauses execution until the user presses Enter."""
    input("\nPress Enter to continue...")


def get_current_date():
    """Returns today's date as a date object."""
    return datetime.now().date()


def get_current_time():
    """Returns the current time formatted as HH:MM:SS."""
    return datetime.now().time().strftime("%H:%M:%S")


def get_int_input(prompt: str):
    """Safely reads an integer from the user, re-prompting on invalid input."""
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("Invalid input. Please enter a number.")


def get_non_empty_input(prompt: str):
    """Safely reads a non-empty string from the user, re-prompting if blank."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def confirm_action(prompt: str) -> bool:
    """Asks the user a YES/NO question and returns True/False."""
    while True:
        choice = input(f"{prompt} (YES/NO): ").strip().upper()
        if choice == "YES":
            return True
        if choice == "NO":
            return False
        print("Please type YES or NO.")


def get_float_input(prompt: str):
    """Safely reads a non-negative float from the user, re-prompting on invalid input."""
    while True:
        value = input(prompt).strip()
        try:
            number = float(value)
            if number < 0:
                print("Value cannot be negative. Please try again.")
                continue
            return number
        except ValueError:
            print("Invalid input. Please enter a number.")


def print_table(rows, headers=None, title=None):
    """
    Renders a list of dict rows (as returned by Database.fetch_all/fetch_one)
    as a formatted table using tabulate. Used everywhere instead of ad-hoc
    print() loops so every module's output looks consistent.
    """
    if title:
        print_header(title)

    if not rows:
        print("No records found.")
        return

    if isinstance(rows, dict):
        rows = [rows]

    display_headers = headers or list(rows[0].keys())
    table_rows = [[row.get(h, "") for h in display_headers] for row in rows]
    print(tabulate(table_rows, headers=display_headers, tablefmt="rounded_grid"))
    print(f"\nTotal Records: {len(rows)}")


def choose_book_condition() -> str:
    """Prompts for a book condition from the fixed list, returns the chosen value."""
    print("\nBook Condition")
    for idx, condition in enumerate(BOOK_CONDITIONS, start=1):
        print(f"{idx}. {condition}")
    while True:
        choice = input(f"Choose (1-{len(BOOK_CONDITIONS)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(BOOK_CONDITIONS):
            return BOOK_CONDITIONS[int(choice) - 1]
        print("Invalid choice. Please try again.")


def choose_listing_type() -> str:
    """Prompts for a listing type from the fixed list, returns the chosen value."""
    print("\nListing Type")
    for idx, listing_type in enumerate(LISTING_TYPES, start=1):
        print(f"{idx}. {listing_type}")
    while True:
        choice = input(f"Choose (1-{len(LISTING_TYPES)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(LISTING_TYPES):
            return LISTING_TYPES[int(choice) - 1]
        print("Invalid choice. Please try again.")

