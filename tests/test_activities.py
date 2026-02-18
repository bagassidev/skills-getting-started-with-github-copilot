import pytest
from fastapi.testclient import TestClient


def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    activities = response.json()
    assert isinstance(activities, dict)
    assert len(activities) > 0

    # Check that each activity has the required fields
    for name, details in activities.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity_success(client: TestClient):
    """Test successful signup for an activity"""
    # Use an activity that exists and an email that's not already signed up
    response = client.post("/activities/Basketball/signup?email=test@example.com")
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert "Signed up test@example.com for Basketball" in result["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Basketball"]["participants"]


def test_signup_for_nonexistent_activity(client: TestClient):
    """Test signup for an activity that doesn't exist"""
    response = client.post("/activities/NonExistent/signup?email=test@example.com")
    assert response.status_code == 404

    result = response.json()
    assert "detail" in result
    assert result["detail"] == "Activity not found"


def test_signup_duplicate_participant(client: TestClient):
    """Test signup when student is already signed up"""
    # First signup
    client.post("/activities/Basketball/signup?email=duplicate@example.com")

    # Try to signup again
    response = client.post("/activities/Basketball/signup?email=duplicate@example.com")
    assert response.status_code == 400

    result = response.json()
    assert "detail" in result
    assert result["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_success(client: TestClient):
    """Test successful unregistration from an activity"""
    # First signup
    client.post("/activities/Soccer/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Soccer/unregister?email=unregister@example.com")
    assert response.status_code == 200

    result = response.json()
    assert "message" in result
    assert "Unregistered unregister@example.com from Soccer" in result["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "unregister@example.com" not in activities["Soccer"]["participants"]


def test_unregister_from_nonexistent_activity(client: TestClient):
    """Test unregistration from an activity that doesn't exist"""
    response = client.delete("/activities/NonExistent/unregister?email=test@example.com")
    assert response.status_code == 404

    result = response.json()
    assert "detail" in result
    assert result["detail"] == "Activity not found"


def test_unregister_non_participant(client: TestClient):
    """Test unregistration when student is not signed up"""
    response = client.delete("/activities/Basketball/unregister?email=notsignedup@example.com")
    assert response.status_code == 400

    result = response.json()
    assert "detail" in result
    assert result["detail"] == "Student is not signed up for this activity"


def test_root_redirect(client: TestClient):
    """Test root endpoint redirects to static index.html"""
    response = client.get("/")
    assert response.status_code == 200
    # FastAPI TestClient follows redirects by default, so we should get the HTML content
    assert "Mergington High School" in response.text