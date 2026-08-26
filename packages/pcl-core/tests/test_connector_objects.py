def test_connector_upsert_and_token(hub):
    cxa = hub.create_connector("google", "calendar")
    assert cxa["type"] == "connector_account"
    assert cxa["status"] == "pending_consent"
    hub.set_connector_token(cxa["id"], "tok")
    assert hub.get_connector_token(cxa["id"]) == "tok"
    item = {
        "id": "evt_test",
        "type": "event",
        "title": "Standup",
        "starts_at": "2026-08-21T10:00:00Z",
        "ends_at": "2026-08-21T10:30:00Z",
        "source_key": f"google:{cxa['id']}:abc",
        "classification": "private",
        "authority": "source_imported",
        "space_id": "personal",
        "owner": hub.person_id(),
        "labels": [],
        "created_at": cxa["created_at"],
        "updated_at": cxa["updated_at"],
        "source_refs": [cxa["id"]],
        "confidence": 1.0,
        "retention": {"mode": "until_revoked"},
        "policy_tags": [],
        "version": 1,
    }
    stored, action = hub.upsert_by_source_key(item)
    assert action == "created"
    again, action2 = hub.upsert_by_source_key({**item, "title": "Standup (moved)"})
    assert action2 == "updated"
    assert again["id"] == stored["id"]
    assert again["title"] == "Standup (moved)"
    summary = hub.apply_connector_items(cxa["id"], [], deleted_keys=[item["source_key"]])
    assert summary["tombstoned"] == 1


def test_apply_connector_items_batch(hub):
    cxa = hub.create_connector("google", "email")
    items = []
    for i in range(80):
        items.append(
            {
                "id": f"art_test_{i}",
                "type": "artifact",
                "kind": "email",
                "title": f"Msg {i}",
                "subject": f"Msg {i}",
                "body_text": ("lorem " * 400) + str(i),
                "source_key": f"google:{cxa['id']}:msg-{i}",
                "classification": "sensitive",
                "authority": "source_imported",
                "space_id": "personal",
                "owner": hub.person_id(),
                "labels": [],
                "created_at": cxa["created_at"],
                "updated_at": cxa["updated_at"],
                "source_refs": [cxa["id"]],
                "confidence": 1.0,
                "retention": {"mode": "until_revoked"},
                "policy_tags": [],
                "version": 1,
            }
        )
    summary = hub.apply_connector_items(cxa["id"], items)
    assert summary["outcome"] == "ok"
    assert summary["created"] == 80
    again = hub.apply_connector_items(cxa["id"], items)
    assert again["created"] == 0
    assert again["updated"] == 80


def test_disconnect_removes_connector_from_list(hub):
    cxa = hub.create_connector("google", "calendar")
    hub.set_connector_token(cxa["id"], "tok")
    hub.disconnect_connector(cxa["id"], purge=False)
    assert hub.get_connector_token(cxa["id"]) is None
    assert all(c["id"] != cxa["id"] for c in hub.list_connectors())
