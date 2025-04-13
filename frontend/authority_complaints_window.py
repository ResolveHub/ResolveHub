# authority_complaints_window.py

import requests
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QTextEdit, QScrollArea
)


class AuthorityComplaintWindow(QWidget):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setWindowTitle("🛠 Complaints Under Your Authority")
        self.setGeometry(200, 200, 700, 500)

        self.layout = QVBoxLayout()

        self.refresh_button = QPushButton("🔄 Refresh Complaints")
        self.refresh_button.clicked.connect(self.load_complaints)
        self.layout.addWidget(self.refresh_button)

        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        self.load_complaints()

    def load_complaints(self):
        url = "http://127.0.0.1:8000/complaint/api/complaints/under-you/"
        headers = {
            "Authorization": f"Bearer {self.token}"  # or "Token" based on your backend
        }

        # Clear old widgets
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                complaints = response.json()

                if not complaints:
                    self.scroll_layout.addWidget(QLabel("📭 No complaints assigned to you."))
                else:
                    for c in complaints:
                        complaint_box = QTextEdit()
                        complaint_box.setReadOnly(True)
                        complaint_box.setText(
                            f"📌 Title: {c.get('title', '')}\n"
                            f"📝 Description: {c.get('description', '')}\n"
                            f"📍 Location: {c.get('location', 'N/A')}\n"
                            f"🔄 Status: {c.get('status', '')}\n"
                            f"👍 Upvotes: {c.get('total_upvotes', 0)}"
                        )
                        self.scroll_layout.addWidget(complaint_box)
            else:
                QMessageBox.warning(self, "Error", f"Failed to load complaints. Status: {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
