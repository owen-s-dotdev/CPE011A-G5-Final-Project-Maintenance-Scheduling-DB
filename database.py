# database.py

import sqlite3

def setup_database():
    """Creates the SQLite database and tables based on the ERD."""
    conn = sqlite3.connect("it_inventory.db")
    # Enable foreign key constraint enforcement in SQLite
    conn.execute("PRAGMA foreign_keys = 1") 
    cursor = conn.cursor()

    # Create Departments Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Departments (
            DepartmentID INTEGER PRIMARY KEY AUTOINCREMENT,
            DepartmentName TEXT NOT NULL,
            Location TEXT
        )
    ''')

    # Create DeviceTypes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DeviceTypes (
            DeviceTypeID INTEGER PRIMARY KEY AUTOINCREMENT,
            TypeName TEXT NOT NULL,
            DepartmentID INTEGER,
            FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
        )
    ''')

    # Create Technician Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Technician (
            TechnicianID INTEGER PRIMARY KEY AUTOINCREMENT,
            FirstName TEXT NOT NULL,
            LastName TEXT NOT NULL,
            ContactNumber TEXT,
            Email TEXT
        )
    ''')

    # Create MaintenanceRecord Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MaintenanceRecord (
            RecordID INTEGER PRIMARY KEY AUTOINCREMENT,
            TechnicianID INTEGER,
            CompletionDate TEXT,
            Notes TEXT,
            FOREIGN KEY (TechnicianID) REFERENCES Technician(TechnicianID)
        )
    ''')

    # Create Devices Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Devices (
            DeviceID INTEGER PRIMARY KEY AUTOINCREMENT,
            RecordID INTEGER,
            DeviceName TEXT NOT NULL,
            DeviceTypeID INTEGER,
            SerialNumber TEXT,
            PurchaseDate TEXT,
            Status TEXT,
            FOREIGN KEY (RecordID) REFERENCES MaintenanceRecord(RecordID),
            FOREIGN KEY (DeviceTypeID) REFERENCES DeviceTypes(DeviceTypeID)
        )
    ''')

    conn.commit()
    conn.close()