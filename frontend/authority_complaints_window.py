from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
import requests

class AuthorityComplaintWindow(QWidget):
    def __init__(self, token):
        super().__init__()
        self.setWindowTitle("📋 Complaints Under You")
        self.setGeometry(350, 350, 600, 400)

        self.token = token
        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        layout.addWidget(QLabel("🛠 Below are complaints assigned to you:"))
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self.load_complaints()

    def load_complaints(self):
        try:
            # Use GET request and pass the token in headers (standard way)
            response = requests.get(
                "http://127.0.0.1:8000/api/complaints/assigned/",
                headers={
                    "Authorization": f"Token {self.token}"
                }
            )

            print("Raw response:", response.text)  # Debug
            print("Status code:", response.status_code)  # Debug

            data = response.json()

            if "complaints" in data:
                for c in data["complaints"]:
                    item = QListWidgetItem(
                        f"🆔 {c['id']} - {c['title']} ({c['status']})\n"
                        f"By: {c['user']}\n{c['description']}"
                    )
                    self.list_widget.addItem(item)
            else:
                self.list_widget.addItem("❌ No complaints or unauthorized.")

        except Exception as e:
            self.list_widget.addItem(f"❌ Error fetching complaints: {e}")
