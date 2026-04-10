import mysql.connector
from mysql.connector import Error

# Database Configuration Variables
DB_HOST = "127.0.0.1" # Using IP directly prevents IPv6 hanging
DB_USER = "root"
DB_PASS = ""
DB_NAME = "maintenance_record_db"

class DatabaseManager:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Establishes a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASS,
                database=DB_NAME,
                connection_timeout=3, # Fails fast instead of hanging
                use_pure=True
            )
            return True, "Connection successful."
        except Exception as e:
            print(f"\n--- DATABASE CRASH LOG ---")
            print(f"Reason: {e}")
            print(f"--------------------------\n")
            return False, str(e)

    def disconnect(self):
        """Closes the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def fetch_all(self, table_name):
        """Retrieves all records from a specified table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            records = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return records, columns
        except Error as e:
            raise e

    def insert_record(self, table_name, columns, values):
        """Inserts a new record using parameterized queries."""
        placeholders = ", ".join(["%s"] * len(values))
        col_str = ", ".join(columns)
        query = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
        except Error as e:
            self.connection.rollback()
            raise e

    def update_record(self, table_name, pk_col, pk_val, columns, values):
        """Updates an existing record using parameterized queries."""
        set_str = ", ".join([f"{col} = %s" for col in columns])
        query = f"UPDATE {table_name} SET {set_str} WHERE {pk_col} = %s"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, values + [pk_val])
            self.connection.commit()
            cursor.close()
        except Error as e:
            self.connection.rollback()
            raise e

    def delete_record(self, table_name, pk_col, pk_val):
        """Deletes a record based on its primary key."""
        query = f"DELETE FROM {table_name} WHERE {pk_col} = %s"
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (pk_val,))
            self.connection.commit()
            cursor.close()
        except Error as e:
            self.connection.rollback()
            raise e