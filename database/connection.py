# database/connection.py

import mysql.connector
from .config import DATABASE_CONFIG

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=DATABASE_CONFIG['host'],
                user=DATABASE_CONFIG['user'],
                password=DATABASE_CONFIG['password'],
                database=DATABASE_CONFIG['database']
            )
            print("Database connection successful!")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection = None

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def get_cursor(self):
        if self.connection:
            return self.connection.cursor()
        else:
            return None

    def create_tables(self):
        if self.connection:
            cursor = self.get_cursor()

            # SQL Statements for table creation
            create_roles_table = """
            CREATE TABLE IF NOT EXISTS roles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(50) NOT NULL UNIQUE
            );
            """

            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role_id INT,
                FOREIGN KEY (role_id) REFERENCES roles(id)
            );
            """

            create_tasks_table = """
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                due_date DATE,
                user_id INT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """

            # Execute table creation statements
            try:
                cursor.execute(create_roles_table)
                cursor.execute(create_users_table)
                cursor.execute(create_tasks_table)
                print("Tables created successfully!")
            except mysql.connector.Error as err:
                print(f"Error creating tables: {err}")

            cursor.close()

# Example usage
# if __name__ == "__main__":
#     db = DatabaseConnection()
#     db.connect()
#     db.create_tables()
#     db.disconnect()
