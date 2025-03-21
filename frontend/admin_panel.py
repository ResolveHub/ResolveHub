import sys
from PyQt5 import QtWidgets, uic
import sqlite3

class AdminPanel(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("admin_panel.ui", self)  # Load UI file

        # Button connections
        self.assign_button.clicked.connect(self.assign_authority)
        self.load_users()

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

# Run the application
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec_())
