"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert data["data"]["app_name"] == "AI Meeting Action-Item Extractor"


def test_meeting_lifecycle_and_extraction():
    # 1. Create meeting
    create_payload = {
        "title": "API Test Sync",
        "meeting_type": "Stand-up",
        "transcript_text": "Priya: Arun, please prepare the client demo by Friday.\nArun: Sure, I will prepare it.",
    }
    create_res = client.post("/meetings", json=create_payload)
    assert create_res.status_code == 201
    meeting_id = create_res.json()["data"]["meeting_id"]

    # 2. Process meeting action items
    process_res = client.post(f"/meetings/{meeting_id}/process?provider=mock")
    assert process_res.status_code == 200
    p_data = process_res.json()["data"]
    assert p_data["action_items_count"] >= 1

    # 3. Retrieve meeting action items
    items_res = client.get(f"/meetings/{meeting_id}/action-items")
    assert items_res.status_code == 200
    items = items_res.json()["data"]
    assert len(items) >= 1
    task_id = items[0]["task_id"]

    # 4. Review approval
    approve_res = client.post(f"/action-items/{task_id}/approve?note=LGTM")
    assert approve_res.status_code == 200
    assert approve_res.json()["data"]["review_status"] == "approved"

    # 5. Clean up
    del_res = client.delete(f"/meetings/{meeting_id}")
    assert del_res.status_code == 200
