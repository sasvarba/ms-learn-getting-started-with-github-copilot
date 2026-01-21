"""
Tests for the FastAPI activities endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_activities)
    yield


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_dict(self, client):
        """Test that /activities endpoint returns activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_chess_club(self, client):
        """Test that activities include Chess Club"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
    
    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
    
    def test_get_activities_participants_list(self, client):
        """Test that participants are in a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_data in data.values():
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client):
        """Test signup returns 404 for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_increases_participant_count(self, client):
        """Test that signup increases participant count"""
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client):
        """Test unregister returns 404 for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_registered(self, client):
        """Test unregister returns 400 for student not registered"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_decreases_participant_count(self, client):
        """Test that unregister decreases participant count"""
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
