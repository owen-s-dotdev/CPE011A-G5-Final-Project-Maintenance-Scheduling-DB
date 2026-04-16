import mysql.connector
from mysql.connector import Error
import json
import os

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.load_config()

    
    # Read credentials from JSON
    def load_config(self):
        """Reads database credentials from the external config folder."""
        config_path = os.path.join('config', 'config.json')
        try:
            with open(config_path, 'r') as file:
                config_data = json.load(file)
                self.db_host = config_data['database']['host']
                self.db_user = config_data['database']['user']
                self.db_pass = config_data['database']['password']
                self.db_name = config_data['database']['name']
        except FileNotFoundError:
            raise Exception(f"Missing configuration file at {config_path}")
        except json.JSONDecodeError:
            raise Exception("Invalid JSON formatting in config.json")
        
    def connect(self):
        """Establishes a connection to the MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=self.db_host,       
                user=self.db_user,      
                password=self.db_pass,   
                database=self.db_name,
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