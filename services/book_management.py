"""
services/book_management.py
Module 2 (Book Inventory & Listing Management) and Module 3 (Book Search &
Discovery) business logic. Replaces the old standalone prototypes
(models/add_book.py, update_book.py, delete_book.py, view_books.py,
viewbook.py, searchbook.py) which imported a non-existent `conn`/`cursor`
from `database` and were never reachable from main.py.

Presentation note: only the printed messages/prompts/tables have been
upgraded to utils/ui.py styling. Every field, validation rule, and
database call is unchanged.
"""

from models.book import Book
from models.user import User
from services.validation import Validation
from utils import ui
from utils.helpers import (
    choose_book_condition,
    choose_listing_type,
    confirm_action,
    get_float_input,
    get_non_empty_input,
    print_table,
)

BOOK_TABLE_FIELDS = [
    "Book_ID", "Title", "Author", "ISBN", "Category", "Price", "Availability",
    "Seller_Name", "Phone", "Location", "Book_Condition", "Listing_Type", "Edition",
]


def _book_to_row(book):
    return {
        "Book_ID": book.book_id, "Title": book.title, "Author": book.author,
        "ISBN": book.isbn, "Category": book.category, "Price": book.price,
        "Availability": book.availability, "Seller_Name": book.seller_name,
        "Phone": book.phone, "Location": book.location,
        "Book_Condition": book.book_condition, "Listing_Type": book.listing_type,
        "Edition": book.edition,
    }


def _print_books(books, title=None):
    print_table([_book_to_row(b) for b in books], headers=BOOK_TABLE_FIELDS, title=title)


