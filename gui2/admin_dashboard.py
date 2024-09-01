from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QPushButton,
    QDesktopWidget, QMessageBox, QTableWidget, QTableWidgetItem, QStackedWidget, QFormLayout,
    QLineEdit, QComboBox, QDialog
)
from PyQt5.QtCore import Qt
from database.user import UserManager
from database.role import RoleManager
from database.task import TaskManager
from gui2.task_management import TaskManagementWindow

class UserSelectDialog(QDialog):
    def __init__(self, users, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select User")
        self.setGeometry(100, 100, 300, 100)
        self.selected_user_id = None

        layout = QVBoxLayout()

        self.user_combo_box = QComboBox()
        for user in users:
            self.user_combo_box.addItem(user[1], user[0])  # Display username, store user ID
        layout.addWidget(self.user_combo_box)

        select_button = QPushButton("Select")
        select_button.clicked.connect(self.select_user)
        layout.addWidget(select_button)

        self.setLayout(layout)

    def select_user(self):
        self.selected_user_id = self.user_combo_box.currentData()
        self.accept()  # Close the dialog


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


class AdminDashboard(QWidget):
    def __init__(self, user):
        super().__init__()

        self.user = user
        self.user_manager = UserManager()
        self.role_manager = RoleManager()
        self.task_manager = TaskManager()

        self.setWindowTitle(f"Admin Dashboard - Welcome {self.user[1]}")
        self.initUI()

    def initUI(self):
        # Main layout
        self.main_layout = QHBoxLayout()

        # Sidebar with buttons
        self.sidebar_layout = QVBoxLayout()

        # View User Button
        self.view_user_button = QPushButton("View User")
        self.view_user_button.clicked.connect(self.open_user_select_dialog)
        self.sidebar_layout.addWidget(self.view_user_button)

        # Manage Users Button
        self.manage_users_button = QPushButton("Manage Users")
        self.manage_users_button.clicked.connect(self.show_users)
        self.sidebar_layout.addWidget(self.manage_users_button)

        # Manage Roles Button
        self.manage_roles_button = QPushButton("Manage Roles")
        self.manage_roles_button.clicked.connect(self.manage_roles)
        self.sidebar_layout.addWidget(self.manage_roles_button)

        # Logout Button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        self.sidebar_layout.addWidget(self.logout_button)

        self.sidebar_layout.addStretch()

        # User Tree
        self.user_tree = QTreeWidget()
        self.user_tree.setHeaderLabels(["User", "Role"])

        # Load users into the tree
        self.load_users()

        # Main content area
        self.content_stack = QStackedWidget()
        self.main_content = QLabel("Main Content Area (Details/Tasks will be shown here)")
        self.main_content.setAlignment(Qt.AlignCenter)
        self.content_stack.addWidget(self.main_content)

        # Add to main layout
        self.main_layout.addLayout(self.sidebar_layout, 1)
        self.main_layout.addWidget(self.user_tree, 2)
        self.main_layout.addWidget(self.content_stack, 4)

        self.setLayout(self.main_layout)
        self.centerAndResize()

    def reset_main_content(self):
        """Reset the main content to the original state."""
        self.content_stack.setCurrentWidget(self.main_content)

    def load_users(self):
        """Load users from the database and populate the tree widget."""
        self.user_tree.clear()  # Clear the tree to ensure no stale data
        users = self.user_manager.get_users()
        for user in users:
            user_id, username, _, role_id = user
            role_name = self.get_role_name(role_id)
            user_item = QTreeWidgetItem([username, role_name])

            # Load tasks for each user
            tasks = self.task_manager.get_tasks()
            for task in tasks:
                if task[4] == user_id:
                    task_item = QTreeWidgetItem([task[1]])  # task[1] is the task title
                    user_item.addChild(task_item)

            self.user_tree.addTopLevelItem(user_item)

    def get_role_name(self, role_id):
        roles = self.role_manager.get_roles()
        for role in roles:
            if role[0] == role_id:
                return role[1]
        return "Unknown"

    def open_user_select_dialog(self):
        """Open a dialog to select a user for viewing details."""
        users = self.user_manager.get_users()
        dialog = UserSelectDialog(users, self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_user_id is not None:
            self.show_user_details(dialog.selected_user_id)

    def show_user_details(self, user_id):
        """Show details of the selected user in the main content area."""
        # Reload the user tree to ensure it has the latest data
        self.load_users()

        # Retrieve the updated user details
        user = next((u for u in self.user_manager.get_users() if u[0] == user_id), None)

        if user is not None:
            role_name = self.get_role_name(user[3])
            # Create a new UserDetailWidget to reflect any updates
            detail_widget = UserDetailWidget(user_id, user[1], role_name, self)
            self.content_stack.addWidget(detail_widget)
            self.content_stack.setCurrentWidget(detail_widget)
        else:
            QMessageBox.warning(self, "View User", "The selected user does not exist.")

    def refresh_all(self):
        """Refresh all relevant UI components."""
        self.load_users()  # Refresh the user tree
        self.update_current_user_details()  # Update the user details in the middle content area

    def update_current_user_details(self):
        """Update the currently viewed user details if any."""
        current_widget = self.content_stack.currentWidget()
        if isinstance(current_widget, UserDetailWidget):
            user_id = current_widget.user_id
            self.show_user_details(user_id)

    def show_users(self):
        """Refresh the content stack to show the user management interface and update the user tree."""
        # Refresh the user tree with the latest data
        self.load_users()

        # Clear the current content in the stack
        self.content_stack.setCurrentWidget(self.main_content)

        # Create the user management widget
        user_management_widget = QWidget()
        user_management_layout = QVBoxLayout()

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels(["ID", "Username", "Role"])

        users = self.user_manager.get_users()

        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user[0])))
            self.users_table.setItem(row, 1, QTableWidgetItem(user[1]))
            role_name = self.get_role_name(user[3])
            self.users_table.setItem(row, 2, QTableWidgetItem(role_name))

        user_management_layout.addWidget(self.users_table)

        buttons_layout = QHBoxLayout()

        add_user_button = QPushButton("Add User")
        add_user_button.clicked.connect(self.add_user)
        buttons_layout.addWidget(add_user_button)

        update_user_button = QPushButton("Update User")
        update_user_button.clicked.connect(self.update_user)
        buttons_layout.addWidget(update_user_button)

        delete_user_button = QPushButton("Delete User")
        delete_user_button.clicked.connect(self.confirm_delete_user)
        buttons_layout.addWidget(delete_user_button)

        user_management_layout.addLayout(buttons_layout)
        user_management_widget.setLayout(user_management_layout)

        # Replace the current widget in the content stack
        self.content_stack.addWidget(user_management_widget)
        self.content_stack.setCurrentWidget(user_management_widget)

        # Call relevant functions to ensure everything is up-to-date
        self.refresh_all()

    def clear_layout(self, layout):
        """Clear a layout and its child widgets."""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

    def add_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New User")

        layout = QFormLayout()

        # Username Input
        username_input = QLineEdit()
        layout.addRow("Username:", username_input)

        # Password Input
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Password:", password_input)

        # Role Selection
        role_combo = QComboBox()
        roles = self.role_manager.get_roles()
        role_dict = {role[1]: role[0] for role in roles}
        role_combo.addItems(role_dict.keys())
        layout.addRow("Role:", role_combo)

        # Buttons
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.confirm_add_user(dialog, username_input, password_input, role_dict, role_combo))
        buttons_layout.addWidget(add_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.close)
        buttons_layout.addWidget(cancel_button)

        layout.addRow(buttons_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def confirm_add_user(self, dialog, username_input, password_input, role_dict, role_combo):
        username = username_input.text().strip()
        password = password_input.text().strip()
        role_name = role_combo.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username and Password cannot be empty.")
            return

        # Check if the username already exists
        existing_users = [user[1] for user in self.user_manager.get_users()]
        if username in existing_users:
            QMessageBox.warning(self, "User Exists", "A user with this username already exists.")
            return

        role_id = role_dict.get(role_name)
        if role_id:
            try:
                self.user_manager.add_user(username, password, role_id)
                QMessageBox.information(self, "Success", "User added successfully.")
                dialog.close()
                self.show_users()  # Refresh the interface after adding a user
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not add user: {e}")
        else:
            QMessageBox.warning(self, "Error", "Invalid role selected.")

    def update_user(self):
        selected = self.users_table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Update User", "Please select a user to update.")
            return

        user_id = int(self.users_table.item(selected, 0).text())
        current_username = self.users_table.item(selected, 1).text()
        current_role = self.users_table.item(selected, 2).text()

        # Check if the user exists
        user = next((u for u in self.user_manager.get_users() if u[0] == user_id), None)
        if not user:
            QMessageBox.warning(self, "User Not Found", "The selected user does not exist.")
            self.show_users()
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Update User")

        layout = QFormLayout()

        # Username Input
        username_input = QLineEdit(current_username)
        layout.addRow("Username:", username_input)

        # Password Input
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("New Password (leave blank to keep current):", password_input)

        # Role Selection
        role_combo = QComboBox()
        roles = self.role_manager.get_roles()
        role_dict = {role[1]: role[0] for role in roles}
        role_combo.addItems(role_dict.keys())
        role_combo.setCurrentText(current_role)
        layout.addRow("Role:", role_combo)

        # Buttons
        buttons_layout = QHBoxLayout()
        update_button = QPushButton("Update")
        update_button.clicked.connect(lambda: self.confirm_update_user(dialog, user_id, username_input, password_input, role_dict, role_combo))
        buttons_layout.addWidget(update_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.close)
        buttons_layout.addWidget(cancel_button)

        layout.addRow(buttons_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def confirm_update_user(self, dialog, user_id, username_input, password_input, role_dict, role_combo):
        username = username_input.text().strip()
        password = password_input.text().strip()
        role_name = role_combo.currentText()

        if not username:
            QMessageBox.warning(self, "Input Error", "Username cannot be empty.")
            return

        role_id = role_dict.get(role_name)
        if role_id:
            try:
                self.user_manager.update_user(user_id, new_username=username, new_password=password if password else None, new_role_id=role_id)
                QMessageBox.information(self, "Success", "User updated successfully.")
                dialog.close()
                self.show_users()  # Refresh the interface after updating a user
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not update user: {e}")
        else:
            QMessageBox.warning(self, "Error", "Invalid role selected.")

    def confirm_delete_user(self):
        selected = self.users_table.currentRow()
        if selected >= 0:
            user_id = int(self.users_table.item(selected, 0).text())

            # Check if the user exists
            user = next((u for u in self.user_manager.get_users() if u[0] == user_id), None)
            if not user:
                QMessageBox.warning(self, "User Not Found", "The selected user does not exist.")
                self.show_users()
                return

            tasks_manager = TaskManager()
            tasks = tasks_manager.get_tasks()

            # Count the number of tasks associated with this user
            user_tasks = [task for task in tasks if task[4] == user_id]
            num_tasks = len(user_tasks)

            if num_tasks > 0:  # Check if the user has tasks
                reply = QMessageBox.question(self, "Confirm Deletion",
                                            f"This user has {num_tasks} associated task(s). "
                                            "Do you acknowledge the consequences of deletion?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.acknowledge_and_delete(user_id)
            else:
                self.delete_user(user_id)
        else:
            QMessageBox.warning(self, "Delete User", "Please select a user to delete.")

    def acknowledge_and_delete(self, user_id):
        # Create a custom QMessageBox
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Acknowledge Deletion")
        msg_box.setText("What would you like to do?")

        # Add custom buttons
        delete_all_button = msg_box.addButton("Delete All Tasks", QMessageBox.AcceptRole)
        delete_manual_button = msg_box.addButton("Delete Tasks Manually", QMessageBox.YesRole)
        exit_button = msg_box.addButton("Exit", QMessageBox.RejectRole)

        # Set the default button to exit
        msg_box.setDefaultButton(exit_button)

        msg_box.exec_()

        # Handle the button clicks
        if msg_box.clickedButton() == delete_all_button:
            self.delete_user(user_id)
        elif msg_box.clickedButton() == delete_manual_button:
            self.show_task_management(user_id)
        # No need to handle the exit button; it will just close the dialog

    def show_task_management(self, user_id):
        username = self.users_table.item(self.users_table.currentRow(), 1).text()
        self.task_management_window = TaskManagementWindow(user_id, username)
        self.task_management_window.show()

    def delete_user(self, user_id):
        try:
            self.user_manager.delete_user(user_id)
            QMessageBox.information(self, "Delete User", "User deleted successfully.")
            self.show_users()  # Refresh the interface after deleting a user
        except Exception as e:
            QMessageBox.warning(self, "Delete User", f"Error: {str(e)}")

    def manage_roles(self):
        """Show the role management interface in the main content area."""
        role_management_widget = QWidget()
        role_management_layout = QVBoxLayout()

        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(2)
        self.roles_table.setHorizontalHeaderLabels(["ID", "Role Name"])

        roles = self.role_manager.get_roles()

        self.roles_table.setRowCount(len(roles))
        for row, role in enumerate(roles):
            self.roles_table.setItem(row, 0, QTableWidgetItem(str(role[0])))
            self.roles_table.setItem(row, 1, QTableWidgetItem(role[1]))

        role_management_layout.addWidget(self.roles_table)

        buttons_layout = QHBoxLayout()

        add_role_button = QPushButton("Add Role")
        add_role_button.clicked.connect(self.add_role)
        buttons_layout.addWidget(add_role_button)

        delete_role_button = QPushButton("Delete Role")
        delete_role_button.clicked.connect(self.confirm_delete_role)
        buttons_layout.addWidget(delete_role_button)

        role_management_layout.addLayout(buttons_layout)
        role_management_widget.setLayout(role_management_layout)

        # Replace the current widget in the content stack
        self.content_stack.addWidget(role_management_widget)
        self.content_stack.setCurrentWidget(role_management_widget)

    def add_role(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Role")

        layout = QFormLayout()

        # Role Name Input
        role_name_input = QLineEdit()
        layout.addRow("Role Name:", role_name_input)

        # Buttons
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.confirm_add_role(dialog, role_name_input))
        buttons_layout.addWidget(add_button)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.close)
        buttons_layout.addWidget(cancel_button)

        layout.addRow(buttons_layout)
        dialog.setLayout(layout)
        dialog.exec_()

    def confirm_add_role(self, dialog, role_name_input):
        role_name = role_name_input.text().strip()

        if not role_name:
            QMessageBox.warning(self, "Input Error", "Role name cannot be empty.")
            return

        try:
            self.role_manager.add_role(role_name)
            QMessageBox.information(self, "Success", "Role added successfully.")
            dialog.close()
            self.manage_roles()  # Refresh the interface after adding a role
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not add role: {e}")

    def confirm_delete_role(self):
        selected = self.roles_table.currentRow()
        if selected >= 0:
            role_id = int(self.roles_table.item(selected, 0).text())
            role_name = self.roles_table.item(selected, 1).text()

            # Check how many users have this role
            users_with_role = [user for user in self.user_manager.get_users() if user[3] == role_id]
            num_users = len(users_with_role)

            if num_users > 0:
                QMessageBox.warning(self, "Role In Use", f"Role '{role_name}' cannot be deleted because {num_users} user(s) have this role.")
            else:
                reply = QMessageBox.question(self, "Confirm Deletion",
                                            f"Are you sure you want to delete the role '{role_name}'?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    try:
                        self.role_manager.delete_role(role_id)
                        QMessageBox.information(self, "Success", "Role deleted successfully.")
                        self.manage_roles()  # Refresh the interface after deleting a role
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Could not delete role: {e}")
        else:
            QMessageBox.warning(self, "Delete Role", "Please select a role to delete.")

    def logout(self):
        self.user_manager.close_connection()
        self.role_manager.close_connection()
        self.close()

    def centerAndResize(self):
        """Center the dialog and resize it to 80% of the screen size."""
        screen_geometry = QDesktopWidget().availableGeometry()
        width = int(screen_geometry.width() * 0.8)
        height = int(screen_geometry.height() * 0.8)
        self.resize(width, height)
        self.move((screen_geometry.width() - width) // 2, (screen_geometry.height() - height) // 2)
