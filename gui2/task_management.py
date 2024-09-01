from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QPushButton, QDesktopWidget, QMessageBox, QTableWidget, QTableWidgetItem, QStackedWidget, QFormLayout, QLineEdit, QComboBox, QDialog
from PyQt5.QtCore import Qt
from database.task import TaskManager

class UserDetailWidget(QWidget):
    def __init__(self, user_id, username, role_name, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.role_name = role_name
        self.task_manager = parent.task_manager if parent else TaskManager()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # User details
        role_label = QLabel(f"Role: {self.role_name}")
        layout.addWidget(role_label)

        # Task table
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(["Task ID", "Title", "Description"])
        layout.addWidget(self.task_table)

        self.load_tasks()

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.clear_details)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def load_tasks(self):
        tasks = self.task_manager.get_tasks()
        user_tasks = [task for task in tasks if task[4] == self.user_id]

        self.task_table.setRowCount(len(user_tasks))
        for row, task in enumerate(user_tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(str(task[0])))
            self.task_table.setItem(row, 1, QTableWidgetItem(task[1]))
            self.task_table.setItem(row, 2, QTableWidgetItem(task[2]))

    def clear_details(self):
        """Restore the main content to the original state."""
        if self.parent():
            self.parent().parent().reset_main_content()


class TaskManagementWindow(QWidget):
    def __init__(self, user_id, username, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"Task Management for {self.username}")
        self.setGeometry(100, 100, 600, 400)

        self.task_manager = TaskManager()

        layout = QVBoxLayout()

        self.label = QLabel(f"Tasks for user: {self.username}")
        layout.addWidget(self.label)

        # Table to show tasks with due date
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(4)
        self.tasks_table.setHorizontalHeaderLabels(["Task ID", "Title", "Description", "Due Date"])
        layout.addWidget(self.tasks_table)

        self.load_tasks()

        # Buttons for actions
        buttons_layout = QHBoxLayout()
        delete_task_button = QPushButton("Delete Selected Task")
        delete_task_button.clicked.connect(self.delete_task)
        buttons_layout.addWidget(delete_task_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def load_tasks(self):
        """Load tasks from the database and display them in the table."""
        tasks = self.task_manager.get_tasks()
        user_tasks = [task for task in tasks if task[4] == self.user_id]

        self.tasks_table.setRowCount(len(user_tasks))
        for row, task in enumerate(user_tasks):
            self.tasks_table.setItem(row, 0, QTableWidgetItem(str(task[0])))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task[1]))
            self.tasks_table.setItem(row, 2, QTableWidgetItem(task[2]))
            self.tasks_table.setItem(row, 3, QTableWidgetItem(task[3].strftime('%Y-%m-%d')))  # Displaying due date

    def delete_task(self):
        """Delete the selected task from the database."""
        selected_row = self.tasks_table.currentRow()
        if selected_row >= 0:
            task_id = int(self.tasks_table.item(selected_row, 0).text())
            self.task_manager.delete_task(task_id)
            QMessageBox.information(self, "Delete Task", "Task deleted successfully.")
            self.load_tasks()  # Refresh the task table

            # Refresh the UserDetailDialog if it's open
            if self.parent() and isinstance(self.parent(), UserDetailWidget):
                self.parent().load_tasks()
        else:
            QMessageBox.warning(self, "Delete Task", "Please select a task to delete.")

    def closeEvent(self, event):
        """Handle the close event to ensure the database connection is properly closed."""
        self.task_manager.close_connection()
        event.accept()
