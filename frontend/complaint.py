import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLineEdit, QLabel, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem
)

# Backend API URL (Change according to your Django server)
BASE_URL = "http://127.0.0.1:8000/complaints/"

class ComplaintApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Complaint Management System")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search complaints...")
        self.search_bar.returnPressed.connect(self.search_complaints)
        self.layout.addWidget(self.search_bar)

        # Complaint Table
        self.complaint_table = QTableWidget()
        self.complaint_table.setColumnCount(3)
        self.complaint_table.setHorizontalHeaderLabels(["ID", "Title", "Status"])
        self.layout.addWidget(self.complaint_table)

        # Buttons
        self.load_button = QPushButton("Load Complaints")
        self.load_button.clicked.connect(self.load_complaints)
        self.layout.addWidget(self.load_button)

        self.create_button = QPushButton("Create Complaint")
        self.create_button.clicked.connect(self.create_complaint_ui)
        self.layout.addWidget(self.create_button)

        self.load_complaints()

    def load_complaints(self):
        """Fetch complaints from Django backend"""
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            complaints = response.json()
            self.complaint_table.setRowCount(len(complaints))

            for row, complaint in enumerate(complaints):
                self.complaint_table.setItem(row, 0, QTableWidgetItem(str(complaint["id"])))
                self.complaint_table.setItem(row, 1, QTableWidgetItem(complaint["title"]))
                self.complaint_table.setItem(row, 2, QTableWidgetItem(complaint["status"]))
        else:
            print("Failed to load complaints")

    def search_complaints(self):
        """Search complaints by title"""
        query = self.search_bar.text()
        response = requests.get(BASE_URL + f"?q={query}")

        if response.status_code == 200:
            complaints = response.json()
            self.complaint_table.setRowCount(len(complaints))
            for row, complaint in enumerate(complaints):
                self.complaint_table.setItem(row, 0, QTableWidgetItem(str(complaint["id"])))
                self.complaint_table.setItem(row, 1, QTableWidgetItem(complaint["title"]))
                self.complaint_table.setItem(row, 2, QTableWidgetItem(complaint["status"]))

    def create_complaint_ui(self):
        """Show UI to create a new complaint"""
        self.create_window = QWidget()
        self.create_window.setWindowTitle("New Complaint")
        self.create_window.setGeometry(200, 200, 400, 300)

        layout = QVBoxLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter complaint title")
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe your issue")
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_input)

        self.type_dropdown = QComboBox()
        self.type_dropdown.addItems(["Accommodation", "Mess", "Maintenance", "Technical", "Billing"])
        layout.addWidget(QLabel("Complaint Type:"))
        layout.addWidget(self.type_dropdown)

        self.submit_button = QPushButton("Submit Complaint")
        self.submit_button.clicked.connect(self.submit_complaint)
        layout.addWidget(self.submit_button)

        self.create_window.setLayout(layout)
        self.create_window.show()

    def submit_complaint(self):
        """Send complaint data to Django API"""
        data = {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "type": self.type_dropdown.currentText(),
            "user": 1  # Example user ID, replace with authentication
        }

        response = requests.post(BASE_URL, json=data)
        if response.status_code == 201:
            print("Complaint submitted successfully.")
            self.create_window.close()
            self.load_complaints()
        else:
            print("Error submitting complaint")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ComplaintApp()
    window.show()
    sys.exit(app.exec_())
