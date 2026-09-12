import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pcl_core.errors import IntegrityMismatch
from pcl_core.service import Hub
from pcl_server.marketplace.catalog import refresh_catalog, verify_catalog
from pcl_server.sync import http as sync_http


def _key_and_catalog(withdrawn=None):
    key = Ed25519PrivateKey.generate()
    public = key.public_key().public_bytes_raw()
    catalog = {
        "format": 1,
        "publishers": {"pcl-first-party": {"name": "PCL", "verification": "first_party"}},
        "listings": [
            {
                "plugin_id": "pcl.example-rss",
                "name": "Example RSS",
                "description": "RSS",
                "publisher": "pcl-first-party",
                "withdrawn": withdrawn,
                "versions": [
                    {
                        "version": "0.1.0",
                        "api_version": 1,
                        "package_url": "https://catalog.test/pkg.pclplugin",
                        "sha256": "00" * 32,
                        "permissions_summary": {
                            "hosts": ["feeds.bbci.co.uk", "example.com"],
                            "produces": [{"type": "artifact", "classification": "personal"}],
                            "schedule": "60m",
                            "secrets": False,
                        },
                    }
                ],
            }
        ],
    }
    body = json.dumps(catalog, separators=(",", ":")).encode()
    return key, public, body, key.sign(body), catalog


@pytest.mark.plugins
def test_verify_accepts_valid_signature():
    _key, public, body, sig, _catalog = _key_and_catalog()
    verify_catalog(body, sig, public)


@pytest.mark.plugins
def test_verify_rejects_tamper():
    _key, public, body, sig, _catalog = _key_and_catalog()
    with pytest.raises(IntegrityMismatch):
        verify_catalog(body + b"x", sig, public)


@pytest.mark.plugins
def test_refresh_and_killswitch(tmp_path, monkeypatch):
    key, public, body, sig, catalog = _key_and_catalog()
    monkeypatch.setenv("PCH_CATALOG_PUBKEY", public.hex())
    monkeypatch.setenv("PCH_CATALOG_URL", "https://catalog.test/catalog.json")

    class Dummy:
        def __init__(self, content):
            self.content = content
            self.status_code = 200

        def raise_for_status(self):
            return None

    class Transport:
        def __init__(self, catalog_body, signature):
            self.catalog_body = catalog_body
            self.signature = signature

        def get(self, url, timeout=30.0):
            if url.endswith(".sig"):
                return Dummy(self.signature)
            return Dummy(self.catalog_body)

    sync_http.set_client(Transport(body, sig))
    hub = Hub(tmp_path / "vault", plain=True)
    hub.setup("Tester")
    inst = hub.create_plugin_installation(
        {
            "id": "pcl.example-rss",
            "name": "RSS",
            "description": "d",
            "version": "0.1.0",
            "publisher": "ex",
            "api_version": 1,
            "entry": "sync:main",
            "permissions": {"hosts": ["example.com"], "produces": [{"type": "artifact", "classification": "personal"}]},
        }
    )
    hub.consent_plugin(inst["id"])
    refresh_catalog(hub)
    catalog["listings"][0]["withdrawn"] = {"reason": "credential harvesting", "at": "2026-08-21T00:00:00Z"}
    body2 = json.dumps(catalog, separators=(",", ":")).encode()
    sync_http.set_client(Transport(body2, key.sign(body2)))
    refresh_catalog(hub)
    assert hub.get_plugin(inst["id"])["state"] == "paused"
    assert "withdrawn" in hub.get_plugin(inst["id"])["state_reason"]
    sync_http.set_client(None)


@pytest.mark.plugins
def test_local_bundled_catalog_when_no_url(monkeypatch):
    monkeypatch.delenv("PCH_CATALOG_URL", raising=False)
    from pcl_server.marketplace.catalog import local_bundled_catalog

    catalog = local_bundled_catalog()
    assert catalog["offline"] is False
    assert catalog["source"] == "bundled"
    ids = {item["plugin_id"] for item in catalog["listings"]}
    assert "pcl.google-calendar" in ids
    assert "pcl.gmail" in ids
    assert "pcl.example-rss" in ids
