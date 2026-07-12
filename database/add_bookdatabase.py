import mysql.connector

try:
    conn = mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12832760",
        password="n9KumuThkc",
        database="sql12832760"
    )

    if conn.is_connected():
        print("Database Connected Successfully")

except mysql.connector.Error as e:
    print("Database Connection Error:", e)