import sys
from PyQt5.QtWidgets import QApplication
from gui2.login import LoginWindow
from database.user import UserManager
from init import initialize_database

def main():
    # Initialize the database and populate initial data
    initialize_database()

    # Launch the application
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
