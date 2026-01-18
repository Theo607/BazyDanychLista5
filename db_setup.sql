CREATE DATABASE IF NOT EXISTS biblioteka CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE biblioteka;

-- Kategorie książek
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Autorzy
CREATE TABLE IF NOT EXISTS authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Użytkownicy
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('reader','librarian') NOT NULL
);

-- Książki
CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author_id INT NOT NULL,
    category_id INT,
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    FOREIGN KEY (author_id) REFERENCES authors(author_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Wypożyczenia
CREATE TABLE IF NOT EXISTS borrowings (
    borrowing_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- Rezerwacje książek
CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    reservation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

-- Płatności (opcjonalne)
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Logi akcji użytkowników
CREATE TABLE IF NOT EXISTS logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action TEXT NOT NULL,
    log_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


DELIMITER //

-- Dodawanie książki (autor/kategoria automatycznie dodawane jeśli nie istnieją)
CREATE PROCEDURE add_book_proc(
    IN p_title VARCHAR(255),
    IN p_author VARCHAR(100),
    IN p_category VARCHAR(100),
    IN p_total INT
)
BEGIN
    DECLARE v_author_id INT;
    DECLARE v_category_id INT;

    START TRANSACTION;

    -- Autor
    SELECT author_id INTO v_author_id FROM authors WHERE name = p_author;
    IF v_author_id IS NULL THEN
        INSERT INTO authors (name) VALUES (p_author);
        SET v_author_id = LAST_INSERT_ID();
    END IF;

    -- Kategoria
    SELECT category_id INTO v_category_id FROM categories WHERE name = p_category;
    IF v_category_id IS NULL THEN
        INSERT INTO categories (name) VALUES (p_category);
        SET v_category_id = LAST_INSERT_ID();
    END IF;

    -- Książka
    INSERT INTO books (title, author_id, category_id, total_copies, available_copies)
    VALUES (p_title, v_author_id, v_category_id, p_total, p_total);

    COMMIT;
END;
//

-- Wypożyczenie książki
CREATE PROCEDURE borrow_book_proc(
    IN p_user_id INT,
    IN p_book_id INT
)
BEGIN
    DECLARE v_available INT;

    SELECT available_copies INTO v_available FROM books WHERE book_id = p_book_id;
    IF v_available < 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Brak dostępnych egzemplarzy';
    END IF;

    START TRANSACTION;

    INSERT INTO borrowings (user_id, book_id, due_date) 
    VALUES (p_user_id, p_book_id, DATE_ADD(CURDATE(), INTERVAL 14 DAY));
    UPDATE books SET available_copies = available_copies - 1 WHERE book_id = p_book_id;
    INSERT INTO logs (user_id, action) 
    VALUES (p_user_id, CONCAT('Wypożyczył książkę ', p_book_id));

    COMMIT;
END;
//

-- Zwracanie książki
CREATE PROCEDURE return_book_proc(
    IN p_borrowing_id INT
)
BEGIN
    DECLARE v_book_id INT;

    SELECT book_id INTO v_book_id FROM borrowings WHERE borrowing_id = p_borrowing_id;

    START TRANSACTION;

    UPDATE borrowings SET return_date = CURDATE() WHERE borrowing_id = p_borrowing_id;
    UPDATE books SET available_copies = available_copies + 1 WHERE book_id = v_book_id;
    INSERT INTO logs (user_id, action) 
    SELECT user_id, CONCAT('Zwrócił książkę ', v_book_id) 
    FROM borrowings WHERE borrowing_id = p_borrowing_id;

    COMMIT;
END;
//

-- Pobranie roli użytkownika
CREATE FUNCTION check_user_role(p_user_id INT) RETURNS ENUM('reader','librarian')
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE user_role ENUM('reader','librarian');
    SELECT role INTO user_role FROM users WHERE user_id = p_user_id;
    RETURN user_role;
END;
//

-- Procedura przeterminowanych książek
CREATE PROCEDURE overdue_books_proc()
BEGIN
    SELECT 
        b.borrowing_id,
        u.username,
        bo.title AS book_title,
        a.name AS author_name,
        c.name AS category_name,
        b.due_date
    FROM borrowings b
    JOIN users u ON b.user_id = u.user_id
    JOIN books bo ON b.book_id = bo.book_id
    LEFT JOIN authors a ON bo.author_id = a.author_id
    LEFT JOIN categories c ON bo.category_id = c.category_id
    WHERE b.return_date IS NULL AND b.due_date < CURDATE()
    ORDER BY b.due_date;
END;
//

DELIMITER ;

