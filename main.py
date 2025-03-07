import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream, QIODevice
from data.database import DatabaseManager
from ui.main_window import MainWindow

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
    style_path = "styles/style.qss"
    if os.path.exists(style_path):
        file = QFile(style_path)
        if file.open(QIODevice.OpenModeFlag.ReadOnly | QIODevice.OpenModeFlag.Text):
            stream = QTextStream(file)
            app.setStyleSheet(stream.readAll())
            file.close()

def main():
    ensure_directories()

    app = QApplication(sys.argv)
    app.setApplicationName("ADHD Support App (Advanced)")

    load_stylesheet(app)

    db_manager = DatabaseManager()
    window = MainWindow(db_manager)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()