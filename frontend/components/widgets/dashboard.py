from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QPushButton,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
import requests
from upvote import UpvoteWidget
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout
from profile_window import ProfileWindow
from complaint import ComplaintApp




class DashboardWindow(QMainWindow):
    def __init__(self, token, user_id, login_window):
        super().__init__()
        self.token = token
        self.user_id = user_id
        self.login_window = login_window

        self.setWindowTitle("User Dashboard")
        self.resize(600, 500)
        self.setMinimumSize(600, 500)
        self.showMaximized()
        

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

    def open_profile(self):
        self.profile_window = ProfileWindow(self.user_id, self.token, self, dashboard_window=self, login_window=self.login_window)
        self.profile_window.show()
     

    def create_complaint(self):
        types = [
            'Transport','Maintenance','Mess','Other'
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
            "complaint_type": complaint_type,
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



import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QMainWindow, QFileDialog
)
from PyQt5.QtCore import Qt


# Replace with your API URLs
BASE_URL = "http://127.0.0.1:8000/complaint/api/complaints/"
SEARCH_URL = "http://127.0.0.1:8000/complaint/api/search/"
CONFIRM_RESOLUTION_URL = "http://127.0.0.1:8000/complaint/api/confirm/"
GENERATE_REPORT_URL = "http://127.0.0.1:8000/complaint/api/report/"

from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QMessageBox
import requests

class UpvoteWidget(QWidget):
    def __init__(self, token, complaint_id, already_upvoted=False):
        super().__init__()
        self.token = token
        self.complaint_id = complaint_id
        self.already_upvoted = already_upvoted

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Add upvote button
        self.upvote_button = QPushButton("✅ Upvoted" if self.already_upvoted else "👍 Upvote")
        self.upvote_button.clicked.connect(self.toggle_upvote)
        self.layout.addWidget(self.upvote_button)

        # Add status label
        #self.status_label = QLabel("")
        #self.layout.addWidget(self.status_label)

    def toggle_upvote(self):
        if self.already_upvoted:
            # Ask for confirmation before removing upvote
            confirm = QMessageBox.question(
                self,
                "Remove Upvote",
                "Are you sure you want to remove your upvote?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.remove_upvote()
        else:
            self.add_upvote()

    def add_upvote(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "complaint_id": self.complaint_id
        }

        try:
            response = requests.post("http://127.0.0.1:8000/complaint/api/complaints/upvote/", json=data, headers=headers)

            if response.status_code in [200, 201]:
                self.already_upvoted = True
                self.upvote_button.setText("✅ Upvoted")
               # self.status_label.setText("✅ Upvoted successfully!")
            else:
                #self.status_label.setText("❌ Failed to upvote.")
                print("Error:", response.json())

        except Exception as e:
           # self.status_label.setText("❌ Error occurred.")
            print("Exception:", str(e))

    def remove_upvote(self):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "complaint_id": self.complaint_id
        }

        try:
            response = requests.post("http://127.0.0.1:8000/complaint/api/complaints/remove-upvote/", json=data, headers=headers)

            if response.status_code == 200:
                self.already_upvoted = False
                self.upvote_button.setText("👍 Upvote")
                #self.status_label.setText("✅ Upvote removed successfully!")
            else:
                #elf.status_label.setText("❌ Failed to remove upvote.")
                print("Error:", response.json())

        except Exception as e:
            #self.status_label.setText("❌ Error occurred.")
            print("Exception:", str(e))



