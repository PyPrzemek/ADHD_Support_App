from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox, QComboBox, QTextEdit,
    QLabel, QSpinBox, QPushButton
)
from PyQt6.QtCore import QDate
from ai.emotion_analyzer import EmotionAnalyzer

class AdvancedMoodDialog(QDialog):
    """Rozszerzony dialog do zapisywania nastroju z obsługą energy/focus i placeholdera analizy emocji."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.emotion_analyzer = EmotionAnalyzer()

        self.setWindowTitle("Zapisz nastrój (Extended)")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Data (YYYY-MM-DD)
        self.date_label = QLabel(QDate.currentDate().toString("yyyy-MM-dd"))
        form_layout.addRow("Data:", self.date_label)

        # Emocja (ręczna)
        self.mood_combo = QComboBox()
        self.mood_combo.addItems(["Dobry", "Neutralny", "Zły", "Stres", "Euforia"])
        form_layout.addRow("Nastrój:", self.mood_combo)

        # Poziom energii
        self.energy_spin = QSpinBox()
        self.energy_spin.setRange(1, 10)
        self.energy_spin.setValue(5)
        form_layout.addRow("Poziom energii:", self.energy_spin)

        # Poziom skupienia
        self.focus_spin = QSpinBox()
        self.focus_spin.setRange(1, 10)
        self.focus_spin.setValue(5)
        form_layout.addRow("Poziom skupienia:", self.focus_spin)

        # Notatki
        self.notes_edit = QTextEdit()
        form_layout.addRow("Notatki:", self.notes_edit)

        layout.addLayout(form_layout)

        # Sekcja analizy audio/video (placeholder)
        analyze_btn = QPushButton("Zrób szybką analizę wideo/audio (PLACEHOLDER)")
        analyze_btn.clicked.connect(self.do_emotion_analysis)
        layout.addWidget(analyze_btn)

        # OK/Cancel
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

        self.setLayout(layout)

    def do_emotion_analysis(self):
        # Tutaj placeholder; w realnej aplikacji – przechwycenie klatki/kilka sekund audio,
        # wywołanie self.emotion_analyzer.analyze_audio(...) i interpretacja wyniku.
        # Możesz np. ustawić mood_combo na bazie wyniku:
        emotion_result = self.emotion_analyzer.analyze_audio(None)
        self.mood_combo.setCurrentText(emotion_result)  # np. "Neutral", "Angry", "Happy"

    def get_mood_data(self):
        return {
            "date": self.date_label.text(),
            "mood": self.mood_combo.currentText(),
            "notes": self.notes_edit.toPlainText(),
            "energy_level": self.energy_spin.value(),
            "focus_level": self.focus_spin.value()
        }
