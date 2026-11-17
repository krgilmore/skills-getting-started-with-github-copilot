from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def student_email():
    email = f"test-{uuid4().hex}@mergington.edu"
    yield email

    for activity in activities.values():
        if email in activity["participants"]:
            activity["participants"].remove(email)


def test_signup_adds_student_to_activity(client, student_email):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": student_email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {student_email} for Chess Club"
    }
    assert student_email in activities["Chess Club"]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client, student_email):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": student_email},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_invalid_email(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "not-an-email"},
    )

    assert response.status_code == 422


def test_signup_rejects_email_outside_school_domain(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student email must use the @mergington.edu domain"
    }


def test_signup_rejects_duplicate_student(client, student_email):
    activities["Chess Club"]["participants"].append(student_email)

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": student_email},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }


def test_unregister_removes_student_from_activity(client, student_email):
    activities["Chess Club"]["participants"].append(student_email)

    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": student_email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {student_email} from Chess Club"
    }
    assert student_email not in activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client, student_email):
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": student_email},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unenrolled_student(
    client, student_email
):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": student_email},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
