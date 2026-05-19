import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def restore_activities():
    """Arrange: preserve and restore the in-memory activities between tests."""
    original = copy.deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(copy.deepcopy(original))


def test_get_activities():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_for_activity():
    # Arrange
    client = TestClient(app)
    email = "test@example.com"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert email in body.get("message", "")
    assert email in activities[activity]["participants"]


def test_signup_duplicate_email():
    # Arrange
    client = TestClient(app)
    activity = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json().get("detail") == "Student already signed up for this activity"


def test_activity_not_found():
    # Arrange
    client = TestClient(app)
    activity = "Nonexistent"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": "noone@example.com"})

    # Assert
    assert response.status_code == 404


def test_remove_participant():
    # Arrange
    client = TestClient(app)
    activity = "Gym Class"
    email = "john@mergington.edu"
    assert email in activities[activity]["participants"]

    # Act
    response = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
