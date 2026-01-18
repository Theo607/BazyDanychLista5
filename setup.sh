#!/bin/bash
set -e

# -------------------------------
# Tworzenie wirtualnego środowiska Python
# -------------------------------
echo "Tworzenie wirtualnego środowiska Python..."
python -m venv venv

echo "Aktywowanie venv i instalacja pakietów Python..."
source venv/bin/activate
pip install --upgrade pip
pip install mysql-connector-python bcrypt tabulate

# -------------------------------
# Instalacja MariaDB (Arch/Manjaro)
# -------------------------------
echo "Sprawdzanie czy MariaDB jest zainstalowana..."
if ! command -v mysql &> /dev/null
then
    echo "MariaDB nie jest zainstalowana. Instalacja..."
    sudo pacman -Syu --noconfirm mariadb
else
    echo "MariaDB jest już zainstalowana."
fi

# -------------------------------
# Inicjalizacja bazy danych MariaDB
# -------------------------------
DB_DIR="/var/lib/mysql"

if [ ! -d "$DB_DIR/mysql" ]; then
    echo "Inicjalizacja bazy danych MariaDB..."
    sudo mariadb-install-db --user=mysql --basedir=/usr --datadir="$DB_DIR"
fi

# -------------------------------
# Uruchamianie serwisu MariaDB
# -------------------------------
echo "Uruchamianie serwisu MariaDB..."
sudo systemctl enable mariadb
sudo systemctl start mariadb

# -------------------------------
# Tworzenie bazy danych i użytkownika
# -------------------------------
echo "Tworzenie bazy danych i użytkownika..."

sudo mariadb <<EOF
CREATE DATABASE IF NOT EXISTS biblioteka CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'biblioteka_user'@'localhost' IDENTIFIED BY 'biblioteka_pass';
GRANT ALL PRIVILEGES ON biblioteka.* TO 'biblioteka_user'@'localhost';
FLUSH PRIVILEGES;

-- Ładowanie tabel z pliku db_setup.sql
SOURCE $(pwd)/db_setup.sql;
EOF

echo "Baza danych 'biblioteka' została utworzona."

# -------------------------------
# Podsumowanie
# -------------------------------
echo "Setup zakończony!"
echo "Aby uruchomić aplikację, aktywuj środowisko venv:"
echo "  source venv/bin/activate"
echo "i uruchom app.py:"
echo "  python app.py"

