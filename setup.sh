#!/bin/bash

# Skrypt do stworzenia bazy danych i załadowania tabel, danych, triggerów i funkcji
# Wymaga: psql (PostgreSQL)

DB_NAME="library_db"
DB_USER="db_admin"

echo "Tworzenie bazy danych $DB_NAME..."
psql -U $DB_USER -f sql/00_create_db.sql

echo "Tworzenie tabel..."
psql -U $DB_USER -d $DB_NAME -f sql/01_tables.sql

echo "Tworzenie triggerów..."
psql -U $DB_USER -d $DB_NAME -f sql/02_triggers.sql

echo "Tworzenie funkcji i procedur..."
psql -U $DB_USER -d $DB_NAME -f sql/03_functions.sql

echo "Wypełnianie danych..."
psql -U $DB_USER -d $DB_NAME -f sql/04_seed_data.sql

echo "Setup zakończony!"

