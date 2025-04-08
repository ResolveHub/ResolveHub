import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog
import requests


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("login.ui", self)

        self.loginButton.clicked.connect(self.login)
        self.pushButton_2.clicked.connect(self.open_signup)  # Use correct button name
        self.forgotPasswordButton.clicked.connect(self.open_reset_password)  # ✅ Add this line

    def login(self):
        email = self.lineEdit.text()
        password = self.lineEdit_2.text()

        url = "http://127.0.0.1:8000/auth/login/"
        payload = {"email": email, "password": password}

        response = requests.post(url, json=payload)  # Send as JSON

        if response.status_code == 200:
            data = response.json()
            # print("Login response:", data)

            token = data.get("token") or data.get("key")  # Try both
            user_id = data.get("user_id")

            print("Login successful")

            from dashboard import DashboardWindow
            self.dashboard_window = DashboardWindow(token, user_id)
            self.dashboard_window.show()
            self.hide()
        else:
            print("Login failed:", response.json())


    def open_signup(self):
        from signup import SignupWindow
        self.signup_window = SignupWindow(self)  # Pass self as login window reference
        self.signup_window.show()
        self.hide()  # Hide login window instead of closing

    def open_reset_password(self):
        from reset_password import ResetPasswordWindow
        self.reset_password_window = ResetPasswordWindow(self)
        self.reset_password_window.show()
        self.hide()  # Hide login window
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())