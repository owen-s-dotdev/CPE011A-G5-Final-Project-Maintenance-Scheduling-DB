import tkinter as tk
from tkinter import ttk

# Import custom modules
from database_mdb import setup_database
from table_tab import TableTab

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IT Inventory Management System")
        self.root.geometry("1000x500")

        # Setup Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Define Schema Structures (Table Name : Columns) - Corrected for ERD
        tables = {
            "Departments": ["DepartmentID", "DepartmentName", "Location"],
            "DeviceTypes": ["DeviceTypeID", "TypeName", "DepartmentID"],
            "Technician": ["TechnicianID", "FirstName", "LastName", "ContactNumber", "Email"],
            "Devices": ["DeviceID", "DeviceName", "DeviceTypeID", "SerialNumber", "PurchaseDate", "Status"], # Corrected
            "MaintenanceRecord": ["RecordID", "DeviceID", "TechnicianID", "CompletionDate", "Notes"] # Corrected
        }

        # Generate a tab for each table
        for table_name, columns in tables.items():
            tab = TableTab(self.notebook, table_name, columns)
            self.notebook.add(tab, text=table_name)

if __name__ == "__main__":
    # Initialize the database (MariaDB) before launching the GUI
    setup_database()
    
    # Launch the application
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()     