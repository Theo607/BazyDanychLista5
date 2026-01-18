# PROJEKT BIBLIOTEKA

## Cel Projektu
Celem projektu jest stworzenie prostego systemu do zarządzania biblioteką.  
Aplikacja pozwala na:
- Ewidencjonowanie książek
- Zarządzanie czytelnikami
- Rejestrowanie wypożyczeń i zwrotów książek
- Wyszukiwanie książek i czytelników
- Sprawdzanie historii wypożyczeń i przeterminowanych pozycji

---

## Instalacja PostgreSQL na Linuxie

### Ubuntu / Debian
- Zaktualizuj pakiety:
```bash
sudo apt update
sudo apt upgrade -y
```
- Zainstaluj PostgreSQL wraz z dodatkami:
```bash
sudo apt install postgresql postgresql-contrib -y
```
- Sprawdź status serwera:
```bash
sudo systemctl status postgresql
```
- Przełącz się na użytkownika PostgreSQL i uruchom psql:
```bash
sudo -i -u postgres
psql
```

### Archlinux
- Zainstaluj PostgreSQL:
```bash
sudo pacman -Syu postgresql
```
- Zainicjuj bazę danych:
```bash
sudo -iu postgres initdb --locale $LANG -E UTF8 -D /var/lib/postgres/data
```
- Włącz i uruchom serwis:
```bash
sudo systemctl enable postgresql
sudo systemctl start postgresql
```
- Wejdź do psql jako użytkownik postgres:
```bash
sudo -iu postgres
psql
```
