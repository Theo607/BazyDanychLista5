import mysql.connector
from mysql.connector import Error

DB_NAME = "biblioteka"
DB_USER = "root"
DB_PASSWORD = ""  # jeśli nie masz hasła
DB_HOST = "localhost"

try:
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cur = conn.cursor(dictionary=True)  # zwraca wyniki jako dict
    print("Połączono z bazą")
except Error as e:
    print("Błąd połączenia:", e)

