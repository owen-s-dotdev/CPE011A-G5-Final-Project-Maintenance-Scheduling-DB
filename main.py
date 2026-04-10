import customtkinter as ctk
from tkinter import ttk, messagebox
import re
from datetime import datetime
from db_manager import DatabaseManager

# Initialize CustomTkinter appearance
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GenericTableTab(ctk.CTkFrame):
    """A reusable UI component for managing CRUD operations on any database table."""
    def __init__(self, master, db_manager, table_name, pk_column, input_fields):
        super().__init__(master)
        self.db = db_manager
        self.table_name = table_name
        self.pk_column = pk_column
        self.input_fields = input_fields # List of tuples: (Column Name, is_date)
        self.entries = {}

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Top Frame: Data Entry Form
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=10, pady=10)

        row_idx = 0
        col_idx = 0
        for col_name, is_date in self.input_fields:
            lbl = ctk.CTkLabel(self.form_frame, text=f"{col_name}:")
            lbl.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="e")
            
            placeholder = "YYYY-MM-DD" if is_date else ""
            entry = ctk.CTkEntry(self.form_frame, placeholder_text=placeholder)
            entry.grid(row=row_idx, column=col_idx+1, padx=5, pady=5, sticky="w")
            self.entries[col_name] = (entry, is_date)

            col_idx += 2
            if col_idx > 3: # Break to new line after 2 columns
                col_idx = 0
                row_idx += 1

        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_add = ctk.CTkButton(self.btn_frame, text="Add Record", command=self.add_record)
        self.btn_add.pack(side="left", padx=5)

        self.btn_update = ctk.CTkButton(self.btn_frame, text="Update Selected", command=self.update_record)
        self.btn_update.pack(side="left", padx=5)

        self.btn_delete = ctk.CTkButton(self.btn_frame, text="Delete Selected", command=self.delete_record, fg_color="darkred")
        self.btn_delete.pack(side="left", padx=5)

        self.btn_refresh = ctk.CTkButton(self.btn_frame, text="Refresh", command=self.load_data)
        self.btn_refresh.pack(side="right", padx=5)

        # Data View: Treeview
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbars for Treeview
        tree_scroll_y = ttk.Scrollbar(self.tree_frame)
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(self.tree_frame, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        self.tree.pack(fill="both", expand=True)
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Bind row selection to fill form
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def validate_inputs(self):
        """Validates that fields are not empty and dates match YYYY-MM-DD format."""
        columns = []
        values = []
        
        for col_name, (entry_widget, is_date) in self.entries.items():
            val = entry_widget.get().strip()
            
            # Check empty
            if not val:
                messagebox.showerror("Validation Error", f"Field '{col_name}' cannot be empty.")
                return None, None
            
            # Check date format if applicable
            if is_date:
                if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
                    messagebox.showerror("Validation Error", f"Date in '{col_name}' must be YYYY-MM-DD.")
                    return None, None
                try:
                    datetime.strptime(val, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror("Validation Error", f"Invalid date provided in '{col_name}'.")
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
            messagebox.showinfo("Success", "Record added successfully.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add record:\n{e}")

    def update_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record from the table to update.")
            return

        pk_val = self.tree.item(selected[0], "values")[0]
        columns, values = self.validate_inputs()
        if not columns:
            return

        try:
            self.db.update_record(self.table_name, self.pk_column, pk_val, columns, values)
            messagebox.showinfo("Success", "Record updated successfully.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update record:\n{e}")

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record from the table to delete.")
            return

        pk_val = self.tree.item(selected[0], "values")[0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
        
        if confirm:
            try:
                self.db.delete_record(self.table_name, self.pk_column, pk_val)
                messagebox.showinfo("Success", "Record deleted successfully.")
                self.clear_form()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to delete record:\n{e}")

    def load_data(self):
        """Fetches data from MySQL and populates the Treeview."""
        # Clear current data
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            records, columns = self.db.fetch_all(self.table_name)
            
            # Configure columns
            self.tree["columns"] = columns
            self.tree["show"] = "headings"
            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor="center")

            # Insert data
            for row in records:
                self.tree.insert("", "end", values=row)

        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load data for {self.table_name}:\n{e}")

    def on_row_select(self, event):
        """Populates the input form when a row is clicked."""
        selected = self.tree.selection()
        if not selected:
            return
            
        values = self.tree.item(selected[0], "values")
        columns = self.tree["columns"]
        
        self.clear_form()
        
        # Start at index 1 to skip the primary key column in the form
        for i in range(1, len(columns)):
            col_name = columns[i]
            if col_name in self.entries:
                entry_widget = self.entries[col_name][0]
                entry_widget.insert(0, values[i])

    def clear_form(self):
        """Empties all input fields."""
        for entry_widget, _ in self.entries.values():
            entry_widget.delete(0, "end")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Maintenance Record Management System")
        self.geometry("900x600")

        self.db = DatabaseManager()
        self.check_database_connection()

    def check_database_connection(self):
        """Attempts to connect to MySQL and displays an error if it fails."""
        success, message = self.db.connect()
        if not success:
            messagebox.showerror("Database Connection Failed", 
                                 f"Could not connect to MySQL server.\nPlease check credentials and ensure the server is running.\n\nError: {message}")
            self.destroy() # Close app if DB connection fails
        else:
            self.setup_ui()

    def setup_ui(self):
        # Create a Tabview to hold the different tables
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Define Schema structures: TableName -> (PrimaryKey, [(ColumnName, is_date_bool)])
        schemas = {
            "Departments": ("DepartmentID", [("DepartmentName", False), ("Location", False)]),
            "Technician": ("TechnicianID", [("FirstName", False), ("LastName", False), ("ContactNumber", False), ("Email", False)]),
            "DeviceTypes": ("DeviceTypeID", [("TypeName", False), ("DepartmentID", False)]),
            "MaintenanceRecord": ("RecordID", [("TechnicianID", False), ("CompletionDate", True), ("Notes", False)]),
            "Devices": ("DeviceID", [("RecordID", False), ("DeviceName", False), ("DeviceTypeID", False), ("SerialNumber", False), ("PurchaseDate", True), ("Status", False)])
        }

        # Dynamically create tabs for each table
        for table, (pk, fields) in schemas.items():
            tab = self.tabview.add(table)
            table_ui = GenericTableTab(tab, self.db, table, pk, fields)
            table_ui.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()