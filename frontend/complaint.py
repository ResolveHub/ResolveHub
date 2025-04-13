import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, 
    QLineEdit, QLabel, QComboBox, QTextEdit, QTableWidget, QTableWidgetItem
)
from PyQt5.QtWidgets import QMessageBox

# Backend API URL (Change according to your Django server)
BASE_URL = "http://127.0.0.1:8000/complaints/"
SEARCH_URL = "http://127.0.0.1:8000/complaints/search/"
CONFIRM_RESOLUTION_URL = "http://127.0.0.1:8000/api/confirm_resolution"


class ComplaintApp(QMainWindow):
    def __init__(self, user_id, token):
        super().__init__()
        self.user_id = user_id
        self.token = token


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
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        response = requests.get(BASE_URL, headers=headers)

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
        """Search complaints by title, description, or ID (trace)"""

        # Check if trace input has text; if not, use search bar
        query = self.search_bar.text().strip()

        if not query:
            QMessageBox.warning(self, "Search Error", "Please enter a search term.")
            return

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        # Send search query to backend
        response = requests.get(SEARCH_URL, params={"q": query}, headers=headers)

        if response.status_code == 200:
            complaints = response.json()
            self.complaint_table.setRowCount(len(complaints))
            for row, complaint in enumerate(complaints):
                self.complaint_table.setItem(row, 0, QTableWidgetItem(str(complaint["id"])))
                self.complaint_table.setItem(row, 1, QTableWidgetItem(complaint["title"]))
                self.complaint_table.setItem(row, 2, QTableWidgetItem(complaint["status"]))
                # ✅ Ask user to confirm resolution if needed
                if complaint["status"] == "Resolved" and complaint.get("user_confirmation_status") == "Pending":
                       self.ask_user_confirmation(complaint)
        else: 
            QMessageBox.critical(self, "Search Failed", "Failed to search complaints.")

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
        self.type_dropdown.addItems(["Transport", "Mess", "Maintenance", "Other"])
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
            "type": self.type_dropdown.currentText().lower(),
            "user": self.user_id # Example user ID, replace with authentication
        }
        headers = {}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"

        response = requests.post(BASE_URL, json=data, headers=headers)

        if response.status_code == 201:
            print("Complaint submitted successfully.")
            self.create_window.close()
            self.load_complaints()
        else:
            print("Error submitting complaint:", response.json())

    def ask_user_confirmation(self, complaint):
        reply = QMessageBox.question(
            self,
            "Confirm Resolution",
            f"Your complaint titled \"{complaint['title']}\" has been marked as resolved.\n\nIs the issue actually resolved?",
            QMessageBox.Yes | QMessageBox.No
        )

        confirmation = "Confirmed" if reply == QMessageBox.Yes else "Rejected"

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            CONFIRM_RESOLUTION_URL,
            json={"complaint_id": complaint["id"], "confirmation": confirmation},
            headers=headers
        )

        if response.status_code == 200:
            QMessageBox.information(self, "Thank you", "Your response has been recorded.")
        else:
            QMessageBox.critical(self, "Error", "Failed to submit your confirmation.")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # TEMP VALUES JUST FOR TESTING
    window = ComplaintApp(user_id=1, token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQzODQ1NDUxLCJpYXQiOjE3NDM4NDUxNTEsImp0aSI6ImY1MjNjMDYzZTQ1MjQwYTI5MTQzYjRhYmRlYTUxZDc2IiwidXNlcl9pZCI6NH0.Tom_do9rzuRihfBs6fcSJwvmwW2GEg_x5u7l90dwzb8")  
    window.show()
    sys.exit(app.exec_())