class ComplaintApp(QMainWindow):
    def __init__(self, user_id, token):
        super().__init__()
        self.user_id = user_id
        self.token = token

        self.setWindowTitle("Complaint Management System")
        self.setGeometry(100, 100, 900, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search complaints...")
        self.search_bar.returnPressed.connect(self.search_complaints)
        self.layout.addWidget(self.search_bar)

        self.load_button = QPushButton("🔄 Load Complaints")
        self.load_button.clicked.connect(self.reload_complaints)
        self.layout.addWidget(self.load_button)

        # self.create_button = QPushButton("➕ Create Complaint")
        # self.create_button.clicked.connect(self.create_complaint_ui)
        # self.layout.addWidget(self.create_button)


        self.complaints_container = QVBoxLayout()
        self.layout.addLayout(self.complaints_container)

        self.load_complaints()

    def reload_complaints(self):
        for i in reversed(range(self.complaints_container.count())):
            widget = self.complaints_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.load_complaints()

    def load_complaints(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(BASE_URL, headers=headers)
            # response = requests.get("http://127.0.0.1:8000/complaint/api/complaints/", headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data:
                    for c in data:
                        self.display_complaint(c)
                else:
                    self.complaints_container.addWidget(QLabel("No complaints found."))
            else:
                self.complaints_container.addWidget(QLabel("❌ Failed to load complaints."))
        except Exception as e:
            self.complaints_container.addWidget(QLabel("❌ Error occurred while loading complaints."))
            print("Error:", str(e))

    def display_complaint(self, c):
        complaint_layout = QHBoxLayout()
        self.setGeometry(100, 100, 900, 700)

        complaint_text = QLabel(f"📌 Title: {c['title']}\n📝 Description: {c['description']}\n📅 Created: {c['created_at']} \n Status: {c['status']}")
        complaint_text.setWordWrap(True)
        complaint_layout.addWidget(complaint_text)

        # upvote_count_label = QLabel(f"👍 Total Upvotes: {c.get('total_upvotes', 0)}")
        # upvote_count_label.setStyleSheet("border: none; background: transparent; padding: 0; margin: 0;")
        # complaint_layout.addWidget(upvote_count_label)


        upvote_widget = UpvoteWidget(
            token=self.token,
            complaint_id=c['id'],
            already_upvoted=c.get('already_upvoted', False)
        )
        complaint_layout.addWidget(upvote_widget)



        # Add download button for each complaint
        buttons_layout = QHBoxLayout() 
        download_button = QPushButton("📥 Download Report")
        download_button.clicked.connect(lambda checked, cid=c['id']: self.download_report(cid))
        buttons_layout.addWidget(download_button)

        complaint_layout.addLayout(buttons_layout)

        complaint_widget = QWidget()
        complaint_widget.setLayout(complaint_layout)
        complaint_widget.setStyleSheet(
            "border: 1px solid gray; border-radius: 8px; padding: 10px; margin: 10px;"
        )
        self.complaints_container.addWidget(complaint_widget)

        if c["status"] == "Resolved" and c.get("user_confirmation_status") == "Pending":
            self.ask_user_confirmation(c)

    def search_complaints(self):
        query = self.search_bar.text().strip()
        if not query:
            QMessageBox.warning(self, "Search Error", "Please enter a search term.")
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(SEARCH_URL, params={"q": query}, headers=headers)

        for i in reversed(range(self.complaints_container.count())):
            widget = self.complaints_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if response.status_code == 200:
            complaints = response.json()
            print(complaints)
            if complaints:
                for complaint in complaints:
                    self.display_complaint(complaint)
            else:
                self.complaints_container.addWidget(QLabel("No matching complaints found."))
        else:
            QMessageBox.critical(self, "Search Failed", "Failed to search complaints.")

    def create_complaint_ui(self):
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
        data = {
            "title": self.title_input.text(),
            "description": self.description_input.toPlainText(),
            "type": self.type_dropdown.currentText().lower(),
            "user": self.user_id
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(BASE_URL, json=data, headers=headers)

        if response.status_code == 201:
            QMessageBox.information(self, "Success", "Complaint submitted successfully.")
            self.create_window.close()
            self.reload_complaints()
        else:
            QMessageBox.critical(self, "Error", "Error submitting complaint.")

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

    def download_report(self, complaint_id=None):
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save Report",
                "complaint_report.pdf",
                "PDF Files (*.pdf)"
            )
            if not filename:  # User cancelled
                return
                
            headers = {"Authorization": f"Bearer {self.token}"}
            url = f"{GENERATE_REPORT_URL}{complaint_id}/" if complaint_id else GENERATE_REPORT_URL
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                QMessageBox.information(self, "Report Downloaded", f"Report saved as {filename}")
            else:
                QMessageBox.critical(self, "Download Failed", f"Server returned status code: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Download Failed", f"Error: {str(e)}")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ComplaintApp(
        user_id=1,
        token="your_token_here"
    )
    window.show()
    sys.exit(app.exec_())