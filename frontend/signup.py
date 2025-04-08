import sys
import requests
from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFormLayout, QWidget,
    QApplication, QMessageBox  # ✅ Added QMessageBox
)
from PyQt5.QtCore import Qt


class SignupWindow(QMainWindow):
    def __init__(self, login_window=None):
        super().__init__()

        self.setWindowTitle("Sign Up")
        self.resize(900, 600)
        self.setMinimumSize(600, 500)
        self.showMaximized()

        with open("signup.qss", "r") as file:
            self.setStyleSheet(file.read())

        self.login_window = login_window

        # Widgets
        self.email_label = QLabel("Email")
        self.username_label = QLabel("Username")
        self.password_label = QLabel("Password")

        self.lineEdit = QLineEdit()
        self.lineEdit_2 = QLineEdit()
        self.lineEdit_3 = QLineEdit()
        self.lineEdit_3.setEchoMode(QLineEdit.Password)

        self.pushButton = QPushButton("Sign Up")
        self.backButton = QPushButton("Back to Login")

        # Signals
        self.pushButton.clicked.connect(self.signup)
        self.backButton.clicked.connect(self.open_login)

        # Layouts
        form_layout = QFormLayout()
        form_layout.addRow(self.email_label, self.lineEdit)
        form_layout.addRow(self.username_label, self.lineEdit_2)
        form_layout.addRow(self.password_label, self.lineEdit_3)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.pushButton)
        button_layout.addWidget(self.backButton)

        inner_layout = QVBoxLayout()
        inner_layout.addLayout(form_layout)
        inner_layout.addSpacing(20)
        inner_layout.addLayout(button_layout)

        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addLayout(inner_layout)
        center_layout.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addStretch()
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def signup(self):
        email = self.lineEdit.text()
        username = self.lineEdit_2.text()
        password = self.lineEdit_3.text()

        try:
            response = requests.post(
                "http://127.0.0.1:8000/auth/signup/",
                json={"email": email, "username": username, "password": password}
            )
            try:
                data = response.json()
            except Exception:
                QMessageBox.warning(self, "Error", "Invalid response from server.")
                return

            if response.status_code == 201:
                QMessageBox.information(self, "Success", data.get("message", "Account created successfully!"))
                self.open_login()
            else:
                QMessageBox.warning(self, "Signup Failed", data.get("error", "Signup failed. Try again."))

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Failed to connect to server:\n{str(e)}")

    def open_login(self):
        self.hide()
        if self.login_window:
            self.login_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SignupWindow()
    window.show()
    sys.exit(app.exec_())
