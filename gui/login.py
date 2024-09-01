from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from database.user import UserManager
from gui.admin_dashboard import AdminDashboard
from gui.user_dashboard import UserDashboard

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 150)

        self.user_manager = UserManager()

        # Layout
        layout = QVBoxLayout()

        # Username
        self.username_label = QLabel("Username:")
        layout.addWidget(self.username_label)
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        # Password
        self.password_label = QLabel("Password:")
        layout.addWidget(self.password_label)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Authenticate the user
        user = self.user_manager.authenticate_user(username, password)

        if user:
            QMessageBox.information(self, "Login Success", f"Welcome, {username}!")
            self.redirect_to_dashboard(user)
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

    def redirect_to_dashboard(self, user):
        # Determine the user's role and redirect accordingly
        role_id = user[3]
        if role_id == 1:  # Assuming role_id 1 is Admin
            self.show_admin_dashboard(user)
        else:
            self.show_user_dashboard(user)

    def show_admin_dashboard(self, user):
        # Redirect to the Admin Dashboard
        self.close()
        self.admin_dashboard = AdminDashboard(user)
        self.admin_dashboard.show()

    def show_user_dashboard(self, user):
        # Close the login window
        self.close()
        # Open the User Dashboard window (implement this next)
        self.user_dashboard = UserDashboard(user)
        self.user_dashboard.show()

    def closeEvent(self, event):
        # Ensure the database connection is closed when the application exits
        self.user_manager.close_connection()
