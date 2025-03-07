# ADHD Support App (PyQt6) – Minimalne MVP

Prosta aplikacja stworzona w Pythonie (PyQt6), pomagająca w zarządzaniu zadaniami i śledzeniu nastroju.  
Wersja **bez przekombinowania** – zawiera tylko kluczowe funkcje:

- Dodawanie / edycja / usuwanie zadań (z priorytetem i statusem)  
- Śledzenie nastroju (data, rodzaj nastroju, notatki)  
- Prosty widok kalendarza (podgląd zadań i nastrojów w wybranym dniu)  
- Baza danych SQLite (dwie tabele: `tasks` i `moods`)

## Wymagania
- Python 3.9+  
- Zainstalowane pakiety z `requirements.txt` (obecnie tylko `PyQt6`).

## Instalacja
1. Sklonuj to repozytorium lub pobierz paczkę ZIP.
2. Wejdź do katalogu `ADHD_Support_App/`.
3. Zainstaluj wymagane paczki:
   ```bash
   pip install -r requirements.txt
