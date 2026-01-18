-- Utworzenie bazy
CREATE DATABASE biblioteka;
\c biblioteka;

-- 1. Użytkownicy (czytelnicy i bibliotekarze)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('reader', 'librarian'))
);

-- 2. Książki
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255),
    category_id INT REFERENCES categories(category_id),
    total_copies INT NOT NULL CHECK (total_copies >= 0),
    available_copies INT NOT NULL CHECK (available_copies >= 0)
);

-- 3. Kategorie książek
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- 4. Wypożyczenia
CREATE TABLE borrowings (
    borrowing_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    book_id INT REFERENCES books(book_id) ON DELETE CASCADE,
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE
);

-- 5. Autorzy (dla przyszłych rozszerzeń)
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- 6. Rezerwacje książek
CREATE TABLE reservations (
    reservation_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    book_id INT REFERENCES books(book_id) ON DELETE CASCADE,
    reserve_date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- 7. Płatności (opcjonalnie np. kary za przeterminowane książki)
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    amount NUMERIC(6,2) NOT NULL,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    description TEXT
);

-- 8. Logi akcji użytkowników
CREATE TABLE logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    action_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger do aktualizacji dostępnych książek przy wypożyczeniu/zwrocie
CREATE OR REPLACE FUNCTION update_available_copies() RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE books SET available_copies = available_copies - 1 WHERE book_id = NEW.book_id;
    ELSIF (TG_OP = 'UPDATE' AND NEW.return_date IS NOT NULL) THEN
        UPDATE books SET available_copies = available_copies + 1 WHERE book_id = NEW.book_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_copies
AFTER INSERT OR UPDATE ON borrowings
FOR EACH ROW EXECUTE FUNCTION update_available_copies();

