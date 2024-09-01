from .connection import DatabaseConnection

class RoleManager:
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()

    def add_role(self, name):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("INSERT INTO roles (name) VALUES (%s)", (name,))
            self.db.connection.commit()
            print(f"Role '{name}' added successfully.")
        except Exception as e:
            print(f"Error adding role '{name}': {e}")
        finally:
            cursor.close()

    def get_roles(self):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("SELECT * FROM roles")
            roles = cursor.fetchall()
            return roles
        except Exception as e:
            print(f"Error retrieving roles: {e}")
            return []
        finally:
            cursor.close()

    def update_role(self, role_id, new_name):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("UPDATE roles SET name = %s WHERE id = %s", (new_name, role_id))
            self.db.connection.commit()
            print(f"Role ID {role_id} updated successfully.")
        except Exception as e:
            print(f"Error updating role ID {role_id}: {e}")
        finally:
            cursor.close()

    def delete_role(self, role_id):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("DELETE FROM roles WHERE id = %s", (role_id,))
            self.db.connection.commit()
            print(f"Role ID {role_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting role ID {role_id}: {e}")
        finally:
            cursor.close()

    def close_connection(self):
        self.db.disconnect()
