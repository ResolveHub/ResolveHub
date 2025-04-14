import pytest
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel
from PyQt5.QtCore import Qt
from unittest.mock import Mock, patch
import sys
import os
from dashboard import ComplaintApp

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard import ComplaintApp, GENERATE_REPORT_URL

@pytest.fixture
def app(qtbot):
    test_app = ComplaintApp(user_id=1, token="test_token")
    qtbot.addWidget(test_app)
    return test_app

class TestDashboard:
    def test_load_complaints(self, app, qtbot):
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{
                'id': 1,
                'title': 'Test Complaint',
                'description': 'Test Description',
                'created_at': '2025-04-14',
                'status': 'Pending',
                'total_upvotes': 0
            }]
            mock_get.return_value = mock_response
            
            app.reload_complaints()
            assert app.complaints_container.count() > 0

    def test_create_complaint(self, app, qtbot):
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_post.return_value = mock_response
            
            # Simulate complaint creation
            app.title_input.setText("Test Title")
            app.description_input.setText("Test Description")
            qtbot.mouseClick(app.submit_button, Qt.LeftButton)
            
            assert mock_post.called

    def test_upvote_functionality(self, app, qtbot):
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            # Simulate upvote
            app.upvote_widget.upvote_button.click()
            assert mock_post.called

def test_init(app):
    """Test if the application initializes correctly"""
    assert app.user_id == 1
    assert app.token == "test_token"
    assert app.windowTitle() == "Complaint Management System"

@pytest.mark.parametrize("search_term,expected_count", [
    ("test", 2),
    ("nonexistent", 0),
])
def test_search_complaints(app, qtbot, search_term, expected_count):
    """Test complaint search functionality"""
    with patch('requests.get') as mock_get:
        # Mock response data with all required fields
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
        ] if search_term == "test" else []
        
        mock_get.return_value = mock_response

        # Clear existing complaints
        for i in reversed(range(app.complaints_container.count())):
            widget = app.complaints_container.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Type search term and press enter
        app.search_bar.setText(search_term)
        qtbot.keyClick(app.search_bar, Qt.Key_Return)

        # Wait for Qt to process events
        qtbot.wait(100)

        # Check if the correct number of complaints is displayed
        assert app.complaints_container.count() == expected_count

def test_download_report(app, qtbot):
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

        # Trigger download
        app.download_report(complaint_id=1)

        # Verify API call
        mock_get.assert_called_once_with(
            f"{GENERATE_REPORT_URL}1/",
            headers={"Authorization": "Bearer test_token"},
            timeout=30
        )

        # Verify file was opened for writing
        mock_open.assert_called_once_with("test_report.pdf", "wb")

def test_error_handling(app, qtbot):
    """Test error handling"""
    with patch('requests.get') as mock_get:
        # Mock failed response
        mock_get.side_effect = Exception("Network error")

        # Trigger load complaints
        app.load_complaints()

        # Verify error message is displayed
        widgets = [app.complaints_container.itemAt(i).widget() 
                  for i in range(app.complaints_container.count())]
        error_labels = [w for w in widgets if isinstance(w, QLabel) 
                       and "Error occurred" in w.text()]
        assert len(error_labels) > 0