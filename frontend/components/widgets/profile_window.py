from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget,
    QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget, QInputDialog, QMessageBox,  QScrollArea
import requests
from frontend.components.widgets.authority_complaints_window import AuthorityComplaintWindow

class ProfileWindow(QMainWindow):
    def __init__(self, user_id, token, is_authority=False, dashboard_window=None, login_window=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.token = token
        self.is_authority = is_authority
        self.dashboard_window = dashboard_window
        self.login_window = login_window
        self.showMaximized()

        self.setWindowTitle("👤 Your Profile")
        self.setGeometry(300, 300, 700, 500)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint & ~Qt.WindowMinimizeButtonHint)
        
         # Apply dark theme
        self.apply_dark_theme()

        # Main layout
        self.container = QWidget()
        self.layout = QVBoxLayout()

        # Tabs
        self.tabs = QTabWidget()
        try:
            self.tabs.addTab(UserComplaintsTab(user_id, token, allow_edit=True), "📝 My Complaints")
            self.tabs.addTab(UserComplaintsTab(user_id, token, upvoted=True), "👍 Upvoted")
        except Exception as e:
            print(f"[ERROR] Failed to load complaint tabs: {e}")
            self.tabs.addTab(QLabel("Error loading complaints."), "Error")

        self.layout.addWidget(self.tabs)

        # Authority section
        if self.is_authority:
            try:
                authority_button = QPushButton("🛠 Complaints Under You")
                authority_button.clicked.connect(self.open_authority_complaints)
                self.layout.addWidget(authority_button)
            except Exception as e:
                print(f"[ERROR] Failed to load authority section: {e}")
        self.layout.addWidget(self.tabs)

        # Logout Button
        logout_button = QPushButton("🚪 Logout")
        logout_button.clicked.connect(self.logout)
        self.layout.addWidget(logout_button)

        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

    def apply_dark_theme(self):
        try:
            with open("dark_theme.qss", "r") as file:
                self.setStyleSheet(file.read())
        except FileNotFoundError:
            print("Dark theme QSS file not found.")

    def logout(self):
        confirm = QMessageBox.question(self, "Logout", "Are you sure you want to logout?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            # Close the ProfileWindow
            self.close()

            # Close the DashboardWindow if it exists
            if self.dashboard_window:
                self.dashboard_window.close()

            # Show the LoginWindow if it exists
            if self.login_window:
                self.login_window.show()

    def open_authority_complaints(self):
        self.auth_window = AuthorityComplaintWindow(self.token)
        self.auth_window.show()


class UserComplaintsTab(QWidget):
   
    def __init__(self, user_id, token, allow_edit=False, upvoted=False):
        super().__init__()
        self.user_id = user_id
        self.token = token
        self.allow_edit = allow_edit

        self.upvoted = upvoted
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("🔍 Loading complaints..."))
        self.load_complaints()
    def load_complaints(self):
        self.setGeometry(100, 100, 900, 700)
        try:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }

            url = "http://127.0.0.1:8000/complaint/api/complaints/mine/" if not self.upvoted else "http://127.0.0.1:8000/complaint/api/complaints/upvoted/"
            response = requests.get(url, headers=headers)
            print("🔄 API Response Code:", response.status_code)
            print("🔄 API Response Body:", response.text)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            # scroll.setStyleSheet("background-color: #111; border: none;")
            container = QWidget()
            complaint_list_layout = QVBoxLayout(container)
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    for c in data:
                        complaint_layout = QVBoxLayout()
                        complaint_text = QLabel(f"📌 Title: {c['title']}\n📝 Description: {c['description']} \n Status: {c['status']}")
                        complaint_text.setWordWrap(True)
                        complaint_layout.addWidget(complaint_text)

                        upvote_count_label = QLabel(f"👍 Total Upvotes: {c.get('total_upvotes', 0)}")
                        complaint_layout.addWidget(upvote_count_label)

                        if self.allow_edit:
                            edit_button = QPushButton("✏️ Edit")
                            edit_button.clicked.connect(
                                lambda _, cid=c['id'], title=c['title'], desc=c['description']:
                                self.edit_complaint(cid, title, desc)
                            )
                            complaint_layout.addWidget(edit_button)

                            delete_button = QPushButton("🗑️ Delete")
                            delete_button.clicked.connect(
                                lambda _, cid=c['id']: self.delete_complaint(cid)
                            )
                            complaint_layout.addWidget(delete_button)

                        complaint_widget = QWidget()
                        complaint_widget.setLayout(complaint_layout)
                        complaint_list_layout.addWidget(complaint_widget)
                        complaint_list_layout.addWidget(QLabel("—" * 80))

                        separator = QLabel(" ")
                        separator.setFixedHeight(15)
                        complaint_list_layout.addWidget(separator)
                else:
                    self.layout.addWidget(QLabel("📭 No complaints found."))
            else:
                self.layout.addWidget(QLabel(f"❌ Failed to load complaints: {response.status_code}"))
            scroll.setWidget(container)
            self.layout.addWidget(scroll)
            
        except Exception as e:
            self.layout.addWidget(QLabel("❌ Error occurred while loading complaints."))
            print("Error:", str(e))

    def edit_complaint(self, complaint_id, old_title, old_description):
        new_title, ok1 = QInputDialog.getText(self, "Edit Complaint", "New Title:", text=old_title)
        if not ok1 or not new_title.strip():
            return

        new_description, ok2 = QInputDialog.getMultiLineText(self, "Edit Complaint", "New Description:", text=old_description)
        if not ok2 or not new_description.strip():
            return

        url = f"http://127.0.0.1:8000/complaint/api/complaints/{complaint_id}/update/"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {
            "title": new_title,
            "description": new_description
        }

        try:
            response = requests.put(url, json=data, headers=headers)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Complaint updated.")
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", f"Update failed.\n{response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def delete_complaint(self, complaint_id):
        confirm = QMessageBox.question(self, "Delete", "Are you sure you want to delete this complaint?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            url = f"http://127.0.0.1:8000/complaint/api/complaints/{complaint_id}/delete/"
            headers = {
                "Authorization": f"Bearer {self.token}"
            }

            try:
                response = requests.delete(url, headers=headers)
                if response.status_code == 204:
                    QMessageBox.information(self, "Deleted", "Complaint deleted successfully.")
                    self.refresh()
                else:
                    QMessageBox.warning(self, "Error", f"Delete failed.\n{response.text}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def refresh(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.load_complaints()
        