class BookManagement:
    """Implements every My Listings (Module 2) and Marketplace (Module 3) operation."""

    def __init__(self, session):
        self.session = session

    # ==================== MY LISTINGS (Module 2) ====================
    def add_book(self, listing_type=None):
        """
        `listing_type` lets a role-specific menu (Seller -> Sale, Donor ->
        Donation, Exchange User -> Exchange) preset the listing type so the
        user isn't asked to choose it again; pass None to prompt for it.
        """
        ui.section_header("ADD NEW BOOK LISTING", icon="📚")
        try:
            owner = User.get_by_id(self.session.user_id)

            title = get_non_empty_input("Book Title: ")
            author = get_non_empty_input("Author Name: ")
            isbn = ui.prompt("ISBN (optional)").strip() or None
            category = get_non_empty_input("Category: ")

            price = get_float_input("Price: ")
            location = ui.prompt("Location", default=owner.location).strip() or owner.location

            book_condition = choose_book_condition()
            #if listing_type is None:
           #     listing_type = choose_listing_type()
            edition = ui.prompt("Edition (optional)").strip() or None

            Book.create(
                title=title, author=author, isbn=isbn, category=category, price=price,
                seller_name=owner.full_name, phone=owner.phone_number, location=location,
                book_condition=book_condition, listing_type=listing_type, edition=edition,
                owner_id=self.session.user_id,
            )
            ui.success(f"Book '{title}' added successfully.")
        except Exception as e:
            ui.error(f"Failed to add book: {e}")

    def view_my_listings(self):
        books = Book.get_by_owner(self.session.user_id)
        _print_books(books, title="MY BOOK LISTINGS")

    def edit_book(self):
        book = self._select_own_book("edit")
        if not book:
            return

        ui.section_header("EDIT BOOK", icon="✏️")
        ui.info("Press Enter to keep the current value.")
        title = ui.prompt("Title", default=book.title).strip() or book.title


        author = ui.prompt("Author", default=book.author).strip() or book.author
        isbn = ui.prompt("ISBN", default=book.isbn or "").strip() or book.isbn
        category = ui.prompt("Category", default=book.category).strip() or book.category

        price_input = ui.prompt(f"Price (current: {book.price}, blank to keep)").strip()
        if price_input and not Validation.validate_price(price_input):
            ui.error("Invalid price. Update cancelled.")
            return
        price = float(price_input) if price_input else book.price

        location = ui.prompt("Location", default=book.location).strip() or book.location
        ui.info(f"Current Condition: {book.book_condition}")
        book_condition = choose_book_condition()
        #print(f"Current Listing Type: {book.listing_type}")
        #listing_type = choose_listing_type()
        edition = ui.prompt("Edition", default=book.edition or "").strip() or book.edition

        Book.update(
            book.book_id, title, author, isbn, category, price, book.seller_name,
            book.phone, location, book_condition, book.listing_type, edition,
        )
        ui.success("Book updated successfully.")

    def delete_book(self):
        book = self._select_own_book("delete")
        if book and confirm_action(f"Confirm deletion of '{book.title}'?"):
            Book.soft_delete(book.book_id)
            ui.success("Book deleted successfully.")
        elif book:
            ui.warning("Deletion cancelled.")

    def _select_own_book(self, action_name):
        bname = ui.prompt(f"Enter Book Name to {action_name}").strip()
        if not Book.search("title",bname):
            ui.error("Invalid Book ID.")
            return None
        book = Book.get_by_id(bname)
        if not book:
            ui.error("Book not found.")
            return None
        if book.owner_id != self.session.user_id:
            ui.error("You can only manage your own listings.")
            return None
        return book

    # ==================== MARKETPLACE (Module 3) ====================
    def browse_books(self):
        ui.menu(
            "BROWSE BOOKS",
            [
                ("1", "All Books", "📚"),
                ("2", "Available for Sale", "💰"),
                # ("3", "Available for Donation", "🎁"),
                # ("4", "Available for Exchange", "🔄"),
            ],
            icon="📚",
        )
        choice = ui.prompt("Enter choice").strip()

        if choice == "1":
            _print_books(Book.get_all(), title="ALL BOOKS")
        elif choice == "2":
            _print_books(Book.get_by_listing_type("Sale"), title="BOOKS FOR SALE")
        elif choice == "3":
            _print_books(Book.get_by_listing_type("Donation"), title="BOOKS FOR DONATION")
        elif choice == "4":
            _print_books(Book.get_by_listing_type("Exchange"), title="BOOKS FOR EXCHANGE")
        else:
            ui.warning("Invalid choice.")

    def search_books(self):
        ui.menu(
            "SEARCH BOOKS",
            [
                ("1", "By Title", "🔤"),
                ("2", "By Author", "✍️"),
                ("3", "By ISBN", "🔢"),
                ("4", "By Category", "🏷️"),
                ("5", "By Price Range", "💰"),
                ("6", "By Availability", "📶"),
                ("7", "By Location", "📍"),
                ("8", "By Condition", "🧾"),
                ("9", "By Edition", "📖"),
            ],
            icon="🔍",
        )
        choice = ui.prompt("Enter choice").strip()

        try:
            if choice == "1":
                books = Book.search("title", get_non_empty_input("Title: "))
            elif choice == "2":
                books = Book.search("author", get_non_empty_input("Author: "))
            elif choice == "3":
                books = Book.search("isbn", get_non_empty_input("ISBN: "))
            elif choice == "4":
                books = Book.search("category", get_non_empty_input("Category: "))
            elif choice == "5":
                minimum = get_float_input("Minimum Price: ")
                maximum = get_float_input("Maximum Price: ")
                books = Book.search("price_range", (minimum, maximum))
            elif choice == "6":
                status = get_non_empty_input("Availability (Available/Reserved/Sold/Donated/Exchanged): ")
                books = Book.search("availability", status)
            elif choice == "7":
                books = Book.search("location", get_non_empty_input("Location: "))
            elif choice == "8":
                books = Book.search("condition", choose_book_condition())
            elif choice == "9":
                books = Book.search("edition", get_non_empty_input("Edition: "))
            else:
                ui.warning("Invalid choice.")
                return
        except Exception as e:
            ui.error(f"Search failed: {e}")
            return

        _print_books(books, title="SEARCH RESULTS")

    # ==================== ADMIN MODERATION ====================
    def admin_view_all_books(self):
        _print_books(Book.get_all(), title="ALL BOOK LISTINGS (ADMIN VIEW)")

    def admin_delete_book(self):
        bid = ui.prompt("Enter Book ID to delete").strip()
        if not bid.isdigit():
            ui.error("Invalid Book ID.")
            return
        book = Book.get_by_idd(int(bid))
        if not book:
            ui.error("Book not found.")
            return
        if confirm_action(f"Confirm admin deletion of '{book.title}'?"):
            Book.soft_delete(book.book_id)
            ui.success("Book deleted successfully.")
        else:
            ui.warning("Deletion cancelled.")
