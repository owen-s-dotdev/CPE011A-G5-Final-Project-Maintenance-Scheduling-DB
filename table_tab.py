# table_tab.py

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

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

    def add_record(self):
        values = [self.entries[col].get() for col in self.columns[1:]]
        placeholders = ", ".join(["?"] * len(values))
        col_names = ", ".join(self.columns[1:])

        try:
            conn = sqlite3.connect("it_inventory.db")
            conn.execute("PRAGMA foreign_keys = 1")
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {self.table_name} ({col_names}) VALUES ({placeholders})", values)
            conn.commit()
            conn.close()

            # Clear inputs
            for var in self.entries.values():
                var.set("")
            self.load_data()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Error", f"Integrity Error: {e}\nCheck your Foreign Key values.")

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect("it_inventory.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {self.table_name}")
        for row in cursor.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a record to delete.")
            return

        record_id = self.tree.item(selected[0], "values")[0]
        pk_col = self.columns[0]

        try:
            conn = sqlite3.connect("it_inventory.db")
            conn.execute("PRAGMA foreign_keys = 1")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.table_name} WHERE {pk_col}=?", (record_id,))
            conn.commit()
            conn.close()
            self.load_data()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("Database Error", f"Cannot delete record: {e}\nThis record is referenced by another table.")