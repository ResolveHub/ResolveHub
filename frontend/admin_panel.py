import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import sqlite3
import requests

class AdminPanel(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("admin_panel.ui", self)  # Load UI file

        # Button connections
        self.assign_button.clicked.connect(self.assign_authority)
        self.load_users()

        self.delete_button.clicked.connect(self.delete_authority)


    def load_users(self):
        """ Load users from the database into the dropdown list. """
        conn = sqlite3.connect("../db.sqlite3")  # Adjust path if needed
        cursor = conn.cursor()
        cursor.execute("SELECT id, email FROM auth_app_user")  
        users = cursor.fetchall()
        conn.close()

        self.user_dropdown.clear()
        for user in users:
            self.user_dropdown.addItem(f"{user[1]} (ID: {user[0]})", user[0])

    def assign_authority(self):
        """ Assign authority to selected user. """
        user_id = self.user_dropdown.currentData()
        role = self.role_dropdown.currentText()
        priority = self.priority_spinbox.value()

        if not user_id:
            QtWidgets.QMessageBox.warning(self, "Error", "No user selected!")
            return

        conn = sqlite3.connect("../db.sqlite3")
        cursor = conn.cursor()

        # Check if the user already has an authority assigned
        cursor.execute("SELECT id FROM admin_panel_authority WHERE user_id=?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("UPDATE admin_panel_authority SET role=?, priority=? WHERE user_id=?", (role, priority, user_id))
        else:
            cursor.execute("INSERT INTO admin_panel_authority (user_id, role, priority) VALUES (?, ?, ?)", (user_id, role, priority))

        conn.commit()
        conn.close()

        QtWidgets.QMessageBox.information(self, "Success", "Authority assigned successfully!")


    def delete_authority(self):
        """ Delete authority for the selected user ID. """
        user_id = self.user_id_input.text().strip()

        if not user_id:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter a User ID!")
            return
        
        try:
            user_id = int(user_id)  # Convert to integer
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Error", "Invalid User ID format!")
            return


        conn = sqlite3.connect("../db.sqlite3")
        cursor = conn.cursor()

        # Check if the user has an assigned authority
        cursor.execute("SELECT id FROM admin_panel_authority WHERE user_id=?", (user_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("DELETE FROM admin_panel_authority WHERE user_id=?", (user_id,))
            conn.commit()
            QtWidgets.QMessageBox.information(self, "Success", "Authority deleted successfully!")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No authority found for the given User ID!")

        conn.close()


# Run the application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec_())
