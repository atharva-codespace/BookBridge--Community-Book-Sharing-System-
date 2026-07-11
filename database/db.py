"""
database/db.py
Handles the MySQL database connection for the Book Bank Management System.
Uses a Singleton pattern so the whole application shares a single active
connection, and provides small helper methods that always use
parameterized queries (never string concatenation) to prevent SQL Injection.
"""

import mysql.connector
from mysql.connector import Error


class Database:
  

    _instance = None  # Holds the single Database instance (Singleton pattern)

    # ---- CHANGE THESE VALUES TO MATCH YOUR MYSQL SETUP ----
    DB_CONFIG = {
        "host": "sql12.freesqldatabase.com",
        "user": "sql12832760",
        "password": "n9KumuThkc",
        "database": "sql12832760",
    }

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
        """Opens a connection to the MySQL server. Raises an exception on failure."""
        try:
            self.connection = mysql.connector.connect(**self.DB_CONFIG)
        except Error as e:
            print(f"[DATABASE ERROR] Could not connect to MySQL: {e}")
            raise

    def get_connection(self):
        """Returns a live connection, reconnecting automatically if it dropped."""
        try:
            if self.connection is None or not self.connection.is_connected():
                self._connect()
        except Error as e:
            print(f"[DATABASE ERROR] Reconnection failed: {e}")
            raise
        return self.connection

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
            cursor.execute(query, params or ())
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
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"[DATABASE ERROR] Query failed: {e}")
            raise
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        """Executes a SELECT query and returns all matching rows as a list of dictionaries."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"[DATABASE ERROR] Query failed: {e}")
            raise
        finally:
            cursor.close()

    def close(self):
        """Closes the database connection cleanly. Call on program exit."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
