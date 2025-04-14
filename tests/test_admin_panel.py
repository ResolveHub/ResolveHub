import pytest
from unittest.mock import patch, MagicMock, mock_open
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from frontend.components.widgets.admin_panel import AdminPanel

# --------------------- Frontend (PyQt5) Tests --------------------- #

class TestAdminPanelFrontend:
    @pytest.fixture(autouse=True)
    def setup_panel(self, qtbot):
        # Mock the QSS file reading to simulate UI styles
        mock_qss = """
        QWidget {
            background-color: #f0f0f0;
        }
        QPushButton {
            padding: 5px;
        }
        """
        with patch('builtins.open', mock_open(read_data=mock_qss)):
            # Setup AdminPanel widget
            self.panel = AdminPanel()
            qtbot.addWidget(self.panel)

            # Mock DB connection
            self.mock_db_patcher = patch('C:\Work\Projects\SE\ResolveHub\db.sqlite3.connect')
            self.mock_db = self.mock_db_patcher.start()
            self.mock_cursor = MagicMock()
            self.mock_db.return_value.cursor.return_value = self.mock_cursor

            # Mock current user ID from dropdown
            self.panel.user_dropdown.currentData = lambda: 1  # Mock returning user ID '1'

            yield

            self.mock_db_patcher.stop()
            self.panel.close()

    def test_assign_authority(self, qtbot, monkeypatch):
        # Simulate user interaction with the "assign authority" form
        self.mock_cursor.fetchone.return_value = None  # Simulate no existing authority
        monkeypatch.setattr(QMessageBox, 'information', lambda *args: None)  # Mock info box

        # Set dropdown and spinbox values for role and priority
        self.panel.role_dropdown.setCurrentIndex(0)  # Assuming index 0 corresponds to "Maintenance"
        self.panel.priority_spinbox.setValue(5)

        # Simulate clicking the "Assign Authority" button
        qtbot.mouseClick(self.panel.assign_button, Qt.LeftButton)

        # Assert that the INSERT query is executed with the expected parameters
        self.mock_cursor.execute.assert_any_call(
            "INSERT INTO admin_panel_authority (user_id, role, priority) VALUES (?, ?, ?)",
            (1, "Maintenance", 5)
        )

    def test_assign_authority_invalid_user(self, qtbot, monkeypatch):
        # Simulate user interaction with invalid user selection
        self.panel.user_dropdown.clear()  # Clear the dropdown (no user selected)
        warning_shown = False

        # Mock warning message when no user is selected
        def mock_warning(*args):
            nonlocal warning_shown
            warning_shown = True

        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)

        # Simulate clicking the "Assign Authority" button
        qtbot.mouseClick(self.panel.assign_button, Qt.LeftButton)

        # Check that the warning was shown and no database query was executed
        assert warning_shown
        self.mock_cursor.execute.assert_not_called()

    def test_delete_authority(self, qtbot, monkeypatch):
        # Simulate deleting authority for an existing user
        self.mock_cursor.fetchone.return_value = (1,)  # Simulate authority exists
        monkeypatch.setattr(QMessageBox, 'information', lambda *args: None)  # Mock info box

        # Set the user ID input to '1'
        self.panel.user_id_input.setText("1")
        qtbot.mouseClick(self.panel.delete_button, Qt.LeftButton)

        # Assert that the DELETE query is executed with the expected user ID
        self.mock_cursor.execute.assert_any_call(
            "DELETE FROM admin_panel_authority WHERE user_id=?",
            (1,)
        )

    def test_delete_authority_nonexistent(self, qtbot, monkeypatch):
        # Simulate deleting authority for a nonexistent user
        self.mock_cursor.fetchone.return_value = None  # Simulate no authority found
        warning_shown = False

        # Mock warning message when no authority is found
        def mock_warning(*args):
            nonlocal warning_shown
            warning_shown = True

        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)

        # Set the user ID input to '999' (nonexistent user)
        self.panel.user_id_input.setText("999")
        qtbot.mouseClick(self.panel.delete_button, Qt.LeftButton)

        # Check that the warning was shown and the correct SELECT query was executed
        assert warning_shown
        self.mock_cursor.execute.assert_called_once()  # Ensure SELECT query was called
        assert "SELECT" in self.mock_cursor.execute.call_args[0][0]
