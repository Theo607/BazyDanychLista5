-- Funkcja: wypożyczenia przeterminowane
CREATE OR REPLACE FUNCTION FindOverdueLoans()
RETURNS TABLE(
    loan_id INT,
    patron_name VARCHAR,
    book_title VARCHAR,
    due_date DATE
) AS $$
BEGIN
    RETURN QUERY
    SELECT l.loan_id, p.first_name || ' ' || p.last_name, b.title, l.due_date
    FROM Loans l
    JOIN Patrons p ON l.patron_id = p.patron_id
    JOIN Books b ON l.book_id = b.book_id
    WHERE l.return_date IS NULL AND l.due_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

