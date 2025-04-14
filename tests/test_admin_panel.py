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
        """Setup test environment"""
        # Mock QSS file reading
        mock_qss = """
        QWidget { background-color: #f0f0f0; }
        QPushButton { padding: 5px; }
        """
        
        # Mock database connection
        self.mock_db_patcher = patch('sqlite3.connect')
        self.mock_db = self.mock_db_patcher.start()
        self.mock_cursor = MagicMock()
        self.mock_db.return_value.cursor.return_value = self.mock_cursor
        
        # Mock initial user data
        self.mock_cursor.fetchall.return_value = [
            (1, "test@example.com"),
            (2, "admin@example.com")
        ]
        
        # Setup panel with mocks
        with patch('builtins.open', mock_open(read_data=mock_qss)):
            self.panel = AdminPanel()
            qtbot.addWidget(self.panel)
        
        # Reset mock cursor after initialization
        self.mock_cursor.reset_mock()
        
        yield
        
        # Cleanup
        self.mock_db_patcher.stop()
        self.panel.close()

    def test_assign_authority(self, qtbot, monkeypatch):
        """Test assigning authority to a user"""
        # Mock successful authority assignment
        self.mock_cursor.fetchone.return_value = None  # No existing authority
        monkeypatch.setattr(QMessageBox, 'information', lambda *args: None)

        # Set UI values
        self.panel.user_dropdown.setCurrentIndex(0)  # First user
        self.panel.role_dropdown.setCurrentIndex(0)  # First role
        self.panel.priority_spinbox.setValue(5)

        # Click assign button
        qtbot.mouseClick(self.panel.assign_button, Qt.LeftButton)

        # Verify database interaction
        self.mock_cursor.execute.assert_called_with(
            "INSERT INTO admin_panel_authority (user_id, role, priority) VALUES (?, ?, ?)",
            (1, "Maintenance", 5)
        )

    def test_assign_authority_invalid_user(self, qtbot, monkeypatch):
        """Test assigning authority with invalid user selection"""
        # Reset mock cursor and setup warning
        self.mock_cursor.reset_mock()
        warning_shown = False
        def mock_warning(*args):
            nonlocal warning_shown
            warning_shown = True
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)

        # Clear user dropdown and try to assign
        self.panel.user_dropdown.clear()
        qtbot.mouseClick(self.panel.assign_button, Qt.LeftButton)

        # Verify warning shown and no DB operations
        assert warning_shown
        assert not self.mock_cursor.execute.called

    def test_delete_authority(self, qtbot, monkeypatch):
        """Test deleting an existing authority"""
        # Mock existing authority
        self.mock_cursor.fetchone.return_value = (1,)
        monkeypatch.setattr(QMessageBox, 'information', lambda *args: None)

        # Set user ID and delete
        self.panel.user_id_input.setText("1")
        qtbot.mouseClick(self.panel.delete_button, Qt.LeftButton)

        # Verify database interaction
        self.mock_cursor.execute.assert_called_with(
            "DELETE FROM admin_panel_authority WHERE user_id=?",
            (1,)
        )

    def test_delete_authority_nonexistent(self, qtbot, monkeypatch):
        """Test deleting a nonexistent authority"""
        # Reset mock cursor and setup responses
        self.mock_cursor.reset_mock()
        self.mock_cursor.fetchone.return_value = None
        
        # Setup warning mock
        warning_shown = False
        def mock_warning(*args):
            nonlocal warning_shown
            warning_shown = True
        monkeypatch.setattr(QMessageBox, 'warning', mock_warning)

        # Attempt to delete nonexistent authority
        self.panel.user_id_input.setText("999")
        qtbot.mouseClick(self.panel.delete_button, Qt.LeftButton)

        # Verify warning shown and correct DB query
        assert warning_shown
        self.mock_cursor.execute.assert_called_once_with(
            "SELECT id FROM admin_panel_authority WHERE user_id=?", 
            (999,)
        )
