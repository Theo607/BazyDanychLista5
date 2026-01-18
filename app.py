import mysql.connector
import bcrypt
from getpass import getpass
from tabulate import tabulate

# ---------------- Konfiguracja bazy ----------------
DB_NAME = "biblioteka"
DB_USER = "biblioteka_user"
DB_PASSWORD = "biblioteka_pass"
DB_HOST = "localhost"

# Połączenie z bazą
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cur = conn.cursor(dictionary=True)
print("Połączono z bazą")

# ---------------- Bezpieczeństwo haseł ----------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ---------------- Rejestracja i logowanie ----------------
def register_user():
    username = input("Nazwa użytkownika: ")
    password = getpass("Hasło: ")
    role = input("Rola (reader/librarian): ").lower()
    hashed = hash_password(password)
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            (username, hashed, role)
        )
        conn.commit()
        print("Użytkownik zarejestrowany.")
    except mysql.connector.Error as e:
        conn.rollback()
        print("Błąd:", e)

def login():
    username = input("Nazwa użytkownika: ")
    password = getpass("Hasło: ")
    cur.execute("SELECT user_id, password_hash FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    if not row:
        print("Błędny login lub hasło.")
        return None
    user_id, password_hash = row["user_id"], row["password_hash"]
    if check_password(password, password_hash):
        cur.execute("SELECT check_user_role(%s) AS role", (user_id,))
        role = cur.fetchone()["role"]
        print(f"Zalogowano jako {role}")
        return {"id": user_id, "role": role}
    else:
        print("Błędny login lub hasło.")
        return None

# ---------------- CRUD książek ----------------
def add_book():
    title = input("Tytuł: ")
    author = input("Autor: ")
    category = input("Kategoria: ")
    total = int(input("Liczba egzemplarzy: "))
    try:
        cur.callproc("add_book_proc", [title, author, category, total])
        conn.commit()
        print("Książka dodana.")
    except mysql.connector.Error as e:
        conn.rollback()
        print("Błąd:", e)

def list_books():
    cur.execute("""
        SELECT b.book_id, b.title, a.name AS author, c.name AS category, b.available_copies
        FROM books b
        LEFT JOIN authors a ON b.author_id = a.author_id
        LEFT JOIN categories c ON b.category_id = c.category_id
        ORDER BY b.title
    """)
    rows = cur.fetchall()
    if not rows:
        print("Brak książek w bibliotece.")
        return
    data = [[r["book_id"], r["title"], r["author"], r["category"], r["available_copies"]] for r in rows]
    print(tabulate(data, headers=["ID", "Tytuł", "Autor", "Kategoria", "Dostępne"], tablefmt="grid"))

# ---------------- Wypożyczenia ----------------
def borrow_book(user_id):
    list_books()
    book_id = int(input("ID książki do wypożyczenia: "))
    try:
        cur.callproc("borrow_book_proc", [user_id, book_id])
        conn.commit()
        print("Wypożyczono książkę.")
    except mysql.connector.Error as e:
        conn.rollback()
        print("Błąd:", e)

def return_book(user_id):
    # Pobranie aktywnych wypożyczeń użytkownika
    cur.execute("""
        SELECT borrowing_id, book_id, due_date FROM borrowings 
        WHERE user_id=%s AND return_date IS NULL
    """, (user_id,))
    borrows = cur.fetchall()
    if not borrows:
        print("Brak aktywnych wypożyczeń.")
        return
    data = [[r["borrowing_id"], r["book_id"], r["due_date"]] for r in borrows]
    print(tabulate(data, headers=["ID Wypożyczenia", "ID Książki", "Termin"], tablefmt="grid"))
    borrow_id = int(input("ID wypożyczenia do zwrotu: "))
    try:
        cur.callproc("return_book_proc", [borrow_id])
        conn.commit()
        print("Książka zwrócona.")
    except mysql.connector.Error as e:
        conn.rollback()
        print("Błąd:", e)

# ---------------- Raporty ----------------
def overdue_books():
    # Wywołanie procedury, która SELECTuje
    cur.execute("CALL overdue_books_proc()")  # execute zamiast callproc
    rows = cur.fetchall()  # fetch po execute
    if not rows:
        print("Brak przeterminowanych wypożyczeń.")
        return
    data = [[r["borrowing_id"], r["username"], r["book_title"], r["author_name"], r["category_name"], r["due_date"]] for r in rows]
    print(tabulate(data, headers=["ID Wypożyczenia", "Czytelnik", "Tytuł", "Autor", "Kategoria", "Termin"], tablefmt="grid"))

# ---------------- Menu terminalowe ----------------
def main():
    while True:
        print("\n1. Rejestracja\n2. Logowanie\n3. Wyjście")
        choice = input("Wybierz: ")
        if choice == "1":
            register_user()
        elif choice == "2":
            user = login()
            if user:
                while True:
                    if user["role"] == "librarian":
                        print("\n1. Dodaj książkę\n2. Lista książek\n3. Raport przeterminowanych\n4. Wyloguj")
                        action = input("Wybierz: ")
                        if action == "1":
                            add_book()
                        elif action == "2":
                            list_books()
                        elif action == "3":
                            overdue_books()
                        elif action == "4":
                            break
                    else:
                        print("\n1. Lista książek\n2. Wypożycz książkę\n3. Zwróć książkę\n4. Wyloguj")
                        action = input("Wybierz: ")
                        if action == "1":
                            list_books()
                        elif action == "2":
                            borrow_book(user["id"])
                        elif action == "3":
                            return_book(user["id"])
                        elif action == "4":
                            break
        elif choice == "3":
            break

if __name__ == "__main__":
    main()

