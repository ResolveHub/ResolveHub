from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt
import requests
import sys


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(600, 500)
        self.setMinimumSize(600, 500)
        self.showMaximized()
        self.init_ui()

    def init_ui(self):
        self.emailLabel = QLabel("Email:")
        self.passwordLabel = QLabel("Password:")
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("Enter email")

        self.lineEdit_2 = QLineEdit()
        self.lineEdit_2.setPlaceholderText("Enter password")
        self.lineEdit_2.setEchoMode(QLineEdit.Password)

        self.loginButton = QPushButton("Login")
        self.pushButton_2 = QPushButton("Sign Up")
        self.forgotPasswordButton = QPushButton("Forgot Password?")

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.emailLabel)
        main_layout.addWidget(self.lineEdit)
        main_layout.addWidget(self.passwordLabel)
        main_layout.addWidget(self.lineEdit_2)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.loginButton)

        button_row = QHBoxLayout()
        button_row.addWidget(self.pushButton_2)
        button_row.addWidget(self.forgotPasswordButton)
        main_layout.addLayout(button_row)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.loginButton.clicked.connect(self.login)
        self.pushButton_2.clicked.connect(self.open_signup)
        self.forgotPasswordButton.clicked.connect(self.open_reset_password)

    def login(self):
        email = self.lineEdit.text()
        password = self.lineEdit_2.text()
        url = "http://127.0.0.1:8000/auth/login/"
        payload = {"email": email, "password": password}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            data = response.json()
            # print("Login response:", data)

            token = data.get("token") or data.get("key")  # Try both
            user_id = data.get("user_id")

            print("Login successful")

            email = self.lineEdit.text()

            if email.endswith("@admin.ac.in"):
                from admin_panel import AdminPanel
                self.admin_window = AdminPanel()
                self.admin_window.show()
            else:
                from dashboard import DashboardWindow
                self.dashboard_window = DashboardWindow(data["token"], data["user_id"] , self)
                self.dashboard_window.show()

            self.hide()

        else:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {"error": "Unexpected error or empty response from server."}
            print("Login failed:", error_data)

    def open_signup(self):
        from signup import SignupWindow
        self.signup_window = SignupWindow(self)
        self.signup_window.show()
        self.hide()

    def open_reset_password(self):
        from reset_password import ResetPasswordWindow
        self.reset_password_window = ResetPasswordWindow(self)
        self.reset_password_window.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Optional: apply QSS after testing
    with open("login.qss", "r") as file:
        app.setStyleSheet(file.read())

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
