"""
models/book.py
Defines the Book entity and all database operations (CRUD) for the
Books table. Covers Module 2 (Book Inventory & Listing Management)
and Module 3 (Book Search & Discovery). Every SQL statement uses
parameterized queries (%s placeholders + a params tuple).
"""

from database.db import Database


class Book:
    """Represents a single row from the Books table plus all Book CRUD operations."""

    def __init__(self, book_id=None, title=None, author=None, isbn=None, category=None,
                 price=None, availability=None, seller_name=None, phone=None, location=None,
                 book_condition=None, listing_type=None, edition=None, owner_id=None,
                 listed_date=None, is_deleted=0):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.price = price
        self.availability = availability
        self.seller_name = seller_name
        self.phone = phone
        self.location = location
        self.book_condition = book_condition
        self.listing_type = listing_type
        self.edition = edition
        self.owner_id = owner_id
        self.listed_date = listed_date
        self.is_deleted = is_deleted

    @staticmethod
    def _row_to_book(row):
        """Converts a DB row (dict) into a Book object. Returns None for an empty row."""
        if not row:
            return None
        return Book(
            book_id=row.get("Book_ID"),
            title=row.get("Title"),
            author=row.get("Author"),
            isbn=row.get("ISBN"),
            category=row.get("Category"),
            price=row.get("Price"),
            availability=row.get("Availability"),
            seller_name=row.get("Seller_Name"),
            phone=row.get("Phone"),
            location=row.get("Location"),
            book_condition=row.get("Book_Condition"),
            listing_type=row.get("Listing_Type"),
            edition=row.get("Edition"),
            owner_id=row.get("Owner_ID"),
            listed_date=row.get("Listed_Date"),
            is_deleted=row.get("Is_Deleted", 0),
        )

    # ==================== CREATE ====================
    @classmethod
    def create(cls, title, author, isbn, category, price, seller_name, phone, location,
               book_condition, listing_type, edition, owner_id):
        db = Database.get_instance()
        query = """
            INSERT INTO Books
            (Title, Author, ISBN, Category, Price, Availability, Seller_Name, Phone,
             Location, Book_Condition, Listing_Type, Edition, Owner_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (title, author, isbn, category, price, "Available", seller_name, phone,
                   location, book_condition, listing_type, edition, owner_id)
        return db.execute_query(query, params, commit=True)

    # ==================== READ ====================
    @classmethod
    def get_by_id(cls, book_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Books WHERE Title = %s", (book_id,))
        return cls._row_to_book(row)
    
    @classmethod
    def get_by_idd(cls, book_id):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Books WHERE Book_ID = %s", (book_id,))
        return cls._row_to_book(row)


    @classmethod
    def get_all(cls):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * FROM Books ORDER BY Book_ID DESC")
        return [cls._row_to_book(r) for r in rows]

    @classmethod
    def get_by_owner(cls, owner_id):
        db = Database.get_instance()
        rows = db.fetch_all(
            "SELECT * FROM Books WHERE Owner_ID = %s ORDER BY Book_ID DESC",
            (owner_id,),
        )
        return [cls._row_to_book(r) for r in rows]

    @classmethod
    def get_by_listing_type(cls, listing_type):
        db = Database.get_instance()
        rows = db.fetch_all("SELECT * FROM Books WHERE Listing_Type = %s ORDER BY Book_ID DESC",(listing_type,),)
        return [cls._row_to_book(r) for r in rows]

    @classmethod
    def search_by_availability(cls,book_name):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Books WHERE Title LIKE %s AND Availability='Available'",
    (f"%{book_name}%",))
        return cls._row_to_book(row)
    
    @classmethod
    def search_book(cls,book_name):
        db = Database.get_instance()
        row = db.fetch_one("SELECT * FROM Books WHERE Title LIKE %s",(f"%{book_name}%",))
        return cls._row_to_book(row)

    @classmethod
    def search(cls, field, value):
        """
        Generic search used by Module 3 (Book Search & Discovery).
        `field` selects the search mode; `value` is the search term
        (a (min, max) tuple for 'price_range').
        """
        db = Database.get_instance()
        base = "SELECT * FROM Books WHERE "

        if field == "title":
            rows = db.fetch_all(base + "Title LIKE %s", (f"%{value}%",))
        elif field == "author":
            rows = db.fetch_all(base + "Author LIKE %s", (f"%{value}%",))
        elif field == "isbn":
            rows = db.fetch_all(base + "ISBN = %s", (value,))
        elif field == "category":
            rows = db.fetch_all(base + "Category = %s", (value,))
        elif field == "price_range":
            minimum, maximum = value
            rows = db.fetch_all(base + "Price BETWEEN %s AND %s", (minimum, maximum))
        elif field == "availability":
            rows = db.fetch_all(base + "Availability = %s", (value,))
        elif field == "location":
            rows = db.fetch_all(base + "Location LIKE %s", (f"%{value}%",))
        elif field == "condition":
            rows = db.fetch_all(base + "Book_Condition = %s", (value,))
        elif field == "edition":
            rows = db.fetch_all(base + "Edition = %s", (value,))
        else:
            raise ValueError(f"Unknown search field: {field}")

        return [cls._row_to_book(r) for r in rows]

    @classmethod
    def searchinwishlist(cls, field, value):
        """
        Generic search used by Module 3 (Book Search & Discovery).
        `field` selects the search mode; `value` is the search term
        (a (min, max) tuple for 'price_range').
        """
        db = Database.get_instance()
        base = "SELECT * FROM wishlist WHERE "

        if field == "title":
            rows = db.fetch_all(base + "book_name LIKE %s", (f"%{value}%",))
        else:
            raise ValueError(f"Unknown search field: {field}")

        return [cls._row_to_book(r) for r in rows]
    
    @classmethod
    def searchinreservations(cls, field, value):
        """
        Generic search used by Module 3 (Book Search & Discovery).
        `field` selects the search mode; `value` is the search term
        (a (min, max) tuple for 'price_range').
        """
        db = Database.get_instance()
        base = "SELECT * FROM reservations WHERE "

        if field == "title":
            rows = db.fetch_all(base + "book_name LIKE %s", (f"%{value}%",))
        else:
            raise ValueError(f"Unknown search field: {field}")

        return [cls._row_to_book(r) for r in rows]
    # ==================== UPDATE ====================
    @classmethod
    def update(cls, book_id, title, author, isbn, category, price, seller_name, phone,
               location, book_condition, listing_type, edition):
        db = Database.get_instance()
        query = """
            UPDATE Books
            SET Title = %s, Author = %s, ISBN = %s, Category = %s, Price = %s,
                Seller_Name = %s, Phone = %s, Location = %s, Book_Condition = %s,
                Listing_Type = %s, Edition = %s
            WHERE Book_ID = %s
        """
        params = (title, author, isbn, category, price, seller_name, phone, location,
                  book_condition, listing_type, edition, book_id)
        db.execute_query(query, params, commit=True)

    @classmethod
    def update_availability(cls, book_id, availability):
        db = Database.get_instance()
        db.execute_query(
            "UPDATE Books SET Availability = %s WHERE book_name = %s",
            (availability, book_id), commit=True,
        )

    # ==================== DELETE (soft delete) ====================
    @classmethod
    def soft_delete(cls, book_id):
        db = Database.get_instance()
        db.execute_query(
            "Delete FROM Books WHERE Book_ID = %s",
            (book_id,), commit=True,
        )
