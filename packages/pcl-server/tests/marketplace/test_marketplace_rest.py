import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pcl_server.sync import http as sync_http


@pytest.mark.plugins
def test_catalog_and_tampered_install(client, monkeypatch, tmp_path):
    key = Ed25519PrivateKey.generate()
    public = key.public_key().public_bytes_raw()
    monkeypatch.setenv("PCH_CATALOG_PUBKEY", public.hex())
    monkeypatch.setenv("PCH_CATALOG_URL", "https://catalog.test/catalog.json")
    catalog = {
        "format": 1,
        "publishers": {"p": {"name": "P", "verification": "verified"}},
        "listings": [
            {
                "plugin_id": "pcl.example-rss",
                "name": "RSS",
                "description": "d",
                "publisher": "p",
                "withdrawn": None,
                "versions": [
                    {
                        "version": "0.1.0",
                        "api_version": 1,
                        "package_url": "https://catalog.test/pkg.pclplugin",
                        "sha256": "aa" * 32,
                        "permissions_summary": {"hosts": ["example.com"], "produces": [{"type": "artifact"}]},
                    }
                ],
            }
        ],
    }
    body = json.dumps(catalog, separators=(",", ":")).encode()
    sig = key.sign(body)

    class Dummy:
        def __init__(self, content, status=200):
            self.content = content
            self.status_code = status
            self.headers = {}

        def raise_for_status(self):
            if self.status_code >= 400:
                raise RuntimeError("http")

    class Transport:
        def get(self, url, timeout=30.0):
            if url.endswith(".sig"):
                return Dummy(sig)
            if url.endswith("catalog.json"):
                return Dummy(body)
            return Dummy(b"not-a-real-package")

    sync_http.set_client(Transport())
    refreshed = client.post("/v1/marketplace/refresh", json={})
    assert refreshed.status_code == 200
    listed = client.get("/v1/marketplace/catalog")
    assert listed.json()["listings"]
    bad = client.post("/v1/marketplace/install", json={"plugin_id": "pcl.example-rss"})
    assert bad.status_code in {400, 422}
    sync_http.set_client(None)
