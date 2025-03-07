import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Prosta klasa do obsługi bazy SQLite."""

    def __init__(self):
        self.db_path = "data/adhd_app.db"
        self._create_database()

    def _create_database(self):
        """Tworzy tabele, jeśli jeszcze nie istnieją."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabela zadań
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    due_date TEXT,
                    created_at TEXT NOT NULL,
                    modified_at TEXT NOT NULL
                )
            """)

            # Tabela nastrojów
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS moods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    mood TEXT NOT NULL,
                    notes TEXT
                )
            """)

            conn.commit()
            conn.close()
            logger.info("Baza danych zainicjalizowana.")
        except sqlite3.Error as e:
            logger.error(f"Błąd podczas inicjalizacji bazy: {e}")

    # ----- METODY DLA ZADAŃ -----
    def get_tasks(self):
        """Zwraca wszystkie zadania w postaci listy słowników."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tasks ORDER BY due_date IS NULL, due_date ASC, created_at DESC")
            rows = cursor.fetchall()
            tasks = [dict(row) for row in rows]

            conn.close()
            return tasks
        except sqlite3.Error as e:
            logger.error(f"Błąd pobierania zadań: {e}")
            return []

    def add_task(self, title, description, priority, status, due_date=""):
        """Dodaje nowe zadanie do bazy."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO tasks 
                (title, description, priority, status, due_date, created_at, modified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, priority, status, due_date, now, now))

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Błąd dodawania zadania: {e}")

    def update_task(self, task_id, title, description, priority, status, due_date=""):
        """Aktualizuje istniejące zadanie."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, status = ?, due_date = ?, modified_at = ?
                WHERE id = ?
            """, (title, description, priority, status, due_date, now, task_id))

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Błąd aktualizacji zadania: {e}")

    def delete_task(self, task_id):
        """Usuwa zadanie o podanym ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Błąd usuwania zadania: {e}")

    def get_task_by_date(self, date_str):
        """Zwraca zadania dla konkretnej daty (due_date)."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tasks
                WHERE due_date = ?
                ORDER BY priority DESC
            """, (date_str,))
            tasks = [dict(row) for row in cursor.fetchall()]

            conn.close()
            return tasks
        except sqlite3.Error as e:
            logger.error(f"Błąd pobierania zadań po dacie: {e}")
            return []

    # ----- METODY DLA NASTROJÓW -----
    def add_mood(self, date_str, mood, notes=""):
        """Dodaje wpis o nastroju do bazy."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO moods (date, mood, notes)
                VALUES (?, ?, ?)
            """, (date_str, mood, notes))

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Błąd dodawania nastroju: {e}")

    def get_moods(self):
        """Zwraca wszystkie wpisy nastrojów, najnowsze pierwsze."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM moods ORDER BY id DESC")
            rows = cursor.fetchall()
            moods = [dict(row) for row in rows]

            conn.close()
            return moods
        except sqlite3.Error as e:
            logger.error(f"Błąd pobierania nastrojów: {e}")
            return []

    def get_mood_by_date(self, date_str):
        """Pobiera nastroje nagrane na daną datę (powinien być tylko jeden, ale na wszelki wypadek...)."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM moods
                WHERE date = ?
            """, (date_str,))
            rows = cursor.fetchall()
            moods = [dict(row) for row in rows]

            conn.close()
            return moods
        except sqlite3.Error as e:
            logger.error(f"Błąd pobierania nastroju po dacie: {e}")
            return []
