import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox,
    QVBoxLayout, QSpinBox, QPushButton, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Panel")
        self.setMinimumSize(600, 500)
        self.setStyleSheet(open("admin_panel.qss").read())  # Load the external .qss file

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        central_widget.setLayout(layout)

        # Font
        label_font = QFont("Segoe UI", 12)
        input_font = QFont("Segoe UI", 11)

        # Widgets
        self.label1 = QLabel("Select User:")
        self.label1.setFont(label_font)
        self.user_dropdown = QComboBox()
        self.user_dropdown.setFont(input_font)

        self.label2 = QLabel("Select Role:")
        self.label2.setFont(label_font)
        self.role_dropdown = QComboBox()
        self.role_dropdown.addItems(["Maintenance", "Transport", "Mess", "Other"])
        self.role_dropdown.setFont(input_font)

        self.label3 = QLabel("Set Priority:")
        self.label3.setFont(label_font)
        self.priority_spinbox = QSpinBox()
        self.priority_spinbox.setRange(0, 10)
        self.priority_spinbox.setFont(input_font)

        self.assign_button = QPushButton("Assign Authority")
        self.assign_button.setFont(label_font)

        self.label4 = QLabel("Enter User ID to Delete:")
        self.label4.setFont(label_font)
        self.user_id_input = QLineEdit()
        self.user_id_input.setFont(input_font)

        self.delete_button = QPushButton("Delete Authority")
        self.delete_button.setFont(label_font)

        # Add widgets to layout
        layout.addWidget(self.label1)
        layout.addWidget(self.user_dropdown)
        layout.addWidget(self.label2)
        layout.addWidget(self.role_dropdown)
        layout.addWidget(self.label3)
        layout.addWidget(self.priority_spinbox)
        layout.addWidget(self.assign_button)
        layout.addSpacing(20)
        layout.addWidget(self.label4)
        layout.addWidget(self.user_id_input)
        layout.addWidget(self.delete_button)

        # Connect buttons
        self.assign_button.clicked.connect(self.assign_authority)
        self.delete_button.clicked.connect(self.delete_authority)

        # Load users
        self.load_users()

    def load_users(self):
        conn = sqlite3.connect("../db.sqlite3")
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM auth_app_user")
        users = cursor.fetchall()
        conn.close()

        self.user_dropdown.clear()
        for user in users:
            self.user_dropdown.addItem(f"{user[1]} (ID: {user[0]})", user[0])

    def assign_authority(self):
        user_id = self.user_dropdown.currentData()
        role = self.role_dropdown.currentText()
        priority = self.priority_spinbox.value()

        if not user_id:
            QMessageBox.warning(self, "Error", "No user selected!")
            return

        conn = sqlite3.connect("../db.sqlite3")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM admin_panel_authority WHERE user_id=?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("UPDATE admin_panel_authority SET role=?, priority=? WHERE user_id=?", (role, priority, user_id))
        else:
            cursor.execute("INSERT INTO admin_panel_authority (user_id, role, priority) VALUES (?, ?, ?)", (user_id, role, priority))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Authority assigned successfully!")

    def delete_authority(self):
        user_id = self.user_id_input.text().strip()
        if not user_id:
            QMessageBox.warning(self, "Error", "Please enter a User ID!")
            return

        try:
            user_id = int(user_id)
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid User ID format!")
            return

        conn = sqlite3.connect("../db.sqlite3")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM admin_panel_authority WHERE user_id=?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("DELETE FROM admin_panel_authority WHERE user_id=?", (user_id,))
            conn.commit()
            QMessageBox.information(self, "Success", "Authority deleted successfully!")
        else:
            QMessageBox.warning(self, "Error", "No authority found for the given User ID!")

        conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec_())

