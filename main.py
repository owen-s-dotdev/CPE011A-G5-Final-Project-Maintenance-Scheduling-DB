import sys
import re
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow,QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from db_manager import DatabaseManager
from ui_components import GenericTableTab

# Main application window

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maintenance Record Management System (PyQt6)")
        # self.resize(900, 600)
        self.load_settings()

        self.db = DatabaseManager()
        self.check_database_connection()
    
    # Method to load the settings.json
    def load_settings(self):
        """Loads window settings from the external JSON file."""
        settings_path = os.path.join('config', 'settings.json')
        try:
            with open(settings_path, 'r') as file:
                settings_data = json.load(file)
                width = settings_data['window']['width']
                height = settings_data['window']['height']
                # Apply JSON settings
                self.resize(width, height)
        except Exception as e:
            print(f"Warning: Failed to load settings.json. Using defaults. Error: {e}")
            self.resize(900, 600) # Default fallback
    
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

            # [MODIFIED] Loop logic to parse JSON structure
            for table_name, table_details in schema_data.items():
                pk = table_details["primary_key"]
                # Convert the JSON array of objects back into a list of tuples
                fields = [(f["name"], f["is_date"]) for f in table_details["fields"]]
                
                tab_view = GenericTableTab(self.db, table_name, pk, fields)
                pretty_tab_title = table_name.replace("_", " ").title()
                self.tab_widget.addTab(tab_view, pretty_tab_title)
                
        except Exception as e:
             QMessageBox.critical(self, "Configuration Error", f"Failed to load schema.json:\n{e}")
             sys.exit(1)

if __name__ == "__main__":
    import traceback 
    
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = MainApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print("\n--- FATAL PYQT CRASH ---", flush=True)
        traceback.print_exc() 
        print("------------------------\n", flush=True)