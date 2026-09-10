def test_setup_status_includes_encrypted_and_key_storage(client):
    status = client.get("/v1/setup")
    assert status.status_code == 200
    body = status.json()
    assert isinstance(body["encrypted"], bool)
    assert body["key_storage"] in {"keychain", "file"}
