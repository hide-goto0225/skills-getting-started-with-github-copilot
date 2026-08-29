from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    activities.clear()
    activities.update(deepcopy(original))
    yield
    activities.clear()
    activities.update(deepcopy(original))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_student(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{quote(activity_name)}/signup?email={email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_student(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{quote(activity_name)}/signup?email={email}")

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up for this activity"}


def test_signup_with_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Club/signup?email=test@mergington.edu")

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_student_from_activity(client):
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"

    response = client.post(f"/activities/{quote(activity_name)}/remove?email={email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]
