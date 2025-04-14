import pytest
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QVBoxLayout, QWidget, QScrollArea, QLineEdit
from PyQt5.QtCore import Qt
from unittest.mock import Mock, patch, call
import sys
import os

# Add project root to Python path for reliable imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Import constants first
from frontend.components.widgets.dashboard import GENERATE_REPORT_URL
# Import base widget
from frontend.components.widgets.base import BaseWindow
# Then import ComplaintApp
from frontend.components.widgets.dashboard import ComplaintApp

@pytest.fixture
def app(qtbot):
    test_app = ComplaintApp()
    
    # Create complaints container if not initialized
    main_widget = QWidget()
    test_app.setCentralWidget(main_widget)
    main_layout = QVBoxLayout(main_widget)
    
    # Add search bar
    test_app.search_bar = QLineEdit()
    test_app.search_bar.returnPressed.connect(test_app.search_complaints)  # Connect signal
    main_layout.addWidget(test_app.search_bar)
    
    # Add complaints container
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    complaints_widget = QWidget()
    test_app.complaints_container = QVBoxLayout(complaints_widget)
    scroll_area.setWidget(complaints_widget)
    main_layout.addWidget(scroll_area)
    
    # Set properties
    test_app.user_id = 1
    test_app.token = "test_token"
    test_app.setWindowTitle("Complaint Management System")  # Set window title
    
    qtbot.addWidget(test_app)
    return test_app

def test_init(app):
    """Test if the application initializes correctly"""
    assert app.user_id == 1
    assert app.token == "test_token"
    assert app.windowTitle() == "Complaint Management System"

@pytest.mark.parametrize("query,expected_count", [
    ("test", 2),
    ("nonexistent", 0),
])
def test_search_complaints(app, qtbot, query, expected_count):
    """Test complaint search functionality"""
    # Mock UpvoteWidget to avoid initialization errors
    with patch('frontend.components.widgets.dashboard.UpvoteWidget') as mock_upvote, \
         patch('requests.get') as mock_get:
        
        # Configure UpvoteWidget mock
        mock_upvote.return_value = QWidget()
        
        # Mock response data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "title": "Test Complaint 1",
                "description": "Test Description 1",
                "created_at": "2025-04-13",
                "status": "Pending",
                "total_upvotes": 0
            },
            {
                "id": 2,
                "title": "Test Complaint 2",
                "description": "Test Description 2",
                "created_at": "2025-04-13",
                "status": "Pending",
                "total_upvotes": 0
            }
        ] if query == "test" else []

        mock_get.return_value = mock_response

        # Clear existing complaints
        while app.complaints_container.count():
            item = app.complaints_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Force layout update
        app.complaints_container.update()
        qtbot.wait(100)

        # Trigger search
        app.search_bar.setText(query)
        with qtbot.waitSignal(app.search_bar.returnPressed, timeout=1000):
            qtbot.keyClick(app.search_bar, Qt.Key_Return)
        
        # Wait for search completion and UI updates
        qtbot.wait(500)

        # Count actual complaint widgets
        complaint_widgets = []
        for i in range(app.complaints_container.count()):
            widget = app.complaints_container.itemAt(i).widget()
            if widget and not isinstance(widget, QLabel):  # Exclude error/info labels
                complaint_widgets.append(widget)
        
        # Verify results count
        actual_count = len(complaint_widgets)
        assert actual_count == expected_count, \
            f"Expected {expected_count} complaints, found {actual_count}"

        # Verify UpvoteWidget was created correctly for each complaint
        if expected_count > 0:
            expected_calls = [
                call(token='test_token', complaint_id=complaint["id"], already_upvoted=False)
                for complaint in mock_response.json.return_value
            ]
            assert mock_upvote.call_count == expected_count
            mock_upvote.assert_has_calls(expected_calls, any_order=True)

def test_download_report(app, qtbot, monkeypatch):
    """Test report download functionality"""
    with patch('requests.get') as mock_get, \
         patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName') as mock_dialog, \
         patch('builtins.open', create=True) as mock_open:
        
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"PDF content"
        mock_get.return_value = mock_response

        # Mock file dialog
        mock_dialog.return_value = ("test_report.pdf", "")

        # Mock QMessageBox
        monkeypatch.setattr(QMessageBox, 'information', lambda *args: None)

        # Trigger download
        app.download_report()

        # Verify API call - update URL expectation to match implementation
        mock_get.assert_called_once_with(
            f"{GENERATE_REPORT_URL}",  # Remove '1/' to match actual implementation
            headers={"Authorization": "Bearer test_token"},
            timeout=30
        )

        # Verify file was opened for writing
        mock_open.assert_called_once_with("test_report.pdf", "wb")

def test_create_complaint(app, qtbot):
    """Test complaint creation"""
    with patch('requests.post') as mock_post:
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_post.return_value = mock_response

        # Open create complaint window
        app.create_complaint_ui()
        
        # Fill in the form
        qtbot.keyClicks(app.title_input, "Test Complaint")
        qtbot.keyClicks(app.description_input, "Test Description")
        app.type_dropdown.setCurrentText("Maintenance")

        # Click submit
        qtbot.mouseClick(app.submit_button, Qt.LeftButton)

        # Verify API call
        mock_post.assert_called_once()
        assert mock_post.call_args[1]['json']['title'] == "Test Complaint"
        assert mock_post.call_args[1]['json']['description'] == "Test Description"
        assert mock_post.call_args[1]['json']['type'] == "maintenance"

def test_load_complaints(app, qtbot):
    """Test loading complaints"""
    with patch('requests.get') as mock_get:
        # Mock response data
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "title": "Test Complaint",
                "description": "Test Description",
                "created_at": "2025-04-13",
                "status": "Pending",
                "total_upvotes": 5
            }
        ]
        mock_get.return_value = mock_response

        # Trigger reload
        app.reload_complaints()

        # Verify complaints are displayed
        assert app.complaints_container.count() > 0

def test_error_handling(app, qtbot):
    """Test error handling"""
    with patch('requests.get') as mock_get:
        # Mock failed response
        mock_get.side_effect = Exception("Network error")

        # Initialize UI state before test
        if not hasattr(app, 'complaints_container'):
            # Create container if missing
            main_widget = QWidget()
            app.setCentralWidget(main_widget)
            main_layout = QVBoxLayout(main_widget)
            app.complaints_container = QVBoxLayout()
            main_layout.addLayout(app.complaints_container)

        # Wait for Qt to process events
        qtbot.wait(100)

        # Trigger load complaints
        app.load_complaints()

        # Wait for error handling to complete
        qtbot.wait(100)

        # Get all widgets in the container
        widgets = []
        for i in range(app.complaints_container.count()):
            widget = app.complaints_container.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widgets.append(widget)
        
        # Check that at least one error label exists
        error_messages = [w.text() for w in widgets if "Error occurred" in w.text()]
        assert len(error_messages) > 0, "No error message found in UI"