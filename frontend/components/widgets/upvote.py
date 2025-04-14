from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
import requests
import json
class UpvoteWidget(QWidget):
  def send_upvote(self):
    headers = {
        "Authorization": f"Bearer {self.token}"
    }
    data = {
        "complaint_id": self.complaint_id
    }

    try:
        # Use the correct URL as defined in the backend
        response = requests.post("http://127.0.0.1:8000/complaint/api/complaints/upvote/", json=data, headers=headers)

        if response.status_code in [200, 201]:
            result = response.json()
            self.status_label.setText("✅ " + result.get("message", "Upvoted!"))
            self.upvote_button.setEnabled(False)
        else:
            self.status_label.setText("❌ Failed to upvote.")
            print("Error:", response.json())

    except Exception as e:
        self.status_label.setText("❌ Error occurred.")
        print("Exception:", str(e))
