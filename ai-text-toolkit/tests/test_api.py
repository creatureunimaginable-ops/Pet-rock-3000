CLIENT_ID = "test-client-1234"


def test_list_tools(client):
    res = client.get("/api/tools")
    assert res.status_code == 200
    data = res.json()
    assert {t["id"] for t in data["tools"]} == {"summarize", "rewrite", "captions"}
    assert data["demo_mode"] is True


def test_run_tool_and_credits(client):
    res = client.post(
        "/api/tools/summarize",
        json={"client_id": CLIENT_ID, "text": "Hello world. This is a test.", "options": {"length": "short"}},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["tool"] == "summarize"
    assert data["result"]
    assert data["credits_remaining"] == 4

    credits = client.get(f"/api/credits/{CLIENT_ID}").json()
    assert credits["credits_remaining"] == 4


def test_credit_limit_enforced(client):
    from app import config

    object.__setattr__(config.settings, "free_daily_credits", 1)
    try:
        first = client.post(
            "/api/tools/summarize",
            json={"client_id": CLIENT_ID, "text": "Hello world. This is a test."},
        )
        assert first.status_code == 200
        second = client.post(
            "/api/tools/summarize",
            json={"client_id": CLIENT_ID, "text": "Hello world. This is a test."},
        )
        assert second.status_code == 429
    finally:
        object.__setattr__(config.settings, "free_daily_credits", 5)


def test_unknown_tool_404(client):
    res = client.post("/api/tools/nope", json={"client_id": CLIENT_ID, "text": "hi"})
    assert res.status_code == 404


def test_validation_error(client):
    res = client.post("/api/tools/summarize", json={"client_id": "short", "text": ""})
    assert res.status_code == 422


def test_history(client):
    client.post(
        "/api/tools/rewrite",
        json={"client_id": CLIENT_ID, "text": "Some text here.", "options": {"tone": "casual"}},
    )
    res = client.get(f"/api/history/{CLIENT_ID}")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) >= 1
    assert items[0]["tool"] == "rewrite"


def test_index_served(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "AI Text Toolkit" in res.text
