import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Rozszerzona wersja bazy SQLite z polami pod AI i pomodoro."""

    def __init__(self):
        self.db_path = "data/adhd_app.db"
        self._create_database()

    def _create_database(self):
        """Tworzy tabele, jeśli jeszcze nie istnieją."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabela zadań - dodajmy kilka pól
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    due_date TEXT,
                    created_at TEXT NOT NULL,
                    modified_at TEXT NOT NULL,
                    focus_score REAL,         -- ocena 'skupienia' - placeholder
                    recommended_session INTEGER -- rekomendowana długość sesji
                )
            """)

            # Tabela nastrojów - poszerzona
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS moods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    mood TEXT NOT NULL,
                    notes TEXT,
                    energy_level INTEGER, 
                    focus_level INTEGER
                )
            """)

            # Tabela pomodoro_sessions - do śledzenia sesji
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    start_time TEXT,
                    end_time TEXT,
                    planned_duration INTEGER,
                    actual_duration INTEGER,
                    completed INTEGER,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)

            conn.commit()
            conn.close()
            logger.info("Baza danych zainicjalizowana (rozszerzona).")
        except sqlite3.Error as e:
            logger.error(f"Błąd podczas inicjalizacji bazy: {e}")

    # ----- Zadania -----
    def get_tasks(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tasks 
                ORDER BY due_date IS NULL, due_date ASC, created_at DESC
            """)
            rows = cursor.fetchall()
            tasks = [dict(row) for row in rows]

            conn.close()
            return tasks
        except sqlite3.Error as e:
            logger.error(f"Błąd pobierania zadań: {e}")
            return []

    def add_task(self, title, description, priority, status, due_date="", focus_score=0.0):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO tasks 
                (title, description, priority, status, due_date, created_at, modified_at, focus_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, priority, status, due_date, now, now, focus_score))

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Błąd dodawania zadania: {e}")

    def update_task(self, task_id, title, description, priority, status, due_date="", focus_score=0.0):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, status = ?, due_date = ?, 
                    modified_at = ?, focus_score = ?
                WHERE id = ?
            """, (title, description, priority, status, due_date, now, focus_score, task_id))

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Błąd aktualizacji zadania: {e}")

    def delete_task(self, task_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Błąd usuwania zadania: {e}")

    def get_task_by_date(self, date_str):
        """Zwraca zadania z due_date = date_str."""
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

    # ----- Moods -----
    def add_mood(self, date_str, mood, notes="", energy_level=5, focus_level=5):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO moods (date, mood, notes, energy_level, focus_level)
                VALUES (?, ?, ?, ?, ?)
            """, (date_str, mood, notes, energy_level, focus_level))

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            logger.error(f"Błąd dodawania nastroju: {e}")

    def get_moods(self):
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
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM moods WHERE date = ?", (date_str,))
            rows = cursor.fetchall()
            moods = [dict(row) for row in rows]

            conn.close()
            return moods
        except sqlite3.Error as e:
            logger.error(f"Błąd pobierania nastroju po dacie: {e}")
            return []

    # ----- Pomodoro Sessions -----
    def add_pomodoro_session(self, task_id, planned_duration):
        """Start nową sesję pomodoro (bez end_time, bo jeszcze nie wiemy)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("""
                INSERT INTO pomodoro_sessions 
                (task_id, start_time, planned_duration, completed) 
                VALUES (?, ?, ?, 0)
            """, (task_id, start_time, planned_duration))

            conn.commit()
            session_id = cursor.lastrowid
            conn.close()
            return session_id
        except sqlite3.Error as e:
            logger.error(f"Błąd dodawania pomodoro sesji: {e}")
            return None

    def end_pomodoro_session(self, session_id):
        """Zakończ trwającą sesję pomodoro."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            end_time = datetime.now()
            end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

            # Pobierz poprzedni start
            cursor.execute("""
                SELECT start_time FROM pomodoro_sessions WHERE id = ?
            """, (session_id,))
            row = cursor.fetchone()

            if not row:
                conn.close()
                return False

            start_dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            duration = int((end_time - start_dt).total_seconds() // 60)

            cursor.execute("""
                UPDATE pomodoro_sessions
                SET end_time = ?, actual_duration = ?, completed = 1
                WHERE id = ?
            """, (end_str, duration, session_id))

            conn.commit()
            conn.close()
            return True

        except sqlite3.Error as e:
            logger.error(f"Błąd kończenia sesji pomodoro: {e}")
            return False
