import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "sql12.freesqldatabase.com",
    "user": "sql12832760",
    "password": "n9KumuThkc",
    "database": "sql12832760",
    "port": 3306
}

def get_connection():
    """Returns a new mysql.connector connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Database connection failed: {e}")
        raise