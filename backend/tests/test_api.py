TRANSCRIPT = (
    "[00:00] Alice: Welcome to the planning meeting.\n"
    "[00:05] Bob: I will send the report by Friday.\n"
    "[00:10] Alice: We need to review the budget next week.\n"
)


def _create(client, **over):
    payload = {
        "title": "Sprint Planning",
        "participants": [{"name": "Alice"}, {"name": "Bob"}],
        "tags": ["planning"],
        "transcript_text": TRANSCRIPT,
        "transcript_filename": "t.txt",
    }
    payload.update(over)
    r = client.post("/api/meetings", json=payload)
    assert r.status_code == 201, r.text
    return r.json()


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_create_generates_summary_and_actions(client):
    m = _create(client)
    assert len(m["segments"]) == 3
    assert m["summary"]["overview"]
    assert any("report" in a["text"].lower() for a in m["action_items"])
    assert m["topics"]


def test_get_and_list(client):
    m = _create(client)
    assert client.get(f"/api/meetings/{m['id']}").status_code == 200
    rows = client.get("/api/meetings").json()
    assert len(rows) == 1
    assert rows[0]["action_item_count"] >= 1


def test_filter_by_participant_and_search(client):
    _create(client, title="Alpha Meeting")
    assert len(client.get("/api/meetings?participant=Alice").json()) == 1
    assert len(client.get("/api/meetings?participant=Zoe").json()) == 0
    assert len(client.get("/api/meetings?search=Alpha").json()) == 1


def test_update_and_delete(client):
    m = _create(client)
    r = client.patch(f"/api/meetings/{m['id']}", json={"title": "Renamed"})
    assert r.json()["title"] == "Renamed"
    assert client.delete(f"/api/meetings/{m['id']}").status_code == 204
    assert client.get(f"/api/meetings/{m['id']}").status_code == 404


def test_action_item_crud(client):
    m = _create(client)
    r = client.post(f"/api/meetings/{m['id']}/action-items", json={"text": "Manual task"})
    item = r.json()
    assert r.status_code == 201
    r2 = client.patch(f"/api/action-items/{item['id']}", json={"completed": True})
    assert r2.json()["completed"] is True
    assert client.delete(f"/api/action-items/{item['id']}").status_code == 204


def test_transcript_reupload_via_form(client):
    m = _create(client, transcript_text=None)
    assert m["segments"] == []
    r = client.post(
        f"/api/meetings/{m['id']}/transcript",
        data={"content": TRANSCRIPT, "filename": "t.txt"},
    )
    assert r.status_code == 200
    assert len(r.json()["segments"]) == 3


def test_global_search(client):
    _create(client)
    r = client.get("/api/search?q=budget")
    body = r.json()
    assert body["count"] >= 1
    assert "budget" in body["hits"][0]["text"].lower()


def test_highlight_crud(client):
    m = _create(client)
    seg = m["segments"][0]
    r = client.post(
        f"/api/meetings/{m['id']}/highlights",
        json={
            "segment_id": seg["id"],
            "quote": seg["text"],
            "note": "Important point",
            "speaker": seg["speaker"],
            "start_ms": seg["start_ms"],
        },
    )
    assert r.status_code == 201, r.text
    hid = r.json()["id"]

    # Highlight shows up on the meeting detail.
    detail = client.get(f"/api/meetings/{m['id']}").json()
    assert len(detail["highlights"]) == 1
    assert detail["highlights"][0]["note"] == "Important point"

    # Update the note, then delete.
    r2 = client.patch(f"/api/highlights/{hid}", json={"note": "Edited"})
    assert r2.json()["note"] == "Edited"
    assert client.delete(f"/api/highlights/{hid}").status_code == 204
    detail2 = client.get(f"/api/meetings/{m['id']}").json()
    assert detail2["highlights"] == []


def test_ask_meeting_general(client):
    m = _create(client)
    r = client.post(f"/api/meetings/{m['id']}/ask", json={"question": "What about the budget?"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["citations"]
    assert "budget" in body["answer"].lower()


def test_ask_meeting_action_intent(client):
    m = _create(client)
    r = client.post(f"/api/meetings/{m['id']}/ask", json={"question": "What are the action items?"})
    body = r.json()
    # Even though "action items" isn't literally in the transcript, intent routing
    # returns the extracted action items.
    assert "action items" in body["answer"].lower()
    assert "report" in body["answer"].lower()
