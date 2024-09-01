from .connection import DatabaseConnection

class TaskManager:
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()

    def add_task(self, title, description, due_date, user_id):
        cursor = self.db.get_cursor()
        try:
            cursor.execute(
                "INSERT INTO tasks (title, description, due_date, user_id) VALUES (%s, %s, %s, %s)",
                (title, description, due_date, user_id)
            )
            self.db.connection.commit()
            print(f"Task '{title}' added successfully.")
        except Exception as e:
            print(f"Error adding task '{title}': {e}")
        finally:
            cursor.close()

    def get_tasks(self):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("SELECT * FROM tasks")
            tasks = cursor.fetchall()
            return tasks
        except Exception as e:
            print(f"Error retrieving tasks: {e}")
            return []
        finally:
            cursor.close()

    def update_task(self, task_id, new_title=None, new_description=None, new_due_date=None, new_user_id=None):
        cursor = self.db.get_cursor()
        try:
            if new_title:
                cursor.execute("UPDATE tasks SET title = %s WHERE id = %s", (new_title, task_id))
            if new_description:
                cursor.execute("UPDATE tasks SET description = %s WHERE id = %s", (new_description, task_id))
            if new_due_date:
                cursor.execute("UPDATE tasks SET due_date = %s WHERE id = %s", (new_due_date, task_id))
            if new_user_id is not None:
                cursor.execute("UPDATE tasks SET user_id = %s WHERE id = %s", (new_user_id, task_id))
            self.db.connection.commit()
            print(f"Task ID {task_id} updated successfully.")
        except Exception as e:
            print(f"Error updating task ID {task_id}: {e}")
        finally:
            cursor.close()

    def delete_task(self, task_id):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            self.db.connection.commit()
            print(f"Task ID {task_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting task ID {task_id}: {e}")
        finally:
            cursor.close()

    def delete_tasks_by_user(self, user_id):
        cursor = self.db.get_cursor()
        try:
            cursor.execute("DELETE FROM tasks WHERE user_id = %s", (user_id,))
            self.db.connection.commit()
            print(f"Tasks for user ID {user_id} deleted successfully.")
        except Exception as e:
            print(f"Error deleting tasks for user ID {user_id}: {e}")
        finally:
            cursor.close()
            
    def close_connection(self):
        self.db.disconnect()
