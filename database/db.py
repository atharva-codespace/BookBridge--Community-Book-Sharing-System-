"""
database/db.py
Handles the SQLite database connection for BookBridge.
Uses a Singleton pattern so the whole application shares a single active
connection, and provides small helper methods that always use
parameterized queries (never string concatenation) to prevent SQL Injection.
"""

import os
import sqlite3
from sqlite3 import Error


class Database:

    _instance = None  # Holds the single Database instance (Singleton pattern)

    # ---- SQLite file lives at the project root, next to main.py ----
    # Anchored with os.path (instead of a bare filename) so the same file is
    # used no matter what directory the app is launched from.
    DB_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "book_bank.db",
    )

    def __init__(self):
        # NOTE: Do not call Database() directly - use Database.get_instance()
        self.connection = None
        self._connect()

    @classmethod
    def get_instance(cls):
        """Returns the single shared Database instance (creates it if needed)."""
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    def _connect(self):
        """Opens a connection to the SQLite database file. Raises an exception on failure."""
        try:
            # check_same_thread=False keeps the singleton usable the same way
            # the old shared MySQL connection was.
            self.connection = sqlite3.connect(self.DB_PATH, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # lets rows be read like dicts
            self.connection.execute("PRAGMA foreign_keys = ON")  # SQLite disables FKs by default
        except Error as e:
            print(f"[DATABASE ERROR] Could not connect to SQLite: {e}")
            raise

    def get_connection(self):
        """Returns a live connection, reconnecting automatically if it dropped."""
        try:
            if self.connection is None:
                self._connect()
        except Error as e:
            print(f"[DATABASE ERROR] Reconnection failed: {e}")
            raise
        return self.connection

    @staticmethod
    def _to_qmark(query):
        """Model/service files were written with MySQL-style %s placeholders;
        sqlite3 expects '?'. Converting here keeps that call-site code unchanged."""
        return query.replace("%s", "?")

    def execute_query(self, query, params=None, commit=False):
        """
        Executes an INSERT / UPDATE / DELETE query using a parameterized
        query (params is always a tuple substituted safely by the driver -
        this is what prevents SQL Injection).
        Returns cursor.lastrowid (useful right after an INSERT).
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(self._to_qmark(query), params or ())
            if commit:
                conn.commit()
            return cursor.lastrowid
        except Error as e:
            conn.rollback()
            print(f"[DATABASE ERROR] Query failed: {e}")
            raise
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        """Executes a SELECT query and returns a single row as a dictionary (or None)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(self._to_qmark(query), params or ())
            row = cursor.fetchone()
            return dict(row) if row is not None else None
        except Error as e:
            print(f"[DATABASE ERROR] Query failed: {e}")
            raise
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        """Executes a SELECT query and returns all matching rows as a list of dictionaries."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(self._to_qmark(query), params or ())
            return [dict(row) for row in cursor.fetchall()]
        except Error as e:
            print(f"[DATABASE ERROR] Query failed: {e}")
            raise
        finally:
            cursor.close()

    def close(self):
        """Closes the database connection cleanly. Call on program exit."""
        if self.connection:
            self.connection.close()
            self.connection = None
