from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QHBoxLayout
from database.task import TaskManager
from gui.dialogs import UserDetailDialog



class TaskManagementWindow(QWidget):
    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.setWindowTitle(f"Task Management for {self.username}")
        self.setGeometry(100, 100, 600, 400)

        self.task_manager = TaskManager()

        layout = QVBoxLayout()

        self.label = QLabel(f"Tasks for user: {self.username}")
        layout.addWidget(self.label)

        # Table to show tasks
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(3)
        self.tasks_table.setHorizontalHeaderLabels(["Task ID", "Title", "Description"])
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
        tasks = self.task_manager.get_tasks()
        user_tasks = [task for task in tasks if task[4] == self.user_id]

        self.tasks_table.setRowCount(len(user_tasks))
        for row, task in enumerate(user_tasks):
            self.tasks_table.setItem(row, 0, QTableWidgetItem(str(task[0])))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(task[1]))
            self.tasks_table.setItem(row, 2, QTableWidgetItem(task[2]))

    def delete_task(self):
        selected_row = self.tasks_table.currentRow()
        if selected_row >= 0:
            task_id = int(self.tasks_table.item(selected_row, 0).text())
            self.task_manager.delete_task(task_id)
            QMessageBox.information(self, "Delete Task", "Task deleted successfully.")
            self.load_tasks()  # Refresh the task table

            # Refresh the UserDetailDialog if it's open
            if hasattr(self, 'parent') and isinstance(self.parent, UserDetailDialog):
                self.parent.refresh_task_table(self.task_manager.get_tasks())
        else:
            QMessageBox.warning(self, "Delete Task", "Please select a task to delete.")

    def show_task_management(self, user_id):
        username = self.users_table.item(self.users_table.currentRow(), 1).text()
        self.task_management_window = TaskManagementWindow(user_id, username, parent=self)
        self.task_management_window.show()


    def closeEvent(self, event):
        self.task_manager.close_connection()
        event.accept()
