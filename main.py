import sys
import re
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from db_manager import DatabaseManager
from ui_components import GenericTableTab

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maintenance Record Management System (PyQt6)")
        self.load_settings()

        self.db = DatabaseManager()
        self.check_database_connection()
    
    def load_settings(self):
        """Loads window settings from the external JSON file."""
        settings_path = os.path.join('config', 'settings.json')
        try:
            with open(settings_path, 'r') as file:
                settings_data = json.load(file)
                width = settings_data['window']['width']
                height = settings_data['window']['height']
                self.resize(width, height)
        except Exception as e:
            print(f"Warning: Failed to load settings.json. Using defaults. Error: {e}")
            self.resize(900, 600)
    
    def check_database_connection(self):
        print("Attempting to connect to the database...", flush=True) 
        
        success, message = self.db.connect()
        
        if not success:
            print(f"\nCRITICAL ERROR: Database Connection Failed!", flush=True)
            print(f"Details: {message}\n", flush=True)
            
            QMessageBox.critical(self, "Database Connection Failed", 
                                 f"Could not connect to MySQL server.\nPlease check credentials and ensure the server is running.\n\nError: {message}")
            sys.exit(1) 
        else:
            print("Database connected successfully! Launching UI...", flush=True) 
            self.setup_ui()
    
    def setup_ui(self):
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        schema_path = os.path.join('config', 'schema.json')
        try:
            with open(schema_path, 'r') as file:
                schema_data = json.load(file)

            for table_name, table_details in schema_data.items():
                pk = table_details["primary_key"]
                fields = table_details["fields"]
                
                tab_view = GenericTableTab(self.db, table_name, pk, fields)
                pretty_tab_title = table_name.replace("_", " ").title()
                self.tab_widget.addTab(tab_view, pretty_tab_title)
                
        except Exception as e:
             QMessageBox.critical(self, "Configuration Error", f"Failed to load schema.json:\n{e}")
             sys.exit(1)

if __name__ == "__main__":
    import traceback
    from ui_layer import apply_global_style, MainUIWrapper  # [ADDED] Import the UI layer wrapper and style

    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        apply_global_style(app)      # [ADDED] Apply global stylesheet from ui_layer
        window = MainApp()
        # window.show()              # [REMOVED] MainApp is no longer shown directly; it is embedded in the wrapper
        wrapped_ui = MainUIWrapper(window)   # [ADDED] Wrap MainApp with dashboard + sidebar shell
        wrapped_ui.resize(1200, 800)         # [ADDED] Set size on the wrapper, not the inner window
        wrapped_ui.show()                    # [ADDED] Show the outer wrapper instead
        sys.exit(app.exec())
    except Exception as e:
        print("\n--- FATAL PYQT CRASH ---", flush=True)
        traceback.print_exc() 
        print("------------------------\n", flush=True)