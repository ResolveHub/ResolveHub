import sys
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
import requests

class SignupWindow(QMainWindow):
    def __init__(self, login_window):  
        super().__init__()
        uic.loadUi("signup.ui", self)

        self.login_window = login_window 
        self.pushButton.clicked.connect(self.signup)
        self.backButton.clicked.connect(self.open_login)

    def signup(self):
        email = self.lineEdit.text()
        username = self.lineEdit_2.text()
        password = self.lineEdit_3.text()
        response = requests.post("http://127.0.0.1:8000/auth/signup/", json={"email": email, "username": username, "password": password})
        print(response.json())

    def open_login(self):
        self.hide()  
        self.login_window.show() 
