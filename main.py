import sys
import re
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QMessageBox, QAbstractItemView, QHeaderView
)
from PyQt6.QtCore import Qt
from db_manager import DatabaseManager

class GenericTableTab(QWidget):
    """A reusable UI component for managing CRUD operations on any database table."""
    def __init__(self, db_manager, table_name, pk_column, input_fields):
        super().__init__()
        self.db = db_manager
        self.table_name = table_name
        self.pk_column = pk_column
        self.input_fields = input_fields 
        self.entries = {}

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # 1. Data Entry Form (Grid Layout)
        form_layout = QGridLayout()
        row_idx = 0
        col_idx = 0

        for col_name, is_date in self.input_fields:
            lbl = QLabel(f"{col_name}:")
            entry = QLineEdit()
            if is_date:
                entry.setPlaceholderText("YYYY-MM-DD")
            
            form_layout.addWidget(lbl, row_idx, col_idx)
            form_layout.addWidget(entry, row_idx, col_idx + 1)
            
            self.entries[col_name] = (entry, is_date)

            col_idx += 2
            if col_idx > 3:  
                col_idx = 0
                row_idx += 1

        main_layout.addLayout(form_layout)

        # 2. Action Buttons (Horizontal Layout)
        btn_layout = QHBoxLayout()
        
        self.btn_add = QPushButton("Add Record")
        self.btn_add.clicked.connect(self.add_record)
        btn_layout.addWidget(self.btn_add)

        self.btn_update = QPushButton("Update Selected")
        self.btn_update.clicked.connect(self.update_record)
        btn_layout.addWidget(self.btn_update)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.setStyleSheet("background-color: darkred; color: white;")
        self.btn_delete.clicked.connect(self.delete_record)
        btn_layout.addWidget(self.btn_delete)

        btn_layout.addStretch() 

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(self.btn_refresh)

        main_layout.addLayout(btn_layout)

        # 3. Search Bar (Horizontal Layout)
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type to filter records dynamically...")
        self.search_bar.textChanged.connect(self.filter_table)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)
        
        main_layout.addLayout(search_layout)

        # 4. Data View (QTableWidget)
        self.table_widget = QTableWidget()
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        self.table_widget.itemSelectionChanged.connect(self.on_row_select)
        
        # FIX: Removed the stretch code from here so it doesn't crash on an empty table!
        main_layout.addWidget(self.table_widget)
    
    def filter_table(self, text):
        """Dynamically filters the table rows based on the search query."""
        search_text = text.lower()
        
        # Iterate through every row in the table
        for row in range(self.table_widget.rowCount()):
            row_visible = False
            
            # Check every column in the current row
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break # Stop checking columns if a match is found
            
            # Hide the row if the text was not found in any column
            self.table_widget.setRowHidden(row, not row_visible)

    def validate_inputs(self):
        columns = []
        values = []
        
        for col_name, (entry_widget, is_date) in self.entries.items():
            val = entry_widget.text().strip()
            
            if not val:
                QMessageBox.warning(self, "Validation Error", f"Field '{col_name}' cannot be empty.")
                return None, None
            
            if is_date:
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
                    QMessageBox.warning(self, "Validation Error", f"Date in '{col_name}' must be YYYY-MM-DD.")
                    return None, None
                try:
                    datetime.strptime(val, "%Y-%m-%d")
                except ValueError:
                    QMessageBox.warning(self, "Validation Error", f"Invalid date provided in '{col_name}'.")
                    return None, None

            columns.append(col_name)
            values.append(val)
            
        return columns, values

    def add_record(self):
        columns, values = self.validate_inputs()
        if not columns:
            return

        try:
            self.db.insert_record(self.table_name, columns, values)
            QMessageBox.information(self, "Success", "Record added successfully.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add record:\n{e}")

    def update_record(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a record from the table to update.")
            return

        row_idx = selected_items[0].row()
        pk_val = self.table_widget.item(row_idx, 0).text()
        
        columns, values = self.validate_inputs()
        if not columns:
            return

        try:
            self.db.update_record(self.table_name, self.pk_column, pk_val, columns, values)
            QMessageBox.information(self, "Success", "Record updated successfully.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update record:\n{e}")

    def delete_record(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Error", "Please select a record from the table to delete.")
            return

        row_idx = selected_items[0].row()
        pk_val = self.table_widget.item(row_idx, 0).text()
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                     "Are you sure you want to delete this record?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_record(self.table_name, self.pk_column, pk_val)
                QMessageBox.information(self, "Success", "Record deleted successfully.")
                self.clear_form()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete record:\n{e}")

    def load_data(self):
        self.table_widget.setRowCount(0) 
        
        # Clear the search bar when data reloads
        if hasattr(self, 'search_bar'):
            self.search_bar.clear()

        try:
            records, columns = self.db.fetch_all(self.table_name)
            
            # Set up columns first
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)

            # FIX: Only apply stretch AFTER the columns actually exist
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

            # Insert data
            for row_idx, row_data in enumerate(records):
                self.table_widget.insertRow(row_idx)
                for col_idx, cell_data in enumerate(row_data):
                    display_text = str(cell_data) if cell_data is not None else ""
                    item = QTableWidgetItem(display_text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table_widget.setItem(row_idx, col_idx, item)

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load data for {self.table_name}:\n{e}")

    def on_row_select(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return
            
        row_idx = selected_items[0].row()
        self.clear_form()
        
        col_count = self.table_widget.columnCount()
        for i in range(1, col_count):
            col_name = self.table_widget.horizontalHeaderItem(i).text()
            if col_name in self.entries:
                cell_value = self.table_widget.item(row_idx, i).text()
                entry_widget = self.entries[col_name][0]
                entry_widget.setText(cell_value)

    def clear_form(self):
        for entry_widget, _ in self.entries.values():
            entry_widget.clear()

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maintenance Record Management System (PyQt6)")
        self.resize(900, 600)

        self.db = DatabaseManager()
        self.check_database_connection()

    def check_database_connection(self):
        # FIX: Added flush=True so Python doesn't hide the text if the UI crashes
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

        # MODIFIED BLOCK: The schemas dictionary has been completely 
        # rewritten to align with the new MySQL Database standards.

        schemas = {
            "departments": ("department_id", [("department_name", False), ("department_location", False)]),
            "technicians": ("technician_id", [("first_name", False), ("last_name", False), ("contact_number", False), ("email", False)]),
            "device_types": ("device_type_id", [("device_type_name", False), ("department_id", False)]),
            "maintenance_records": ("maintenance_record_id", [("technician_id", False), ("completion_date", True), ("maintenance_notes", False)]),
            "devices": ("device_id", [("maintenance_record_id", False), ("device_name", False), ("device_type_id", False), ("serial_number", False), ("purchase_date", True), ("device_status", False)])
        }

        for table, (pk, fields) in schemas.items():
            tab_view = GenericTableTab(self.db, table, pk, fields)
            
            # ADDED: Logic to prettify the tab titles so the UI doesn't look like raw SQL.
            # E.g., 'device_types' becomes 'Device Types' in the UI.
            pretty_tab_title = table.replace("_", " ").title()
            self.tab_widget.addTab(tab_view, pretty_tab_title)

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