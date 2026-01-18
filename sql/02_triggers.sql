-- Trigger po wypożyczeniu
CREATE OR REPLACE FUNCTION update_book_status_on_loan()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE Books SET is_available = FALSE WHERE book_id = NEW.book_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_book_status_on_loan
AFTER INSERT ON Loans
FOR EACH ROW
EXECUTE FUNCTION update_book_status_on_loan();

-- Trigger po zwrocie
CREATE OR REPLACE FUNCTION update_book_status_on_return()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.return_date IS NOT NULL THEN
        UPDATE Books SET is_available = TRUE WHERE book_id = NEW.book_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_book_status_on_return
AFTER UPDATE OF return_date ON Loans
FOR EACH ROW
EXECUTE FUNCTION update_book_status_on_return();

