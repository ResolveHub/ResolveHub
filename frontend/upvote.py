from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
import requests
import json

class UpvoteWidget(QWidget):
    def __init__(self, token, complaint_id, already_upvoted=False, user_id=None):
        super().__init__()
        self.token = token
        self.complaint_id = complaint_id
        self.user_id = user_id  # Must be passed from parent!
        self.already_upvoted = already_upvoted

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.upvote_button = QPushButton("⬆️ Upvote")
        self.status_label = QLabel("✅" if already_upvoted else "")

        self.layout.addWidget(self.upvote_button)
        self.layout.addWidget(self.status_label)

        self.upvote_button.clicked.connect(self.send_upvote)

        if already_upvoted:
            self.upvote_button.setEnabled(False)


    def send_upvote(self):
        # print("Access Token:", self.token)
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        data = {
            "complaint_id": self.complaint_id
        }

        try:
            response = requests.post("http://127.0.0.1:8000/complaint/api/complaints/upvote/", json=data, headers=headers)

            if response.status_code in [200, 201]:
                result = response.json()
                self.status_label.setText("✅ " + result.get("message", "Upvoted!"))
                self.upvote_button.setEnabled(False)
                # print("Upvote Response:", result)
            else:
                self.status_label.setText("❌ Failed to upvote.")
                print("Error:", response.json())

        except Exception as e:
            self.status_label.setText("❌ Error occurred.")
            print("Exception:", str(e))


#ADD COMPLAINTS TO DB
# from complaints.models import Complaint
# >>> from django.contrib.auth import get_user_model
# >>> User = get_user_model()
# >>> user = User.objects.get(id=3)  
# >>> complaints = Complaint.objects.filter(user=user)
# >>> print(complaints)
# <QuerySet [<Complaint: sdvsvsplaint>]>
# >>> Complaint.objects.create(    user=user,    title="Sample Complaint",    description="Testing JWT protected complaints",   )
# <Complaint: Sample Complaint>
# >>>