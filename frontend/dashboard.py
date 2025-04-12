from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QPushButton,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import requests
from upvote import UpvoteWidget
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout
from profile_window import ProfileWindow



class DashboardWindow(QMainWindow):
    def __init__(self, token, user_id, login_window):
        super().__init__()
        self.token = token
        self.user_id = user_id
        self.login_window = login_window

        self.setWindowTitle("User Dashboard")
        self.setGeometry(200, 200, 1000, 700)
        

        central_widget = QWidget()
        main_layout = QVBoxLayout()
        layout = QVBoxLayout()

        # Welcome Label
        welcome = QLabel(f"Welcome, User ID: {user_id}")
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(welcome)

        # Embed ComplaintApp (which handles upvotes now)
        self.complaint_app = ComplaintApp(user_id, token)
        layout.addWidget(self.complaint_app)
 
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


        # Create Complaint Button (outside scroll area)
        self.create_button = QPushButton("➕ Create New Complaint")
        self.create_button.clicked.connect(self.create_complaint)
        main_layout.addWidget(self.create_button)

        # Scroll Area for Complaints
        self.complaint_app = ComplaintApp(user_id, token)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.complaint_app)
        main_layout.addWidget(self.scroll_area)

        main_layout.addWidget(QLabel("Your Complaints:"))
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        profile_button = QPushButton("👤 Profile")
        profile_button.clicked.connect(self.open_profile)
        main_layout.addWidget(profile_button)

    # def open_profile(self):
    #     self.profile_window = ProfileWindow(self.user_id, self.token)
    #     self.profile_window.show()
    def open_profile(self):
        self.profile_window = ProfileWindow(self.user_id, self.token, self, self.login_window)
        self.profile_window.show()

     

    def create_complaint(self):
        types = [
            'accommodation', 'mess', 'maintenance', 'safety', 'technical',
            'billing', 'noise', 'staff', 'general'
        ]

        complaint_type, ok = QInputDialog.getItem(
            self, "Select Complaint Type", "Type:", types, editable=False
        )
        if not ok or not complaint_type:
            return

        title, ok1 = QInputDialog.getText(self, "Create Complaint", "Enter complaint title:")
        if not ok1 or not title.strip():
            return

        description, ok2 = QInputDialog.getMultiLineText(self, "Create Complaint", "Enter complaint description:")
        if not ok2 or not description.strip():
            return

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
                self.complaint_app.reload_complaints()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create complaint.\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")


class ComplaintApp(QWidget):
    def __init__(self, user_id, token):
        super().__init__()
        self.user_id = user_id
        self.token = token

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_complaints()

    def reload_complaints(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
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

                if data:
                    for c in data:
                        complaint_layout = QVBoxLayout()

                        complaint_text = QLabel(f"📌 Title: {c['title']}\n📝 Description: {c['description']}\n📅 Created: {c['created_at']}")
                        complaint_text.setWordWrap(True)
                        complaint_text.setObjectName("complaintText")
                        complaint_layout.addWidget(complaint_text)

                        upvote_count_label = QLabel(f"👍 Total Upvotes: {c.get('total_upvotes', 0)}")
                        upvote_count_label.setObjectName("upvoteCount")
                        complaint_layout.addWidget(upvote_count_label)

                        upvote_widget = UpvoteWidget(
                            token=self.token,
                            complaint_id=c['id'],
                            already_upvoted=c.get('already_upvoted', False)
                        )
                        complaint_layout.addWidget(upvote_widget)

                        complaint_widget = QWidget()
                        complaint_widget.setObjectName("complaintBox")
                        complaint_widget.setLayout(complaint_layout)
                        complaint_widget.setStyleSheet(
                            "border: 1px solid gray; border-radius: 8px; padding: 10px; margin: 10px;"
                        )
                        self.layout.addWidget(complaint_widget)

                        self.layout.addWidget(QLabel(" "))
                else:
                    self.layout.addWidget(QLabel("No complaints found."))
            else:
                self.layout.addWidget(QLabel("❌ Failed to load complaints."))
        except Exception as e:
            self.layout.addWidget(QLabel("❌ Error occurred while loading complaints."))
            print("Error:", str(e))