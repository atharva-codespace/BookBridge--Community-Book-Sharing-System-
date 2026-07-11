"""
utils/helpers.py
General-purpose helper functions used across the application
(screen handling, safe input readers, confirmations, date/time helpers).
"""

import os
from datetime import datetime


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

