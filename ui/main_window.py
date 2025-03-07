from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QLabel,
    QTableWidget, QTableWidgetItem, QCalendarWidget, QMessageBox,
    QDialog, QFormLayout, QDialogButtonBox, QScrollArea, QTreeWidget,
    QTreeWidgetItem
)
from PyQt6.QtCore import Qt, QDate
from data.database import DatabaseManager

class MainWindow(QMainWindow):
    """Główne okno aplikacji."""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

        self.setWindowTitle("ADHD Support App (PyQt6) – MVP")
        self.setMinimumSize(800, 600)

        self.init_ui()
        self.refresh_task_list()
        self.refresh_mood_list()

    def init_ui(self):
        """Inicjalizacja interfejsu."""
        # Główny kontener z zakładkami
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Zakładka z zadaniami ---
        self.task_tab = QWidget()
        self.task_layout = QVBoxLayout(self.task_tab)

        # Panel przycisków (Dodaj, Edytuj, Usuń)
        btn_layout = QHBoxLayout()
        self.add_task_btn = QPushButton("Dodaj zadanie")
        self.add_task_btn.clicked.connect(self.show_add_task_dialog)
        self.edit_task_btn = QPushButton("Edytuj zadanie")
        self.edit_task_btn.clicked.connect(self.show_edit_task_dialog)
        self.del_task_btn = QPushButton("Usuń zadanie")
        self.del_task_btn.clicked.connect(self.delete_task)

        btn_layout.addWidget(self.add_task_btn)
        btn_layout.addWidget(self.edit_task_btn)
        btn_layout.addWidget(self.del_task_btn)

        self.task_layout.addLayout(btn_layout)

        # Tabela z zadaniami
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels(["ID", "Tytuł", "Priorytet", "Status", "Termin"])
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_layout.addWidget(self.task_table)

        # Dodaj zakładkę z zadaniami do QTabWidget
        self.tabs.addTab(self.task_tab, "Zadania")

        # --- Zakładka z nastrojem ---
        self.mood_tab = QWidget()
        self.mood_layout = QVBoxLayout(self.mood_tab)

        # Panel przycisków (Dodaj)
        mood_btn_layout = QHBoxLayout()
        self.add_mood_btn = QPushButton("Zapisz nastrój")
        self.add_mood_btn.clicked.connect(self.show_add_mood_dialog)
        mood_btn_layout.addWidget(self.add_mood_btn)

        self.mood_layout.addLayout(mood_btn_layout)

        # Lista (tabela) nastrojów
        self.mood_table = QTableWidget()
        self.mood_table.setColumnCount(3)
        self.mood_table.setHorizontalHeaderLabels(["Data", "Nastrój", "Notatki"])
        self.mood_table.horizontalHeader().setStretchLastSection(True)
        self.mood_layout.addWidget(self.mood_table)

        self.tabs.addTab(self.mood_tab, "Nastrój")

        # --- Zakładka z kalendarzem ---
        self.calendar_tab = QWidget()
        self.calendar_layout = QVBoxLayout(self.calendar_tab)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.on_date_changed)
        self.calendar_layout.addWidget(self.calendar)

        # Wyświetlanie zadań i nastroju dla wybranej daty
        self.date_info_label = QLabel("Wybierz datę w kalendarzu")
        self.calendar_layout.addWidget(self.date_info_label)

        self.date_tasks = QTreeWidget()
        self.date_tasks.setHeaderLabels(["Zadanie", "Priorytet", "Status"])
        self.calendar_layout.addWidget(self.date_tasks)

        self.date_mood_label = QLabel("Nastrój: Brak wpisu")
        self.calendar_layout.addWidget(self.date_mood_label)

        self.tabs.addTab(self.calendar_tab, "Kalendarz")

    # ------------------- TASKS -------------------
    def refresh_task_list(self):
        """Odśwież listę zadań w tabeli."""
        tasks = self.db_manager.get_tasks()
        self.task_table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(str(task["id"])))
            self.task_table.setItem(row, 1, QTableWidgetItem(task["title"]))
            self.task_table.setItem(row, 2, QTableWidgetItem(task["priority"]))
            self.task_table.setItem(row, 3, QTableWidgetItem(task["status"]))
            self.task_table.setItem(row, 4, QTableWidgetItem(task.get("due_date", "")))

    def show_add_task_dialog(self):
        dialog = TaskDialog(self)
        if dialog.exec():
            data = dialog.get_task_data()
            self.db_manager.add_task(
                data["title"],
                data["description"],
                data["priority"],
                data["status"],
                data["due_date"]
            )
            self.refresh_task_list()

    def show_edit_task_dialog(self):
        row = self.task_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz zadanie do edycji.")
            return

        task_id = self.task_table.item(row, 0).text()
        current_task = {
            "id": task_id,
            "title": self.task_table.item(row, 1).text(),
            "priority": self.task_table.item(row, 2).text(),
            "status": self.task_table.item(row, 3).text(),
            "due_date": self.task_table.item(row, 4).text()
        }

        dialog = TaskDialog(self, current_task)
        if dialog.exec():
            data = dialog.get_task_data()
            self.db_manager.update_task(
                task_id,
                data["title"],
                data["description"],
                data["priority"],
                data["status"],
                data["due_date"]
            )
            self.refresh_task_list()

    def delete_task(self):
        row = self.task_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Uwaga", "Wybierz zadanie do usunięcia.")
            return

        task_id = self.task_table.item(row, 0).text()
        confirm = QMessageBox.question(
            self,
            "Potwierdź",
            "Czy na pewno chcesz usunąć to zadanie?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.db_manager.delete_task(task_id)
            self.refresh_task_list()

    # ------------------- MOOD -------------------
    def refresh_mood_list(self):
        """Odśwież listę nastrojów w tabeli."""
        moods = self.db_manager.get_moods()
        self.mood_table.setRowCount(len(moods))

        for row, mood in enumerate(moods):
            self.mood_table.setItem(row, 0, QTableWidgetItem(mood["date"]))
            self.mood_table.setItem(row, 1, QTableWidgetItem(mood["mood"]))
            self.mood_table.setItem(row, 2, QTableWidgetItem(mood.get("notes", "")))

    def show_add_mood_dialog(self):
        dialog = MoodDialog(self)
        if dialog.exec():
            data = dialog.get_mood_data()
            self.db_manager.add_mood(data["date"], data["mood"], data["notes"])
            self.refresh_mood_list()

    # ------------------- CALENDAR -------------------
    def on_date_changed(self):
        """Reakcja na zmianę wybranej daty w kalendarzu."""
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.date_info_label.setText(f"Wybrana data: {selected_date}")

        # Zadania
        tasks = self.db_manager.get_task_by_date(selected_date)
        self.date_tasks.clear()
        for t in tasks:
            item = QTreeWidgetItem([t["title"], t["priority"], t["status"]])
            self.date_tasks.addTopLevelItem(item)

        # Nastrój
        moods = self.db_manager.get_mood_by_date(selected_date)
        if moods:
            mood_text = moods[-1]  # Ostatni wpis
            self.date_mood_label.setText(f"Nastrój: {mood_text['mood']} - {mood_text.get('notes','')}")
        else:
            self.date_mood_label.setText("Nastrój: Brak wpisu")

# ------------------- DIALOGI -------------------

class TaskDialog(QDialog):
    """Dialog do tworzenia/edycji zadania."""

    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.setWindowTitle("Nowe zadanie" if not task else "Edytuj zadanie")
        self.task = task

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.title_edit = QLineEdit()
        form_layout.addRow("Tytuł:", self.title_edit)

        self.description_edit = QTextEdit()
        form_layout.addRow("Opis:", self.description_edit)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])
        form_layout.addRow("Priorytet:", self.priority_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItems(["To Do", "In Progress", "Done"])
        form_layout.addRow("Status:", self.status_combo)

        self.due_date_edit = QLineEdit()  # Prosta wersja, można np. wprowadzić QDateEdit
        form_layout.addRow("Termin (YYYY-MM-DD):", self.due_date_edit)

        layout.addLayout(form_layout)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        layout.addWidget(btn_box)
        self.setLayout(layout)

        # Jeśli edytujemy istniejące zadanie, wypełnij dane
        if self.task:
            self.title_edit.setText(self.task["title"])
            self.priority_combo.setCurrentText(self.task["priority"])
            self.status_combo.setCurrentText(self.task["status"])
            self.due_date_edit.setText(self.task.get("due_date", ""))

    def get_task_data(self):
        return {
            "title": self.title_edit.text(),
            "description": self.description_edit.toPlainText(),
            "priority": self.priority_combo.currentText(),
            "status": self.status_combo.currentText(),
            "due_date": self.due_date_edit.text(),
        }


class MoodDialog(QDialog):
    """Dialog do zapisu nastroju."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zapisz nastrój")

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.date_edit = QLineEdit()
        self.date_edit.setText(QDate.currentDate().toString("yyyy-MM-dd"))
        form_layout.addRow("Data (YYYY-MM-DD):", self.date_edit)

        self.mood_combo = QComboBox()
        self.mood_combo.addItems(["Dobry", "Neutralny", "Zły"])
        form_layout.addRow("Nastrój:", self.mood_combo)

        self.notes_edit = QTextEdit()
        form_layout.addRow("Notatki:", self.notes_edit)

        layout.addLayout(form_layout)

        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        layout.addWidget(btn_box)
        self.setLayout(layout)

    def get_mood_data(self):
        return {
            "date": self.date_edit.text(),
            "mood": self.mood_combo.currentText(),
            "notes": self.notes_edit.toPlainText(),
        }
