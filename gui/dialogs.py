from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton

from gui.task_management import TaskManager  # Ensure this import is correct based on your project structure

class UserDetailDialog(QDialog):
    def __init__(self, user_id, username, role_name, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.task_manager = TaskManager()  # Initialize task_manager here
        self.setWindowTitle(f"User Details - {username}")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # User Role
        role_label = QLabel(f"Role: {role_name}")
        layout.addWidget(role_label)

        # Task Table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(["Task ID", "Title", "Description"])
        self.refresh_task_table()
        layout.addWidget(self.task_table)

        # Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def refresh_task_table(self):
        """Refresh the task table with the latest data."""
        tasks = self.task_manager.get_tasks()  # Fetch tasks directly from the task manager
        user_tasks = [task for task in tasks if task[4] == self.user_id]  # Filter tasks for the current user
        self.task_table.setRowCount(len(user_tasks))
        for row, task in enumerate(user_tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(str(task[0])))
            self.task_table.setItem(row, 1, QTableWidgetItem(task[1]))
            self.task_table.setItem(row, 2, QTableWidgetItem(task[2]))
