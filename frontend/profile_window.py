from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTabWidget, QInputDialog, QMessageBox
import requests
import authority_complaints_window as  AuthorityComplaintWindow

# class ProfileWindow(QMainWindow):
#     def __init__(self, user_id, token):
#         super().__init__()
#         self.user_id = user_id
#         self.token = token
#         self.setWindowTitle("👤 Your Profile")
#         self.setGeometry(300, 300, 700, 500)

#         tabs = QTabWidget()
#         tabs.addTab(UserComplaintsTab(user_id, token, allow_edit=True), "📝 My Complaints")
#         tabs.addTab(UserComplaintsTab(user_id, token, upvoted=True), "👍 Upvoted")

#         container = QWidget()
#         layout = QVBoxLayout()
#         layout.addWidget(tabs)
#         container.setLayout(layout)
#         self.setCentralWidget(container)

class ProfileWindow(QMainWindow):
    def __init__(self, user_id, token, is_authority=True):  # made optional
        super().__init__()
        self.user_id = user_id
        self.token = token
        self.setWindowTitle("👤 Your Profile")
        self.setGeometry(300, 300, 700, 500)

        tabs = QTabWidget()
        tabs.addTab(UserComplaintsTab(user_id, token, allow_edit=True), "📝 My Complaints")
        tabs.addTab(UserComplaintsTab(user_id, token, upvoted=True), "👍 Upvoted")

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(tabs)

        if is_authority:  # this part stays
            authority_button = QPushButton("🛠 Complaints Under You")
            authority_button.clicked.connect(self.open_authority_complaints)
            layout.addWidget(authority_button)

        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_authority_complaints(self):
        self.auth_window = AuthorityComplaintWindow.AuthorityComplaintWindow(self.token)
        self.auth_window.show()





class UserComplaintsTab(QWidget):
    def __init__(self, user_id, token, upvoted=False, allow_edit=False):
        super().__init__()
        self.user_id = user_id
        self.token = token
        self.upvoted = upvoted
        self.allow_edit = allow_edit

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.load_complaints()

    def load_complaints(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }

            if self.upvoted:
                url = "http://127.0.0.1:8000/complaint/api/complaints/upvoted/"
            else:
                url = "http://127.0.0.1:8000/complaint/api/complaints/mine/"

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()

                if data:
                    for c in data:
                        complaint_layout = QVBoxLayout()
                        complaint_text = QLabel(f"📌 Title: {c['title']}\n📝 Description: {c['description']}")
                        complaint_layout.addWidget(complaint_text)

                        upvote_count_label = QLabel(f"👍 Total Upvotes: {c.get('total_upvotes', 0)}")
                        complaint_layout.addWidget(upvote_count_label)

                        if self.allow_edit:
                            edit_button = QPushButton("✏️ Edit")
                            edit_button.clicked.connect(lambda _, cid=c['id'], title=c['title'], desc=c['description']: self.edit_complaint(cid, title, desc))
                            complaint_layout.addWidget(edit_button)

                            delete_button = QPushButton("🗑️ Delete")
                            delete_button.clicked.connect(lambda _, cid=c['id']: self.delete_complaint(cid))
                            complaint_layout.addWidget(delete_button)

                        complaint_widget = QWidget()
                        complaint_widget.setLayout(complaint_layout)
                        self.layout.addWidget(complaint_widget)
                        self.layout.addWidget(QLabel("—" * 80))
                else:
                    self.layout.addWidget(QLabel("No complaints found."))
            else:
                self.layout.addWidget(QLabel("❌ Failed to load complaints."))

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
