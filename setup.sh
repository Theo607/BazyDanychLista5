#!/bin/bash

pip install psycopg2-binary bcrypt tabulate

# Uruchomienie SQL w PostgreSQL
sudo -i -u postgres psql -f db_setup.sql

echo "Baza danych biblioteka została utworzona."

