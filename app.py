import os
import sys
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
import database
import document_generator

# Configure Logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "system.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

def setup_directories():
    """Ensure all required folders in the directory structure exist."""
    folders = [
        "database",
        "templates/doc",
        "templates/xls",
        "output/docx",
        "output/pdf",
        "assets",
        "backup",
        "logs"
    ]
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
    logging.info("Required directory structure created successfully.")

def main():
    logging.info("Starting SI-DESAKU Desktop Application...")
    
    # 1. Initialize Directories
    setup_directories()
    
    # 2. Initialize Database tables
    try:
        database.init_db()
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize database: {str(e)}")
        sys.exit(1)

    # 3. Bootstrap default templates
    try:
        document_generator.bootstrap_templates()
        logging.info("Template bootstrapping completed.")
    except Exception as e:
        logging.error(f"Failed to bootstrap templates: {str(e)}")

    # 4. Start Qt App
    app = QApplication(sys.argv)
    
    # Set global application font
    app.setStyleSheet("QWidget { font-family: 'Segoe UI', Arial, sans-serif; }")

    window = MainWindow()
    window.show()
    
    logging.info("Main Window displayed. Entering Qt main loop.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
