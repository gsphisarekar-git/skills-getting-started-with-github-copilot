import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    orig = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(orig)


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data


def test_signup_and_reflects_in_activities():
    email = "tester@mergington.edu"
    activity = "Chess Club"
    url_activity = urllib.parse.quote(activity, safe="")
    resp = client.post(f"/activities/{url_activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # GET should also show the new participant
    resp2 = client.get("/activities")
    assert email in resp2.json()[activity]["participants"]


def test_signup_duplicate():
    # michael@mergington.edu is already signed up in initial data
    email = "michael@mergington.edu"
    activity = "Chess Club"
    url_activity = urllib.parse.quote(activity, safe="")
    resp = client.post(f"/activities/{url_activity}/signup", params={"email": email})
    assert resp.status_code == 400


def test_unregister():
    email = "temp@mergington.edu"
    activity = "Chess Club"
    url_activity = urllib.parse.quote(activity, safe="")

    # sign up first
    resp = client.post(f"/activities/{url_activity}/signup", params={"email": email})
    assert resp.status_code == 200

    # then unregister
    resp2 = client.delete(f"/activities/{url_activity}/unregister", params={"email": email})
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_missing():
    activity = "Chess Club"
    url_activity = urllib.parse.quote(activity, safe="")
    resp = client.delete(f"/activities/{url_activity}/unregister", params={"email": "nope@x"})
    assert resp.status_code == 404
