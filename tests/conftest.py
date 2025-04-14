import pytest
from frontend.components.widgets.dashboard import ComplaintApp

@pytest.fixture
def app(qtbot):
    test_app = ComplaintApp()  # ← Only pass args supported by your class
    test_app.user_id = 1       # ← Set manually or use a setter method
    test_app.token = "test_token"
    qtbot.addWidget(test_app)
    return test_app

@pytest.fixture
def client(app):
    return app.test_client()