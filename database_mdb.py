# database_mariadb.py
import mariadb
import sys

# Configuration for your MariaDB connection
db_config = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "123123",
    "database": "it_inventory"
}

def setup_database():
    """Creates the MariaDB tables based on the project ERD."""
    try:
        conn = mariadb.connect(**db_config)
        cursor = conn.cursor()

        # 1. Create Departments Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Departments (
                DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
                DepartmentName VARCHAR(255) NOT NULL,
                Location VARCHAR(255)
            )
        ''')

        # 2. Create DeviceTypes Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DeviceTypes (
                DeviceTypeID INT AUTO_INCREMENT PRIMARY KEY,
                TypeName VARCHAR(255) NOT NULL,
                DepartmentID INT,
                CONSTRAINT fk_dept FOREIGN KEY (DepartmentID) 
                    REFERENCES Departments(DepartmentID)
            )
        ''')

        # 3. Create Technician Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Technician (
                TechnicianID INT AUTO_INCREMENT PRIMARY KEY,
                FirstName VARCHAR(255) NOT NULL,
                LastName VARCHAR(255) NOT NULL,
                ContactNumber VARCHAR(50),
                Email VARCHAR(255)
            )
        ''')

        # 4. Create Devices Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Devices (
                DeviceID INT AUTO_INCREMENT PRIMARY KEY,
                DeviceName VARCHAR(255) NOT NULL,
                DeviceTypeID INT,
                SerialNumber VARCHAR(255),
                PurchaseDate DATE,
                Status VARCHAR(50),
                CONSTRAINT fk_type FOREIGN KEY (DeviceTypeID) 
                    REFERENCES DeviceTypes(DeviceTypeID)
            )
        ''')

        # 5. Create MaintenanceRecord Table (Corrected relationship)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MaintenanceRecord (
                RecordID INT AUTO_INCREMENT PRIMARY KEY,
                DeviceID INT,
                TechnicianID INT,
                CompletionDate DATE,
                Notes TEXT,
                CONSTRAINT fk_device FOREIGN KEY (DeviceID) 
                    REFERENCES Devices(DeviceID),
                CONSTRAINT fk_tech FOREIGN KEY (TechnicianID) 
                    REFERENCES Technician(TechnicianID)
            )
        ''')

        conn.commit()
        print("MariaDB schema initialized successfully.")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_database()