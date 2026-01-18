import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="biblioteka_user",
        password="biblioteka_pass",
        database="biblioteka"
    )

    cur = conn.cursor(dictionary=True)  # zwraca wyniki jako dict
    print("Połączono z bazą")
except Error as e:
    print("Błąd połączenia:", e)

