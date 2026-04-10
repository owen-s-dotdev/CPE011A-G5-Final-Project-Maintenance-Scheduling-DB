import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date # for dates

# Re-use the db_config from your database_mariadb.py file
from database_mdb import db_config 

class TableTab(ttk.Frame):
    """A generic tab frame to handle basic CRUD operations for any given table."""
    def __init__(self, parent, table_name, columns):
        super().__init__(parent)
        self.table_name = table_name
        self.columns = columns
        self.entries = {}

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Input Frame
        input_frame = tk.Frame(self)
        input_frame.pack(pady=10, fill=tk.X)

        # Generate labels and entry fields dynamically, skipping the Primary Key
        col_index = 0
        for col in self.columns[1:]: 
            tk.Label(input_frame, text=f"{col}:").grid(row=0, column=col_index * 2, padx=5, pady=5, sticky=tk.E)
            entry_var = tk.StringVar()
            # For date fields, you might want a specialized date picker widget here.
            # Using a simple entry for now.
            entry = tk.Entry(input_frame, textvariable=entry_var)
            entry.grid(row=0, column=(col_index * 2) + 1, padx=5, pady=5)
            self.entries[col] = entry_var
            col_index += 1

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Record", command=self.add_record).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_record).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Refresh Data", command=self.load_data).pack(side=tk.LEFT, padx=10)

        # Treeview (Data Table)
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

    def _get_connection(self):
        return mysql.connector.connect(**db_config)

    def add_record(self):
        values = [self.entries[col].get() for col in self.columns[1:]]
        placeholders = ", ".join(["%s"] * len(values)) # Use %s for MariaDB
        col_names = ", ".join(self.columns[1:])

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = f"INSERT INTO {self.table_name} ({col_names}) VALUES ({placeholders})"
            cursor.execute(query, values)
            conn.commit()
            print(f"Record added to {self.table_name}")

            # Clear inputs
            for var in self.entries.values():
                var.set("")
            self.load_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}\nCheck your inputs.")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name}")
            for row in cursor.fetchall():
                # Convert date objects to strings for display in Treeview
                processed_row = [str(val) if isinstance(val, (date)) else val for val in row]
                self.tree.insert("", tk.END, values=processed_row)
        except mysql.connector.Error as err:
            print(f"Error loading data: {err}")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")
            return

        record_id = self.tree.item(selected[0], "values")[0]
        pk_col = self.columns[0]

        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = f"DELETE FROM {self.table_name} WHERE {pk_col} = %s"
            cursor.execute(query, (record_id,))
            conn.commit()
            print(f"Record deleted from {self.table_name}")
            self.load_data()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Cannot delete record: {err}\nThis record may be referenced by another table.")
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()