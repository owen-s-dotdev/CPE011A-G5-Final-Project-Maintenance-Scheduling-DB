import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QAbstractItemView, QHeaderView, QFileDialog,
    QDateEdit, QComboBox # [ADDED] New Native Widgets
)
from PyQt6.QtCore import Qt, QDate # [ADDED] Native Date handlers

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

        # [MODIFIED BLOCK] Dynamic Widget Generation
        for field in self.input_fields:
            col_name = field["name"]
            field_type = field.get("type", "text")
            lbl = QLabel(f"{col_name}:")
            
            # -> Handle Date Calendars
            if field_type == "date":
                entry = QDateEdit()
                entry.setCalendarPopup(True)
                entry.setDisplayFormat("yyyy-MM-dd")
                entry.setDate(QDate.currentDate())
                
            # -> Handle Static Dropdowns (Device Status)
            elif field_type == "enum":
                entry = QComboBox()
                entry.addItems(field.get("options", []))
                
            # -> Handle Smart Foreign Key Dropdowns
            elif field_type == "fk":
                entry = QComboBox()
                    
            # -> Handle Standard Text
            else:
                entry = QLineEdit()
            
            form_layout.addWidget(lbl, row_idx, col_idx)
            form_layout.addWidget(entry, row_idx, col_idx + 1)
            
            self.entries[col_name] = (entry, field_type)

            col_idx += 2
            if col_idx > 3:  
                col_idx = 0
                row_idx += 1

        main_layout.addLayout(form_layout)

        # 2. Action Buttons
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

        self.btn_export = QPushButton("Export to JSON")
        self.btn_export.clicked.connect(self.export_to_json)
        btn_layout.addWidget(self.btn_export)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(self.btn_refresh)

        main_layout.addLayout(btn_layout)

        # 3. Search Bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Type to filter records dynamically...")
        self.search_bar.textChanged.connect(self.filter_table)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_bar)
        
        main_layout.addLayout(search_layout)

        # 4. Data View 
        self.table_widget = QTableWidget()
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) 
        self.table_widget.itemSelectionChanged.connect(self.on_row_select)
        
        main_layout.addWidget(self.table_widget)
    
    def export_to_json(self):
        try:
            records, columns = self.db.fetch_all(self.table_name)
            data_to_export = []
            for row in records:
                row_dict = dict(zip(columns, row))
                for key, value in row_dict.items():
                    if value is not None:
                        row_dict[key] = str(value)
                data_to_export.append(row_dict)

            file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON Backup", f"{self.table_name}_backup.json", "JSON Files (*.json)")
            if file_path:
                with open(file_path, 'w') as json_file:
                    json.dump(data_to_export, json_file, indent=4)
                QMessageBox.information(self, "Success", "Data exported successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{e}")

    def filter_table(self, text):
        search_text = text.lower()
        for row in range(self.table_widget.rowCount()):
            row_visible = False
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break 
            self.table_widget.setRowHidden(row, not row_visible)

    # [MODIFIED BLOCK] Native Validation logic
    def validate_inputs(self):
        columns = []
        values = []
        for col_name, (entry_widget, field_type) in self.entries.items():
            
            # Fetch safely based on widget type
            if field_type == "date":
                val = entry_widget.date().toString("yyyy-MM-dd")
            elif field_type == "enum":
                val = entry_widget.currentText()
            elif field_type == "fk":
                val = entry_widget.currentData()
                if val is None:
                    QMessageBox.warning(self, "Validation Error", f"Please select a valid option for '{col_name}'.")
                    return None, None
                val = str(val)
            else:
                val = entry_widget.text().strip()
                if not val:
                    QMessageBox.warning(self, "Validation Error", f"Field '{col_name}' cannot be empty.")
                    return None, None
                    
            columns.append(col_name)
            values.append(val)
        return columns, values

    def add_record(self):
        columns, values = self.validate_inputs()
        if not columns: return
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
        if not columns: return
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
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this record?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
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
        if hasattr(self, 'search_bar'):
            self.search_bar.clear()
        
        self.refresh_dropdowns()
        
        try:
            records, columns = self.db.fetch_all(self.table_name)
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)
            header = self.table_widget.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            for row_idx, row_data in enumerate(records):
                self.table_widget.insertRow(row_idx)
                for col_idx, cell_data in enumerate(row_data):
                    display_text = str(cell_data) if cell_data is not None else ""
                    item = QTableWidgetItem(display_text)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table_widget.setItem(row_idx, col_idx, item)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to load data for {self.table_name}:\n{e}")

    # [MODIFIED BLOCK] Apply table row data to the corresponding native widgets
    def on_row_select(self):
        selected_items = self.table_widget.selectedItems()
        if not selected_items: return
        row_idx = selected_items[0].row()
        self.clear_form()
        col_count = self.table_widget.columnCount()
        
        for i in range(1, col_count):
            col_name = self.table_widget.horizontalHeaderItem(i).text()
            if col_name in self.entries:
                cell_value = self.table_widget.item(row_idx, i).text()
                entry_widget, field_type = self.entries[col_name]
                
                if field_type == "date":
                    if cell_value:
                        entry_widget.setDate(QDate.fromString(cell_value, "yyyy-MM-dd"))
                elif field_type == "enum":
                    entry_widget.setCurrentText(cell_value)
                elif field_type == "fk":
                    if cell_value.isdigit():
                        idx = entry_widget.findData(int(cell_value))
                        if idx >= 0:
                            entry_widget.setCurrentIndex(idx)
                else:
                    entry_widget.setText(cell_value)

    # [MODIFIED BLOCK] Clear safely based on widget type
    def clear_form(self):
        for entry_widget, field_type in self.entries.values():
            if field_type == "date":
                entry_widget.setDate(QDate.currentDate())
            elif field_type in ["enum", "fk"]:
                if entry_widget.count() > 0:
                    entry_widget.setCurrentIndex(0)
            else:
                entry_widget.clear()

    # For live refreshing of data after updating related tables
    def refresh_dropdowns(self):
        """Re-fetches foreign key data and updates the dropdown menus dynamically."""
        for field in self.input_fields:
            if field.get("type") == "fk":
                col_name = field["name"]
                
                # Safety check in case the widget isn't fully initialized yet
                if col_name not in self.entries:
                    continue
                    
                entry_widget, _ = self.entries[col_name]
                
                fk_table = field["fk_table"]
                fk_id_col = field["fk_id"]
                fk_display_col = field["fk_display"]
                
                # Remember what the user currently has selected
                current_selection = entry_widget.currentData()
                
                entry_widget.clear() # Empty the old list
                
                try:
                    records, columns = self.db.fetch_all(fk_table)
                    id_idx = columns.index(fk_id_col)
                    display_idx = columns.index(fk_display_col)
                    
                    for row in records:
                        entry_widget.addItem(str(row[display_idx]), userData=row[id_idx])
                        
                    # Restore previous selection if it still exists
                    if current_selection is not None:
                        idx = entry_widget.findData(current_selection)
                        if idx >= 0:
                            entry_widget.setCurrentIndex(idx)
                            
                except Exception as e:
                    print(f"Failed to refresh FK data for {col_name}: {e}")