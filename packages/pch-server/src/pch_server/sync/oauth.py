from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from pathlib import Path
from urllib.parse import urlencode

from pch_core.errors import ValidationFailed
from pch_core.service import Hub

from pch_server.sync import http as sync_http

SCOPES = {
    "calendar": "https://www.googleapis.com/auth/calendar.readonly",
    "email": "https://www.googleapis.com/auth/gmail.readonly",
}

TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
REDIRECT_URI = os.environ.get(
    "PCH_OAUTH_REDIRECT", "http://127.0.0.1:8765/v1/connectors/oauth/callback"
)
MISSING_CLIENT_DETAIL = (
    "Google OAuth is not configured. Create a Desktop OAuth client in Google Cloud Console, "
    "enable the Calendar API and Gmail API, then put the client ID in ~/.pch/google_oauth.json "
    '({"client_id":"...apps.googleusercontent.com","client_secret":"..."}) '
    "or set GOOGLE_OAUTH_CLIENT_ID. Restart the Hub afterwards."
)


def load_google_oauth(data_dir: Path) -> dict[str, str]:
    file_id = file_secret = ""
    path = data_dir / "google_oauth.json"
    if path.is_file():
        try:
            raw = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            raise ValidationFailed("google_oauth.json is not valid JSON") from exc
        file_id = str(raw.get("client_id") or "").strip()
        file_secret = str(raw.get("client_secret") or "").strip()
    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "").strip() or file_id
    client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "").strip() or file_secret
    return {"client_id": client_id, "client_secret": client_secret}


def google_oauth_configured(data_dir: Path) -> bool:
    client_id = load_google_oauth(data_dir)["client_id"]
    return client_id.endswith(".apps.googleusercontent.com")


def require_google_oauth(data_dir: Path) -> dict[str, str]:
    creds = load_google_oauth(data_dir)
    if not creds["client_id"].endswith(".apps.googleusercontent.com"):
        raise ValidationFailed(MISSING_CLIENT_DETAIL)
    return creds


def save_google_oauth(data_dir: Path, client_id: str, client_secret: str = "") -> dict[str, str]:
    client_id = client_id.strip()
    client_secret = client_secret.strip()
    if not client_id.endswith(".apps.googleusercontent.com"):
        raise ValidationFailed(
            "Client ID must look like xxxxx.apps.googleusercontent.com (Google Desktop OAuth client)."
        )
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / "google_oauth.json"
    payload = {"client_id": client_id}
    if client_secret:
        payload["client_secret"] = client_secret
    elif path.is_file():
        existing = load_google_oauth(data_dir)
        if existing.get("client_secret"):
            payload["client_secret"] = existing["client_secret"]
    path.write_text(json.dumps(payload, indent=2) + "\n")
    path.chmod(0o600)
    return {"client_id": client_id, "client_secret": payload.get("client_secret", "")}


def _pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def start_consent(hub: Hub, connector_id: str, kind: str) -> str:
    creds = require_google_oauth(hub.data_dir)
    verifier, challenge = _pkce()
    state = secrets.token_urlsafe(24)
    hub._kv_set(
        f"oauth_state:{state}",
        json.dumps({"connector_id": connector_id, "verifier": verifier, "kind": kind}),
    )
    params = {
        "client_id": creds["client_id"],
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES[kind],
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "access_type": "offline",
        "prompt": "consent",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def complete_consent(hub: Hub, state: str, code: str) -> dict:
    raw = hub._kv_get(f"oauth_state:{state}")
    if not raw:
        raise ValidationFailed("unknown oauth state")
    meta = json.loads(raw)
    connector_id = meta["connector_id"]
    creds = require_google_oauth(hub.data_dir)
    body = {
        "client_id": creds["client_id"],
        "code": code,
        "code_verifier": meta["verifier"],
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    if creds["client_secret"]:
        body["client_secret"] = creds["client_secret"]
    response = sync_http.client().post(TOKEN_URL, data=body, timeout=30.0)
    if response.status_code >= 400:
        from pch_core.errors import Revoked

        raise Revoked("oauth token exchange failed")
    tokens = response.json()
    hub.set_connector_token(connector_id, json.dumps(tokens))
    connector = hub.store.get(connector_id)
    connector["status"] = "active"
    connector["account_label"] = tokens.get("email") or "google"
    stored = hub.store.put(connector)
    from pch_core.schema.audit import EventKind

    hub.ledger.append(EventKind.CONNECTOR_CONNECTED, "owner", "connector connected", [connector_id])
    hub.engine.conn.commit()
    return stored


def refresh_access_token(hub: Hub, connector_id: str) -> str:
    raw = hub.get_connector_token(connector_id)
    if not raw:
        from pch_core.errors import Revoked

        raise Revoked("missing connector token")
    tokens = json.loads(raw)
    if tokens.get("access_token") and not tokens.get("refresh_token"):
        return tokens["access_token"]
    refresh = tokens.get("refresh_token")
    if not refresh:
        return tokens.get("access_token") or ""
    creds = require_google_oauth(hub.data_dir)
    data = {
        "client_id": creds["client_id"],
        "grant_type": "refresh_token",
        "refresh_token": refresh,
    }
    if creds["client_secret"]:
        data["client_secret"] = creds["client_secret"]
    response = sync_http.client().post(TOKEN_URL, data=data, timeout=30.0)
    response.raise_for_status()
    updated = response.json()
    tokens.update(updated)
    hub.set_connector_token(connector_id, json.dumps(tokens))
    return tokens["access_token"]
