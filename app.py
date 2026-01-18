import psycopg2
import bcrypt
from getpass import getpass
from datetime import date, timedelta
from tabulate import tabulate

DB_NAME = "biblioteka"
DB_USER = "postgres"
DB_PASSWORD = "your_postgres_password"
DB_HOST = "localhost"

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)
cur = conn.cursor()

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
    except Exception as e:
        conn.rollback()
        print("Błąd:", e)

def login():
    username = input("Nazwa użytkownika: ")
    password = getpass("Hasło: ")
    cur.execute("SELECT user_id, password_hash, role FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    if user and check_password(password, user[1]):
        print(f"Zalogowano jako {user[2]}")
        return {"id": user[0], "role": user[2]}
    else:
        print("Błędny login lub hasło.")
        return None

# ---------------- CRUD książek ----------------
def add_book():
    title = input("Tytuł: ")
    author = input("Autor: ")
    category = input("Kategoria: ")
    total = int(input("Liczba egzemplarzy: "))
    cur.execute(
        "INSERT INTO books (title, author, category_id, total_copies, available_copies) "
        "VALUES (%s, %s, (SELECT category_id FROM categories WHERE name=%s), %s, %s)",
        (title, author, category, total, total)
    )
    conn.commit()
    print("Książka dodana.")

def list_books():
    cur.execute("SELECT book_id, title, author, category_id, available_copies FROM books ORDER BY title")
    rows = cur.fetchall()
    print(tabulate(rows, headers=["ID", "Tytuł", "Autor", "Kategoria_ID", "Dostępne"], tablefmt="grid"))

# ---------------- Wypożyczenia ----------------
def borrow_book(user_id):
    list_books()
    book_id = int(input("ID książki do wypożyczenia: "))
    due = date.today() + timedelta(days=14)
    try:
        cur.execute(
            "INSERT INTO borrowings (user_id, book_id, due_date) VALUES (%s, %s, %s)",
            (user_id, book_id, due)
        )
        cur.execute("INSERT INTO logs (user_id, action) VALUES (%s, %s)", (user_id, f"Wypożyczył książkę {book_id}"))
        conn.commit()
        print("Wypożyczono książkę.")
    except Exception as e:
        conn.rollback()
        print("Błąd:", e)

def return_book(user_id):
    cur.execute("SELECT borrowing_id, book_id, due_date FROM borrowings WHERE user_id=%s AND return_date IS NULL", (user_id,))
    borrows = cur.fetchall()
    print(tabulate(borrows, headers=["ID Wypożyczenia", "ID Książki", "Termin"], tablefmt="grid"))
    borrow_id = int(input("ID wypożyczenia do zwrotu: "))
    cur.execute("UPDATE borrowings SET return_date=CURRENT_DATE WHERE borrowing_id=%s", (borrow_id,))
    cur.execute("INSERT INTO logs (user_id, action) VALUES (%s, %s)", (user_id, f"Zwrócił książkę {borrow_id}"))
    conn.commit()
    print("Książka zwrócona.")

# ---------------- Raporty ----------------
def overdue_books():
    cur.execute(
        "SELECT b.borrowing_id, u.username, bo.title, b.due_date FROM borrowings b "
        "JOIN users u ON b.user_id=u.user_id "
        "JOIN books bo ON b.book_id=bo.book_id "
        "WHERE b.return_date IS NULL AND b.due_date < CURRENT_DATE"
    )
    rows = cur.fetchall()
    print(tabulate(rows, headers=["ID Wypożyczenia", "Czytelnik", "Książka", "Termin"], tablefmt="grid"))

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

