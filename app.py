import mysql.connector
import bcrypt
from getpass import getpass
from datetime import date, timedelta
from tabulate import tabulate

# ---------------- Konfiguracja bazy ----------------
DB_NAME = "biblioteka"
DB_USER = "biblioteka_user"  # zgodnie z setup.sh
DB_PASSWORD = "biblioteka_pass"
DB_HOST = "localhost"

# Połączenie z bazą
conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
cur = conn.cursor()
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
    cur.execute("SELECT user_id, password_hash, role FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    if not row:
        print("Błędny login lub hasło.")
        return None
    user_id, password_hash, role = row
    if check_password(password, password_hash):
        print(f"Zalogowano jako {role}")
        return {"id": user_id, "role": role}
    else:
        print("Błędny login lub hasło.")
        return None

# ---------------- CRUD książek ----------------
def add_book():
    title = input("Tytuł: ")
    author_name = input("Autor: ")
    category_name = input("Kategoria: ")
    total = int(input("Liczba egzemplarzy: "))

    # Dodaj autora jeśli nie istnieje
    cur.execute("SELECT author_id FROM authors WHERE name=%s", (author_name,))
    author = cur.fetchone()
    if author:
        author_id = author[0]
    else:
        cur.execute("INSERT INTO authors (name) VALUES (%s)", (author_name,))
        conn.commit()
        author_id = cur.lastrowid

    # Dodaj kategorię jeśli nie istnieje
    cur.execute("SELECT category_id FROM categories WHERE name=%s", (category_name,))
    category = cur.fetchone()
    if category:
        category_id = category[0]
    else:
        cur.execute("INSERT INTO categories (name) VALUES (%s)", (category_name,))
        conn.commit()
        category_id = cur.lastrowid

    # Dodaj książkę
    cur.execute(
        "INSERT INTO books (title, author_id, category_id, total_copies, available_copies) "
        "VALUES (%s, %s, %s, %s, %s)",
        (title, author_id, category_id, total, total)
    )
    conn.commit()
    print("Książka dodana.")

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
    print(tabulate(rows, headers=["ID", "Tytuł", "Autor", "Kategoria", "Dostępne"], tablefmt="grid"))

# ---------------- Wypożyczenia ----------------
def borrow_book(user_id):
    list_books()
    book_id = int(input("ID książki do wypożyczenia: "))

    # Sprawdzenie dostępności
    cur.execute("SELECT available_copies FROM books WHERE book_id=%s", (book_id,))
    row = cur.fetchone()
    if not row:
        print("Nieprawidłowe ID książki.")
        return
    available = row[0]
    if available < 1:
        print("Brak dostępnych egzemplarzy.")
        return

    due = date.today() + timedelta(days=14)
    try:
        cur.execute(
            "INSERT INTO borrowings (user_id, book_id, due_date) VALUES (%s, %s, %s)",
            (user_id, book_id, due)
        )
        cur.execute(
            "UPDATE books SET available_copies = available_copies - 1 WHERE book_id=%s",
            (book_id,)
        )
        cur.execute(
            "INSERT INTO logs (user_id, action) VALUES (%s, %s)",
            (user_id, f"Wypożyczył książkę {book_id}")
        )
        conn.commit()
        print("Wypożyczono książkę.")
    except mysql.connector.Error as e:
        conn.rollback()
        print("Błąd:", e)

def return_book(user_id):
    cur.execute("""
        SELECT borrowing_id, book_id, due_date FROM borrowings 
        WHERE user_id=%s AND return_date IS NULL
    """, (user_id,))
    borrows = cur.fetchall()
    if not borrows:
        print("Brak aktywnych wypożyczeń.")
        return
    print(tabulate(borrows, headers=["ID Wypożyczenia", "ID Książki", "Termin"], tablefmt="grid"))
    borrow_id = int(input("ID wypożyczenia do zwrotu: "))

    # Pobranie book_id
    cur.execute("SELECT book_id FROM borrowings WHERE borrowing_id=%s", (borrow_id,))
    row = cur.fetchone()
    if not row:
        print("Nieprawidłowe ID wypożyczenia.")
        return
    book_id = row[0]

    cur.execute("UPDATE borrowings SET return_date=CURDATE() WHERE borrowing_id=%s", (borrow_id,))
    cur.execute(
        "UPDATE books SET available_copies = available_copies + 1 WHERE book_id=%s",
        (book_id,)
    )
    cur.execute(
        "INSERT INTO logs (user_id, action) VALUES (%s, %s)",
        (user_id, f"Zwrócił książkę {book_id}")
    )
    conn.commit()
    print("Książka zwrócona.")

# ---------------- Raporty ----------------
def overdue_books():
    cur.execute("""
        SELECT b.borrowing_id, u.username, bo.title, a.name AS author, c.name AS category, b.due_date
        FROM borrowings b
        JOIN users u ON b.user_id = u.user_id
        JOIN books bo ON b.book_id = bo.book_id
        LEFT JOIN authors a ON bo.author_id = a.author_id
        LEFT JOIN categories c ON bo.category_id = c.category_id
        WHERE b.return_date IS NULL AND b.due_date < CURDATE()
    """)
    rows = cur.fetchall()
    if not rows:
        print("Brak przeterminowanych wypożyczeń.")
        return
    print(tabulate(rows, headers=["ID Wypożyczenia", "Czytelnik", "Tytuł", "Autor", "Kategoria", "Termin"], tablefmt="grid"))

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

