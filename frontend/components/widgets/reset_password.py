import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
import requests

class ResetPasswordWindow(QMainWindow):
    def __init__(self, login_window=None): 
        super().__init__()
        uic.loadUi("reset_password.ui", self)

        self.login_window = login_window  
        self.sendOtpButton.clicked.connect(self.send_otp)
        self.resetPasswordButton.clicked.connect(self.reset_password)
        self.backButton.clicked.connect(self.open_login)

    def send_otp(self):
        email = self.emailInput.text()
        try:
            response = requests.post("http://127.0.0.1:8000/auth/forgot-password/", json={"email": email})
        
            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError:
                QMessageBox.warning(self, "Error", "Invalid response from server.")
                return

            if response.status_code == 200:
                QMessageBox.information(self, "Success", data.get("message", "OTP sent successfully."))
            else:
                QMessageBox.warning(self, "Error", data.get("error", "Unknown error occurred."))

        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Network Error", f"Failed to connect to server:\n{str(e)}")

    def reset_password(self):
        email = self.emailInput.text()
        otp = self.otpInput.text()
        new_password = self.newPasswordInput.text()

        response = requests.post("http://127.0.0.1:8000/auth/reset-password/", 
                                 json={"email": email, "otp": otp, "new_password": new_password})
        data = response.json()
        if response.status_code == 200:
            QMessageBox.information(self, "Success", data["message"])
            self.open_login()  # Go back to login
        else:
            QMessageBox.warning(self, "Error", data["error"])

    def open_login(self):
      
        from frontend.components.widgets.login import LoginWindow  
        self.login_window = LoginWindow()  
        self.login_window.show()
        self.close() 


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResetPasswordWindow() 
    window.show()
    sys.exit(app.exec_())