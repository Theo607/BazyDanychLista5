-- Tworzenie bazy danych
CREATE DATABASE library_db;

-- Tworzenie ról
CREATE ROLE db_admin WITH LOGIN PASSWORD 'adminpass';
CREATE ROLE librarian WITH LOGIN PASSWORD 'libpass';
GRANT ALL PRIVILEGES ON DATABASE library_db TO db_admin;

