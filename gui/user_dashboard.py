from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog, QLineEdit, QTextEdit, QFormLayout, QMessageBox
from database.task import TaskManager
from gui.task_management import TaskManagementWindow
from database.role import RoleManager
import datetime

class AddTaskDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.task_manager = TaskManager()

        self.setWindowTitle("Add Task")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Task title input
        self.title_input = QLineEdit()
        form_layout.addRow("Task Title:", self.title_input)

        # Task description input
        self.description_input = QTextEdit()
        form_layout.addRow("Task Description:", self.description_input)

        # Task due date input
        self.due_date_input = QLineEdit()
        self.due_date_input.setPlaceholderText("YYYY-MM-DD")
        form_layout.addRow("Due Date:", self.due_date_input)

        layout.addLayout(form_layout)

        # Add task button
        add_button = QPushButton("Add Task")
        add_button.clicked.connect(self.add_task)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def add_task(self):
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        due_date = self.due_date_input.text().strip()

        # Validate inputs
        if not title or not description or not due_date:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        try:
            due_date_obj = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            QMessageBox.warning(self, "Date Error", "Invalid date format. Use YYYY-MM-DD.")
            return

        # Add the task to the database
        self.task_manager.add_task(title, description, due_date_obj, self.user_id)
        self.accept()

class UserDashboard(QWidget):
    def __init__(self, user):
        super().__init__()

        self.user = user
        self.setWindowTitle(f"User Dashboard - Welcome {self.user[1]}")
        self.setGeometry(100, 100, 800, 600)

        # Initialize managers
        self.task_manager = TaskManager()
        self.role_manager = RoleManager()

        # Main Layout
        layout = QVBoxLayout()

        # Top Layout for Username and Role
        top_layout = QHBoxLayout()

        # Username on the top left
        username_label = QLabel(f"Username: {self.user[1]}")
        top_layout.addWidget(username_label)

        # Role on the top right
        role_name = self.get_role_name(self.user[3])
        role_label = QLabel(f"Role: {role_name}")
        top_layout.addWidget(role_label)

        # Add the top layout to the main layout
        layout.addLayout(top_layout)

        # View Tasks Button
        self.view_tasks_button = QPushButton("View Tasks")
        self.view_tasks_button.clicked.connect(self.view_tasks)
        layout.addWidget(self.view_tasks_button)

        # Add Task Button
        self.add_task_button = QPushButton("Add Task")
        self.add_task_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_task_button)

        # Logout Button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

    def get_role_name(self, role_id):
        roles = self.role_manager.get_roles()
        for role in roles:
            if role[0] == role_id:
                return role[1]
        return "Unknown"

    def view_tasks(self):
        # Open task management window to view tasks
        self.task_management_window = TaskManagementWindow(self.user[0], self.user[1], parent=self)
        self.task_management_window.show()

    def add_task(self):
        # Open a dialog to add a task
        dialog = AddTaskDialog(self.user[0], parent=self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Add Task", "Task added successfully.")
        else:
            QMessageBox.warning(self, "Add Task", "Task addition canceled.")

    def delete_task(self):
        # Open task management window to delete tasks
        self.task_management_window = TaskManagementWindow(self.user[0], self.user[1], parent=self, delete_task=True)
        self.task_management_window.show()

    def logout(self):
        """Handle the logout process."""
        # Add any cleanup or logout logic here, if necessary
        QMessageBox.information(self, "Logout", "You have been logged out.")
        self.close()

