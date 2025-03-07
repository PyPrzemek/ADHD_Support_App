from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import Qt
from ai.pomodoro_ai import PomodoroAI

class AdvancedPomodoroWidget(QWidget):
    """Widget do inteligentnego Pomodoro – wybór zadania, start sesji."""

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.pomodoro_ai = PomodoroAI()
        self.current_session_id = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Wybór zadania z listy
        task_layout = QHBoxLayout()
        task_layout.addWidget(QLabel("Zadanie:"))
        self.task_combo = QComboBox()
        self.refresh_task_list()
        task_layout.addWidget(self.task_combo)
        layout.addLayout(task_layout)

        # Rekomendowana długość
        self.recommended_label = QLabel("Rekomendowana długość: ?? min")
        layout.addWidget(self.recommended_label)

        # Start/Stop
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Rozpocznij sesję")
        self.start_btn.clicked.connect(self.start_pomodoro)
        self.end_btn = QPushButton("Zakończ sesję")
        self.end_btn.clicked.connect(self.end_pomodoro)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.end_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.setMinimumHeight(200)

    def refresh_task_list(self):
        self.task_combo.clear()
        tasks = self.db_manager.get_tasks()
        for t in tasks:
            # W combo wyświetlamy np. "ID - Tytuł"
            self.task_combo.addItem(f"{t['id']} - {t['title']}")

    def get_current_mood_entry(self):
        """
        W prawdziwej sytuacji pobrałbyś np.
        ostatni wpis nastroju i stąd brał poziom energii/focusu.
        Tu – placeholder.
        """
        # Weźmy ostatni mood z bazy (jeśli istnieje)
        moods = self.db_manager.get_moods()
        if moods:
            m = moods[0]  # Najnowszy
            return {
                "mood": m["mood"],
                "energy_level": m.get("energy_level", 5),
                "focus_level": m.get("focus_level", 5),
            }
        else:
            return {"mood": "Neutralny", "energy_level": 5, "focus_level": 5}

    def start_pomodoro(self):
        """Logika startu sesji z automatycznym dobraniem czasu."""
        if self.current_session_id:
            QMessageBox.warning(self, "Uwaga", "Sesja pomodoro już trwa!")
            return

        # Odczytaj ID zadania
        selected_text = self.task_combo.currentText()
        if not selected_text:
            QMessageBox.warning(self, "Błąd", "Brak wybranego zadania.")
            return

        task_id = selected_text.split(" - ")[0]

        # AI - ustalenie rekomendowanej długości
        mood_entry = self.get_current_mood_entry()
        # Wczytaj poprzednie pomodoro sesje
        # (Przykład – pobierasz z bazy i ewentualnie filtrujesz po zadaniu)
        # Tu uproszczone: bierzemy wszystko
        # W realu -> implementuj w DB
        last_sessions = []

        recommended_minutes = self.pomodoro_ai.recommend_session_length(mood_entry, last_sessions)
        self.recommended_label.setText(f"Rekomendowana długość: {recommended_minutes} min")

        # Zapisz do bazy start nowej sesji
        session_id = self.db_manager.add_pomodoro_session(task_id, recommended_minutes)
        if session_id:
            self.current_session_id = session_id
            QMessageBox.information(self, "Pomodoro", f"Rozpoczęto sesję na {recommended_minutes} min.")
        else:
            QMessageBox.critical(self, "Błąd", "Nie udało się rozpocząć sesji.")

    def end_pomodoro(self):
        """Kończy bieżącą sesję."""
        if not self.current_session_id:
            QMessageBox.warning(self, "Uwaga", "Nie ma aktywnej sesji do zakończenia.")
            return

        success = self.db_manager.end_pomodoro_session(self.current_session_id)
        if success:
            QMessageBox.information(self, "Pomodoro", "Sesja zakończona.")
        else:
            QMessageBox.critical(self, "Błąd", "Nie udało się zakończyć sesji.")

        self.current_session_id = None
