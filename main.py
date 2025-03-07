import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream
from ui.main_window import MainWindow
from data.database import DatabaseManager

# Konfiguracja logowania do pliku i na konsolę
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log", encoding='utf-8'), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

def ensure_directories():
    """Upewnij się, że katalogi potrzebne do działania aplikacji istnieją."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("styles", exist_ok=True)

def load_stylesheet(app):
    """Wczytaj styl QSS, jeśli istnieje."""
    style_path = "styles/style.qss"
    if os.path.exists(style_path):
        file = QFile(style_path)
        if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(file)
            app.setStyleSheet(stream.readAll())
            file.close()
            logger.info("Stylesheet załadowany.")

def main():
    """Główna funkcja uruchamiająca aplikację."""
    ensure_directories()

    app = QApplication(sys.argv)
    app.setApplicationName("ADHD Support App (PyQt6)")

    # Ładowanie stylu QSS (o ile istnieje)
    load_stylesheet(app)

    # Inicjalizacja bazy danych
    db_manager = DatabaseManager()

    # Główne okno
    window = MainWindow(db_manager)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
