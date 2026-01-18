-- Dodawanie autorów
INSERT INTO Authors (name) VALUES ('Andrzej Sapkowski'), ('J.K. Rowling'), ('George R.R. Martin');

-- Dodawanie wydawnictw
INSERT INTO Publishers (name) VALUES ('SuperNowa'), ('Media Rodzina'), ('Zysk i S-ka');

-- Dodawanie książek
INSERT INTO Books (title, publisher_id, year) VALUES 
('Wiedźmin. Ostatnie życzenie', 1, 1993),
('Harry Potter i Kamień Filozoficzny', 2, 1997),
('Gra o Tron', 3, 1996);

-- Łączenie książek z autorami
INSERT INTO Book_Authors (book_id, author_id) VALUES 
(1, 1),
(2, 2),
(3, 3);

-- Dodawanie czytelników
INSERT INTO Patrons (card_number, first_name, last_name, email) VALUES
('C001', 'Jan', 'Kowalski', 'jan.kowalski@example.com'),
('C002', 'Anna', 'Nowak', 'anna.nowak@example.com');

