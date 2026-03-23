from datetime import datetime, timezone


def test_analyze_requires_auth(client):
    res = client.post("/api/analyze", json={"text": "good"})
    assert res.status_code == 401


def test_analyze_requires_text(client, auth_header):
    res = client.post("/api/analyze", headers=auth_header, json={})
    assert res.status_code == 400


def test_analyze_saves_chat_and_returns_sentiment(client, auth_header):
    res = client.post("/api/analyze", headers=auth_header, json={"text": "good movie"})
    assert res.status_code == 200
    body = res.get_json()
    assert body["text"] == "good movie"
    assert body["sentiment"]["label"] == "Positive"


def test_history_returns_paginated_chats(client, app_module, auth_header):
    app_module.chats_collection.insert_one(
        {
            "user_id": "user-1",
            "text": "t1",
            "sentiment": {"label": "Neutral", "emoji": "😐"},
            "timestamp": datetime(2025, 1, 1, tzinfo=timezone.utc),
        }
    )
    app_module.chats_collection.insert_one(
        {
            "user_id": "user-1",
            "text": "t2",
            "sentiment": {"label": "Positive", "emoji": "😊"},
            "timestamp": datetime(2025, 1, 2, tzinfo=timezone.utc),
        }
    )

    res = client.get("/api/history?page=1&limit=1", headers=auth_header)
    assert res.status_code == 200
    body = res.get_json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["pages"] == 2
    assert len(body["chats"]) == 1
    assert body["chats"][0]["text"] == "t2"
