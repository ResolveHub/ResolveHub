from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import Qt
import requests
from upvote import UpvoteWidget
from PyQt5.QtWidgets import QHBoxLayout

class DashboardWindow(QMainWindow):
    def __init__(self, token, user_id):
        super().__init__()
        self.token = token
        self.user_id = user_id

        self.setWindowTitle("User Dashboard")
        self.setGeometry(200, 200, 800, 600)

        layout = QVBoxLayout()
        welcome = QLabel(f"Welcome, User ID: {user_id}")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)

        # Embed ComplaintApp (which handles upvotes now)
        self.complaint_app = ComplaintApp(user_id, token)
        layout.addWidget(self.complaint_app)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QWidget, QPushButton,
    QInputDialog, QMessageBox
)
import requests
from upvote import UpvoteWidget


class ComplaintApp(QWidget):
    def __init__(self, user_id, token):
        super().__init__()
        self.user_id = user_id
        self.token = token

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Your Complaints:"))

        # 👉 Create Complaint Button
        create_button = QPushButton("➕ Create New Complaint")
        create_button.clicked.connect(self.create_complaint)
        self.layout.addWidget(create_button)

        self.load_complaints()

    def create_complaint(self):

        types = [
            'accommodation', 'mess', 'maintenance', 'safety', 'technical',
            'billing', 'noise', 'staff', 'general'
        ]
        type_display = {
            'accommodation': 'Accommodation',
            'mess': 'Mess & Food',
            'maintenance': 'Maintenance',
            'safety': 'Safety & Security',
            'technical': 'Technical',
            'billing': 'Billing & Payments',
            'noise': 'Noise & Disturbance',
            'staff': 'Staff Behavior',
            'general': 'General',
        }
        complaint_type, ok = QInputDialog.getItem(
            self, "Select Complaint Type", "Type:", types, editable=False
        )
        if not ok or not complaint_type:
            return

        # Step 1: Get title
        title, ok1 = QInputDialog.getText(self, "Create Complaint", "Enter complaint title:")
        if not ok1 or not title.strip():
            return

        # Step 2: Get description
        description, ok2 = QInputDialog.getMultiLineText(self, "Create Complaint", "Enter complaint description:")
        if not ok2 or not description.strip():
            return

        # Step 3: Send data to API
        url = "http://127.0.0.1:8000/complaint/api/complaints/create/"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {
            "title": title,
            "description": description,
            "created_by": self.user_id
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Complaint created successfully.")
                self.reload_complaints()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create complaint.\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def reload_complaints(self):
        # Clear existing widgets
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        self.layout.addWidget(QLabel("Your Complaints:"))

        # Re-add the create button
        create_button = QPushButton("➕ Create New Complaint")
        create_button.clicked.connect(self.create_complaint)
        self.layout.addWidget(create_button)

        # Load again
        self.load_complaints()

    def load_complaints(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            url = "http://127.0.0.1:8000/complaint/api/complaints/"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                print("Loaded complaints:", data)

                if data:
                    for c in data:
                        complaint_layout = QVBoxLayout()
                        complaint_text = QLabel(f"📌 Title: {c['title']}\n📝 Description: {c['description']}")
                        complaint_layout.addWidget(complaint_text)

                        upvote_count_label = QLabel(f"👍 Total Upvotes: {c.get('total_upvotes', 0)}")
                        complaint_layout.addWidget(upvote_count_label)

                        upvote_widget = UpvoteWidget(
                            token=self.token,
                            complaint_id=c['id'],
                            already_upvoted=c.get('already_upvoted', False)
                        )
                        complaint_layout.addWidget(upvote_widget)

                        complaint_widget = QWidget()
                        complaint_widget.setLayout(complaint_layout)
                        self.layout.addWidget(complaint_widget)

                        self.layout.addWidget(QLabel("—" * 80))
                else:
                    self.layout.addWidget(QLabel("No complaints found."))
            else:
                self.layout.addWidget(QLabel("❌ Failed to load complaints."))
                print(f"Status: {response.status_code}")
                print("Response:", response.text)

        except Exception as e:
            self.layout.addWidget(QLabel("❌ Error occurred while loading complaints."))
            print("Error:", str(e))