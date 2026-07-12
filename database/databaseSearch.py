import mysql.connector

conn = mysql.connector.connect(
    host="sql12.freesqldatabase.com",
    user="sql12832760",
    password="n9KumuThkc",
    database="sql12832760",
    port=3306
)

cursor = conn.cursor()

if conn.is_connected():
    print("Online Database Connected Successfully!")
else:
    print("Connection Failed!")