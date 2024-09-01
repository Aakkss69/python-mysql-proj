from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QHBoxLayout
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QPushButton
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox, QHBoxLayout
from database.user import UserManager
from database.role import RoleManager
from database.task import TaskManager
from gui.task_management import TaskManagementWindow
from gui.dialogs import UserDetailDialog


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



class AdminDashboard(QWidget):
    def __init__(self, user):
        super().__init__()

        self.user = user
        self.setWindowTitle(f"Admin Dashboard - Welcome {self.user[1]}")
        self.setGeometry(100, 100, 600, 400)

        self.user_manager = UserManager()
        self.role_manager = RoleManager()
        self.task_manager = TaskManager()

        # Layout
        layout = QVBoxLayout()

        # Welcome Label
        self.welcome_label = QLabel(f"Welcome, {self.user[1]}! You have admin privileges.")
        layout.addWidget(self.welcome_label)

        # View User Button
        self.view_user_button = QPushButton("View User")
        self.view_user_button.clicked.connect(self.open_user_select_dialog)
        layout.addWidget(self.view_user_button)

        # User Management Button
        self.manage_users_button = QPushButton("Manage Users")
        self.manage_users_button.clicked.connect(self.show_users)
        layout.addWidget(self.manage_users_button)

        # Role Management Button
        self.manage_roles_button = QPushButton("Manage Roles")
        self.manage_roles_button.clicked.connect(self.manage_roles)
        layout.addWidget(self.manage_roles_button)

        # Logout Button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)

        self.setLayout(layout)

    def open_user_select_dialog(self):
        users = self.user_manager.get_users()
        dialog = UserSelectDialog(users, self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_user_id is not None:
            self.show_user_details(dialog.selected_user_id)

    def show_user_details(self, user_id):
        user = next((u for u in self.user_manager.get_users() if u[0] == user_id), None)
        if user is not None:
            role_name = self.get_role_name(user[3])
            detail_dialog = UserDetailDialog(user_id, user[1], role_name, self)
            detail_dialog.exec_()
        else:
            QMessageBox.warning(self, "View User", "The selected user does not exist.")

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
                self.show_users()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not add user: {e}")
        else:
            QMessageBox.warning(self, "Error", "Invalid role selected.")


    def show_users(self):
        self.users_window = QWidget()
        self.users_window.setWindowTitle("Manage Users")
        self.users_window.setGeometry(150, 150, 500, 300)

        users_layout = QVBoxLayout()

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

        users_layout.addWidget(self.users_table)

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

        manage_roles_button = QPushButton("Manage Roles")
        manage_roles_button.clicked.connect(self.manage_roles)
        buttons_layout.addWidget(manage_roles_button)

        users_layout.addLayout(buttons_layout)
        self.users_window.setLayout(users_layout)
        self.users_window.show()

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
                self.show_users()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not update user: {e}")
        else:
            QMessageBox.warning(self, "Error", "Invalid role selected.")


    def get_role_name(self, role_id):
        role = self.role_manager.get_roles()
        for r in role:
            if r[0] == role_id:
                return r[1]
        return "Unknown"

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
            self.users_window.close()
            self.show_users()
        except Exception as e:
            QMessageBox.warning(self, "Delete User", f"Error: {str(e)}")

    def manage_roles(self):
        self.roles_window = QWidget()
        self.roles_window.setWindowTitle("Manage Roles")
        self.roles_window.setGeometry(150, 150, 400, 300)

        roles_layout = QVBoxLayout()

        self.roles_table = QTableWidget()
        self.roles_table.setColumnCount(2)
        self.roles_table.setHorizontalHeaderLabels(["ID", "Role Name"])

        roles = self.role_manager.get_roles()

        self.roles_table.setRowCount(len(roles))
        for row, role in enumerate(roles):
            self.roles_table.setItem(row, 0, QTableWidgetItem(str(role[0])))
            self.roles_table.setItem(row, 1, QTableWidgetItem(role[1]))

        roles_layout.addWidget(self.roles_table)

        buttons_layout = QHBoxLayout()

        add_role_button = QPushButton("Add Role")
        add_role_button.clicked.connect(self.add_role)
        buttons_layout.addWidget(add_role_button)

        delete_role_button = QPushButton("Delete Role")
        delete_role_button.clicked.connect(self.confirm_delete_role)
        buttons_layout.addWidget(delete_role_button)

        roles_layout.addLayout(buttons_layout)
        self.roles_window.setLayout(roles_layout)
        self.roles_window.show()

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
            self.manage_roles()
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
                        self.roles_window.close()
                        self.manage_roles()
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Could not delete role: {e}")
        else:
            QMessageBox.warning(self, "Delete Role", "Please select a role to delete.")


    def confirm_delete_role(self):
        selected = self.roles_table.currentRow()
        if selected >= 0:
            role_id = int(self.roles_table.item(selected, 0).text())
            role_name = self.roles_table.item(selected, 1).text()

            reply = QMessageBox.question(self, "Confirm Deletion",
                                        f"Are you sure you want to delete the role '{role_name}'?",
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    self.role_manager.delete_role(role_id)
                    QMessageBox.information(self, "Success", "Role deleted successfully.")
                    self.roles_window.close()
                    self.manage_roles()
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Could not delete role: {e}")
        else:
            QMessageBox.warning(self, "Delete Role", "Please select a role to delete.")


    def logout(self):
        self.user_manager.close_connection()
        self.role_manager.close_connection()
        self.close()
