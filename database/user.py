import bcrypt
from .connection import DatabaseConnection
from .task import TaskManager  # Import TaskManager to manage task deletion

class UserManager:
    # Existing code...

    def delete_user(self, user_id):
        cursor = self.db.get_cursor()
        task_manager = TaskManager()  # Initialize TaskManager to delete tasks
        try:
            # First, delete all tasks associated with this user
            task_manager.delete_tasks_by_user(user_id)

            # Now, delete the user
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.db.connection.commit()
            print(f"User ID {user_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting user ID {user_id}: {e}")
        finally:
            cursor.close()
            task_manager.close_connection()


class UserManager:
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')  # Store the hashed password as a string

    def check_password(self, hashed_password, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def add_user(self, username, password, role_id):
        cursor = self.db.get_cursor()
        hashed_password = self.hash_password(password)
        try:
            cursor.execute("INSERT INTO users (username, password, role_id) VALUES (%s, %s, %s)",
                           (username, hashed_password, role_id))
            self.db.connection.commit()
            print(f"User '{username}' added successfully.")
        except Exception as e:
            print(f"Error adding user '{username}': {e}")
        finally:
            cursor.close()

    def get_users(self):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            return users
        except Exception as e:
            print(f"Error retrieving users: {e}")
            return []
        finally:
            cursor.close()

    def update_user(self, user_id, new_username=None, new_password=None, new_role_id=None):
        cursor = self.db.get_cursor()
        try:
            if new_username:
                cursor.execute("UPDATE users SET username = %s WHERE id = %s",
                               (new_username, user_id))
            if new_password:
                hashed_password = self.hash_password(new_password)
                cursor.execute("UPDATE users SET password = %s WHERE id = %s",
                               (hashed_password, user_id))
            if new_role_id is not None:
                cursor.execute("UPDATE users SET role_id = %s WHERE id = %s",
                               (new_role_id, user_id))
            self.db.connection.commit()
            print(f"User ID {user_id} updated successfully.")
        except Exception as e:
            print(f"Error updating user ID {user_id}: {e}")
        finally:
            cursor.close()

    def delete_user(self, user_id):
        cursor = self.db.get_cursor()
        task_manager = TaskManager()  # Initialize TaskManager to delete tasks
        try:
            # First, delete all tasks associated with this user
            task_manager.delete_tasks_by_user(user_id)

            # Now, delete the user
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.db.connection.commit()
            print(f"User ID {user_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting user ID {user_id}: {e}")
        finally:
            cursor.close()
            task_manager.close_connection()


    def authenticate_user(self, username, password):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("SELECT id, username, password, role_id FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user and self.check_password(user[2], password):
                print(f"Authentication successful for user: {username}")
                return user
            else:
                print("Authentication failed.")
                return None
        except Exception as e:
            print(f"Error authenticating user '{username}': {e}")
            return None
        finally:
            cursor.close()

    def close_connection(self):
        self.db.disconnect()
