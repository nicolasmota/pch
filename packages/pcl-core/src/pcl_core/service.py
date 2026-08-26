from __future__ import annotations

import hashlib
import json
import secrets
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from pcl_core.audit.ledger import Ledger
from pcl_core.errors import NotFound, PolicyDenied, Revoked, ValidationFailed, VersionConflict
from pcl_core.ids import new_id
from pcl_core.memory.orphans import orphan_derived
from pcl_core.memory.pipeline import evaluate_proposal
from pcl_core.memory.sensitivity import blocks_auto_accept
from pcl_core.policy.evaluator import PolicyInput, evaluate
from pcl_core.policy.grants import grant_from_caps, grant_from_preset
from pcl_core.retrieval.ask import compose as compose_ask
from pcl_core.retrieval.ask import retrieve as retrieve_ask
from pcl_core.retrieval.briefs import project_brief
from pcl_core.retrieval.contract import assemble_contract
from pcl_core.retrieval.manifests import build_manifest
from pcl_core.retrieval.search import citations_for, search as fts_search
from pcl_core.schema.action import ActionIntent, IntentStatus
from pcl_core.schema.approval import Approval, DecisionKind
from pcl_core.schema.audit import EventKind
from pcl_core.schema.connection import AgentConnection, ConnectionStatus
from pcl_core.schema.contract import ContextQuery
from pcl_core.schema.grant import Grant, GrantStatus
from pcl_core.schema.manifest import ManifestStatus
from pcl_core.schema.memory import Memory
from pcl_core.schema.metadata import Authority, EntityType
from pcl_core.schema.proposal import ProposalStatus
from pcl_core.schema.state import SharedState, StateVisibility
from pcl_core.timeutil import now_iso, row_is_current, validate_interval
from pcl_core.vault.blobs import BlobStore
from pcl_core.vault.engine import Engine
from pcl_core.vault.keys import load_or_create_key
from pcl_core.vault.objects import ObjectStore


OWNER = "owner"


class Hub:
    def __init__(self, data_dir: Path, passphrase: str | None = None, *, plain: bool | None = None) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.key = load_or_create_key(data_dir, passphrase)
        self.engine = Engine(data_dir / "vault.db", self.key, plain=plain)
        self.store = ObjectStore(self.engine)
        self.ledger = Ledger(self.engine)
        self.blobs = BlobStore(data_dir / "blobs", self.key)
        self.owner_token = self._kv_get("owner_token") or secrets.token_urlsafe(32)
        self._kv_set("owner_token", self.owner_token)

    def close(self) -> None:
        self.engine.close()

    def _kv_get(self, key: str) -> str | None:
        row = self.engine.conn.execute("SELECT v FROM kv WHERE k = ?", (key,)).fetchone()
        return row["v"] if row else None

    def _kv_set(self, key: str, value: str) -> None:
        self.engine.conn.execute(
            "INSERT INTO kv (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v = excluded.v",
            (key, value),
        )
        self.engine.conn.commit()

    def setup_status(self) -> dict:
        person_id = self._kv_get("person_id")
        name = None
        if person_id:
            try:
                name = self.store.get(person_id).get("name")
            except NotFound:
                name = None
        return {
            "initialized": bool(self._kv_get("setup_complete")),
            "in_progress": bool(self._kv_get("setup_started")) and not self._kv_get("setup_complete"),
            "name": name,
        }

    def setup(self, name: str = "Me", restart: bool = False) -> dict:
        with self.engine.tx():
            if restart:
                self.engine.conn.execute("DELETE FROM objects")
                self.engine.conn.execute("DELETE FROM objects_fts")
                self.engine.conn.execute("DELETE FROM object_versions")
            already = bool(self._kv_get("setup_complete")) and not restart
            person_id = self._kv_get("person_id") or new_id("person")
            space_id = "personal"
            now = now_iso()
            if already:
                person = self.store.get(person_id)
                person["name"] = name
                person["updated_at"] = now
                person["version"] = int(person.get("version", 1)) + 1
                self.store.put(person)
                return {"person": person, "space_id": space_id, "owner_token": self.owner_token}
            self._kv_set("setup_started", "1")
            person = {
                "id": person_id,
                "space_id": space_id,
                "type": "person",
                "name": name,
                "time_zone": "UTC",
                "identities": [],
                "owner": person_id,
                "labels": [],
                "classification": "personal",
                "created_at": now,
                "updated_at": now,
                "source_refs": [],
                "confidence": 1.0,
                "authority": "user_confirmed",
                "retention": {"mode": "until_revoked"},
                "policy_tags": [],
                "version": 1,
            }
            space = {
                **person,
                "id": new_id("space"),
                "type": "space",
                "name": "Personal",
                "kind": "personal",
            }
            profile = {
                **person,
                "id": new_id("profile"),
                "type": "profile",
                "contact_norms": "",
                "working_hours": "",
                "extra": {},
            }
            self.store.put(person)
            self.store.put(space)
            self.store.put(profile)
            self._kv_set("person_id", person_id)
            self._kv_set("setup_complete", "1")
            self.ledger.append(EventKind.SETUP, OWNER, "Personal space created", [person_id])
        return {"person": person, "space_id": space_id, "owner_token": self.owner_token}

    def person_id(self) -> str:
        pid = self._kv_get("person_id")
        if not pid:
            raise ValidationFailed("setup not complete")
        return pid

    def _base(self, type_: str, extra: dict[str, Any]) -> dict[str, Any]:
        now = now_iso()
        owner = self.person_id()
        payload = {
            "id": extra.get("id") or new_id(type_),
            "space_id": "personal",
            "type": type_,
            "labels": extra.get("labels") or [],
            "classification": extra.get("classification", "personal"),
            "owner": owner,
            "created_at": extra.get("created_at") or now,
            "updated_at": now,
            "source_refs": extra.get("source_refs") or [],
            "confidence": extra.get("confidence", 1.0),
            "authority": extra.get("authority", "user_confirmed"),
            "retention": extra.get("retention") or {"mode": "until_revoked"},
            "policy_tags": extra.get("policy_tags") or [],
            "version": extra.get("version", 1),
        }
        skip = set(payload) | {"id"}
        for k, v in extra.items():
            if k not in skip or k in extra:
                payload[k] = extra[k]
        payload["id"] = extra.get("id") or payload["id"]
        payload["type"] = type_
        payload["owner"] = owner
        if type_ in ("preference", "memory"):
            payload.setdefault("valid_from", payload["created_at"])
            payload.setdefault("valid_until", None)
            payload.setdefault("never_true", False)
        return payload

    def _assert_interval(self, payload: dict[str, Any]) -> None:
        try:
            validate_interval(payload.get("valid_from"), payload.get("valid_until"))
        except ValueError as exc:
            raise ValidationFailed(str(exc)) from exc

    def _current_preference_for_key(self, key: str, *, exclude_id: str | None = None) -> dict | None:
        at = datetime.now(UTC)
        for row in self.store.list("preference"):
            if row.get("key") != key or row["id"] == exclude_id:
                continue
            if row_is_current(row, at):
                return row
        return None

    def create(self, type_: str, body: dict[str, Any], actor: str = OWNER) -> dict:
        with self.engine.tx():
            payload = self._base(type_, body)
            payload["authority"] = body.get("authority", "user_confirmed")
            if type_ in ("preference", "memory"):
                self._assert_interval(payload)
            if type_ == "preference" and self._current_preference_for_key(
                payload.get("key") or ""
            ):
                raise ValidationFailed(
                    "a current preference with this key already exists; supersede it"
                )
            stored = self.store.put(payload, new=True)
            self.ledger.append(EventKind.OBJECT_WRITE, actor, f"Created {type_}", [stored["id"]])
            return stored

    def get(self, obj_id: str, include_deleted: bool = False) -> dict:
        return self.store.get(obj_id, include_deleted=include_deleted)

    def list(self, type_: str | None = None, project_id: str | None = None) -> list[dict]:
        return self.store.list(type_, project_id)

    def patch(self, obj_id: str, body: dict[str, Any], if_match: int | None, actor: str = OWNER) -> dict:
        with self.engine.tx():
            current = self.store.get(obj_id)
            self.store.versions.check(int(current.get("version", 1)), if_match)
            merged = {**current, **body}
            merged["id"] = obj_id
            merged["type"] = current["type"]
            merged["version"] = int(current.get("version", 1)) + 1
            if actor == OWNER:
                merged["authority"] = "user_confirmed"
            if current.get("type") in ("preference", "memory"):
                self._assert_interval(merged)
            stored = self.store.put(merged)
            self.ledger.append(EventKind.OBJECT_WRITE, actor, f"Updated {current['type']}", [obj_id])
            return stored

    def supersede(self, obj_id: str, body: dict[str, Any], actor: str = OWNER) -> dict:
        with self.engine.tx():
            current = self.store.get(obj_id)
            if current.get("type") not in ("preference", "memory"):
                raise ValidationFailed("only preferences and memories can be superseded")
            now = now_iso()
            if not row_is_current(current, datetime.now(UTC)):
                raise ValidationFailed("target is not current")
            predecessor = {
                **current,
                "valid_until": now,
                "version": int(current.get("version", 1)) + 1,
            }
            if actor == OWNER:
                predecessor["authority"] = "user_confirmed"
            pred_stored = self.store.put(predecessor)
            skip = {"id", "version", "created_at", "updated_at"}
            extra = {k: v for k, v in current.items() if k not in skip}
            extra.update(body)
            extra.pop("id", None)
            extra["valid_from"] = now
            extra["valid_until"] = None
            extra["never_true"] = False
            if actor == OWNER:
                extra["authority"] = "user_confirmed"
            else:
                extra["authority"] = extra.get("authority", "user_confirmed")
            successor = self.create(current["type"], extra, actor=actor)
            self.ledger.append(
                EventKind.OBJECT_WRITE,
                actor,
                f"Superseded {current['type']}",
                [pred_stored["id"], successor["id"]],
                extra={"supersedes": pred_stored["id"], "successor": successor["id"]},
            )
            return {"predecessor": pred_stored, "successor": successor}

    def retract_never_true(self, obj_id: str, actor: str = OWNER) -> dict:
        with self.engine.tx():
            current = self.store.get(obj_id)
            if current.get("type") not in ("preference", "memory"):
                raise ValidationFailed("only preferences and memories can be retracted")
            current["never_true"] = True
            current["version"] = int(current.get("version", 1)) + 1
            self.store.put(current)
            stored = self.store.tombstone(obj_id)
            stored["never_true"] = True
            self.ledger.append(
                EventKind.OBJECT_WRITE,
                actor,
                f"Retracted {current['type']} as never true",
                [obj_id],
            )
            return stored

    def list_truth(self, type_: str) -> list[dict]:
        return [row for row in self.store.list(type_) if not row.get("never_true")]

    def delete(self, obj_id: str, actor: str = OWNER) -> dict:
        with self.engine.tx():
            stored = self.store.tombstone(obj_id)
            orphans = orphan_derived(self.store.list("memory"), obj_id)
            self.ledger.append(EventKind.OBJECT_WRITE, actor, "Deleted object", [obj_id])
            stored["_orphans"] = [o["id"] for o in orphans]
            return stored

    def versions(self, obj_id: str) -> list[dict]:
        return self.store.versions.history(obj_id)

    def search(
        self,
        query: str,
        *,
        type_: str | None = None,
        project_id: str | None = None,
        classification: str | None = None,
        actor: str = OWNER,
        purpose: str | None = None,
        starts_from: str | None = None,
        starts_to: str | None = None,
    ) -> dict:
        rows = fts_search(
            self.engine,
            query,
            type_=type_,
            project_id=project_id,
            classification=classification,
        )
        if starts_from or starts_to:
            filtered = []
            for row in rows:
                start = row.get("starts_at") or ""
                if starts_from and start < starts_from:
                    continue
                if starts_to and start > starts_to:
                    continue
                filtered.append(row)
            rows = filtered
        grants = self.grants_for(actor) if actor != OWNER else []
        kept = []
        redactions: list[str] = []
        for row in rows:
            result = evaluate(
                PolicyInput(
                    actor=actor,
                    is_owner=actor == OWNER,
                    grants=grants,
                    resource_type=row.get("type", ""),
                    resource_project=row.get("project_id"),
                    classification=row.get("classification", "personal"),
                    capability=self._cap_for(row.get("type", "")),
                    purpose=purpose,
                )
            )
            self.ledger.append(
                EventKind.POLICY_DECISION,
                actor,
                f"search {result.decision}",
                [row.get("id", "")],
                extra={"decision": result.decision},
            )
            if result.decision.value == "allow":
                item = {**row, "citations": citations_for(row)}
                kept.append(item)
            else:
                redactions.extend(result.redactions or [result.reason])
        self.ledger.append(EventKind.CONTEXT_REQUEST, actor, f"search {query!r}", [r["id"] for r in kept])
        return {"results": kept, "redactions": redactions}

    def ask(
        self,
        question: str,
        *,
        actor: str = OWNER,
        purpose: str | None = None,
    ) -> dict:
        rows = retrieve_ask(self.engine, question)
        grants = self.grants_for(actor) if actor != OWNER else []
        kept = []
        notices: list[str] = []
        for row in rows:
            result = evaluate(
                PolicyInput(
                    actor=actor,
                    is_owner=actor == OWNER,
                    grants=grants,
                    resource_type=row.get("type", ""),
                    resource_project=row.get("project_id"),
                    classification=row.get("classification", "personal"),
                    capability=self._cap_for(row.get("type", "")),
                    purpose=purpose or "personal_question",
                )
            )
            if result.decision.value == "allow":
                kept.append(row)
            else:
                notices.extend(result.redactions or [result.reason])
        out = compose_ask(kept)
        if notices and not out["citations"]:
            existing_notices = list(out.get("notices") or [])
            out["notices"] = list(dict.fromkeys([*existing_notices, *notices]))
        self.ledger.append(
            EventKind.CONTEXT_DISCLOSE,
            actor,
            f"ask {question!r}",
            [c["id"] for c in out["citations"]],
        )
        return out

    def _cap_for(self, type_: str) -> str:
        if type_ in ("project", "goal", "decision"):
            return "project.read"
        if type_ == "commitment":
            return "commitment.read"
        if type_ in ("memory", "artifact", "event"):
            return "memory.retrieve"
        if type_ in ("profile", "preference", "person"):
            return "profile.read"
        return "project.read"

    def brief(self, project_id: str, actor: str = OWNER) -> dict:
        project = self.store.get(project_id)
        related = self.store.list(project_id=project_id)
        if actor != OWNER:
            filtered = self.search("", project_id=project_id, actor=actor)["results"]
            related = filtered
        return project_brief(project, related)

    def record_contract_refusal(self, actor: str, purpose: str) -> None:
        self.ledger.append(
            EventKind.CONTEXT_CONTRACT,
            actor,
            f"contract refused {purpose!r}",
            extra={
                "contract_id": None,
                "purpose": purpose,
                "status": "refused",
                "situation": None,
                "item_refs": [],
                "omission_categories": [],
            },
        )

    def get_context_contract(
        self,
        actor: str,
        purpose: str,
        subject_ref: str | None = None,
        max_items: int | None = None,
        as_of: str | None = None,
    ) -> dict:
        try:
            query = ContextQuery(
                purpose=purpose, subject_ref=subject_ref, max_items=max_items, as_of=as_of
            )
        except ValidationError as exc:
            loc = ""
            errs = exc.errors() if hasattr(exc, "errors") else []
            if errs:
                loc = ".".join(str(p) for p in errs[0].get("loc", ()))
            if loc == "as_of" or "as_of" in str(exc):
                raise ValidationFailed("as_of is invalid") from exc
            raise ValidationFailed("purpose is required") from exc
        if actor != OWNER:
            conn = self.store.get(actor)
            if conn.get("status") == "revoked":
                self.record_contract_refusal(actor, query.purpose)
                raise Revoked()
            grants = self.grants_for(actor)
            if not any(g.status == GrantStatus.ACTIVE for g in grants):
                self.record_contract_refusal(actor, query.purpose)
                raise PolicyDenied("no active grants")
        else:
            grants = []
        contract = assemble_contract(
            self.store,
            query,
            actor=actor,
            is_owner=actor == OWNER,
            grants=grants,
            cap_for=self._cap_for,
        )
        item_refs = []
        for section in (
            contract.goals,
            contract.preferences,
            contract.memories,
            contract.decisions,
            contract.constraints,
            contract.state,
        ):
            for item in section:
                item_refs.append({"id": item.ref.id, "type": item.ref.type})
        extra = {
            "contract_id": contract.contract_id,
            "purpose": contract.purpose,
            "status": "issued",
            "situation": contract.situation.project_id if contract.situation else None,
            "item_refs": item_refs,
            "omission_categories": [
                {"category": o.category.value, "count": o.count} for o in contract.omissions
            ],
        }
        self.ledger.append(
            EventKind.CONTEXT_CONTRACT,
            actor,
            f"contract {query.purpose!r}",
            [r["id"] for r in item_refs],
            extra=extra,
        )
        return contract.model_dump(mode="json")

    # --- connections / grants ---

    def mint_link(self, name: str = "agent") -> dict:
        code = secrets.token_urlsafe(16)
        conn = AgentConnection(id=new_id("connection"), name=name, status=ConnectionStatus.PENDING)
        with self.engine.tx():
            self.store.put({**conn.model_dump(mode="json"), "type": "connection", "owner": self.person_id(),
                            "labels": [], "classification": "private", "created_at": now_iso(),
                            "updated_at": now_iso(), "source_refs": [], "confidence": 1.0,
                            "authority": "user_confirmed", "retention": {"mode": "until_revoked"},
                            "policy_tags": [], "version": 1})
            self._kv_set(f"link:{code}", conn.id)
        return {"link": f"pch://pair/{code}", "code": code, "connection_id": conn.id}

    def pair(self, code: str, runtime_info: dict | None = None) -> dict:
        conn_id = self._kv_get(f"link:{code}")
        if not conn_id:
            raise ValidationFailed("invalid pairing code")
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self.engine.tx():
            payload = self.store.get(conn_id)
            if payload.get("status") == "revoked":
                raise Revoked()
            payload["status"] = "active"
            payload["credential_hash"] = token_hash
            payload["paired_at"] = now_iso()
            payload["runtime_info"] = runtime_info or {}
            payload["version"] = int(payload.get("version", 1)) + 1
            self.store.put(payload)
            self._kv_set(f"token:{token_hash}", conn_id)
            self.ledger.append(EventKind.CONNECTION_PAIRED, conn_id, f"Paired {payload.get('name')}", [conn_id])
        return {"connection_id": conn_id, "token": token}

    def issue_connection_token(self, connection_id: str) -> str:
        payload = self.store.get(connection_id)
        if payload.get("status") == "revoked":
            raise Revoked()
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self.engine.tx():
            payload["status"] = "active"
            payload["credential_hash"] = token_hash
            payload["paired_at"] = payload.get("paired_at") or now_iso()
            payload["version"] = int(payload.get("version", 1)) + 1
            self.store.put(payload)
            self._kv_set(f"token:{token_hash}", connection_id)
        return token

    def actor_from_token(self, token: str) -> tuple[str, bool]:
        if token == self.owner_token:
            return OWNER, True
        digest = hashlib.sha256(token.encode()).hexdigest()
        conn_id = self._kv_get(f"token:{digest}")
        if not conn_id:
            raise Revoked("invalid token")
        payload = self.store.get(conn_id)
        if payload.get("status") == "revoked":
            raise Revoked()
        return conn_id, False

    def connections(self) -> list[dict]:
        return self.store.list("connection")

    def revoke_connection(self, conn_id: str) -> dict:
        with self.engine.tx():
            payload = self.store.get(conn_id)
            payload["status"] = "revoked"
            payload["revoked_at"] = now_iso()
            payload["version"] = int(payload.get("version", 1)) + 1
            self.store.put(payload)
            for grant in self.grants_for(conn_id):
                g = grant.model_dump()
                g["status"] = "revoked"
                self._put_grant(Grant.model_validate(g))
            for man in self.store.list("manifest"):
                if man.get("connection_id") == conn_id:
                    man["status"] = "invalidated"
                    self.store.put(man)
            self.ledger.append(EventKind.CONNECTION_REVOKED, OWNER, "Connection revoked", [conn_id])
        return payload

    def _put_grant(self, grant: Grant) -> dict:
        payload = grant.model_dump(mode="json")
        payload.update({
            "type": "grant",
            "owner": self.person_id(),
            "labels": [],
            "classification": "private",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "source_refs": [],
            "confidence": 1.0,
            "authority": "user_confirmed",
            "retention": {"mode": "until_revoked"},
            "policy_tags": [],
            "version": 1,
            "id": grant.id,
        })
        return self.store.put(payload)

    def create_grant(self, connection_id: str, preset: str | None, capabilities: list[str] | None,
                     selectors: dict | None, classification_ceiling: str = "private") -> dict:
        if preset:
            grant = grant_from_preset(connection_id, preset, selectors, classification_ceiling)
        else:
            grant = grant_from_caps(connection_id, capabilities or [], selectors, classification_ceiling)
        with self.engine.tx():
            stored = self._put_grant(grant)
            self.ledger.append(EventKind.GRANT_CREATED, OWNER, grant.summary_human, [grant.id, connection_id])
        return stored

    def revoke_grant(self, grant_id: str) -> dict:
        with self.engine.tx():
            payload = self.store.get(grant_id)
            payload["status"] = "revoked"
            stored = self.store.put(payload)
            self.ledger.append(EventKind.GRANT_REVOKED, OWNER, "Grant revoked", [grant_id])
        return stored

    def grants_for(self, connection_id: str) -> list[Grant]:
        out = []
        for row in self.store.list("grant"):
            if row.get("connection_id") == connection_id:
                out.append(Grant.model_validate({k: v for k, v in row.items() if k in Grant.model_fields}))
        return out

    def all_grants(self, connection_id: str | None = None) -> list[dict]:
        rows = self.store.list("grant")
        if connection_id:
            rows = [r for r in rows if r.get("connection_id") == connection_id]
        return rows

    def create_manifest(self, actor: str, purpose: str, requested: list[str],
                        selectors: dict, ttl: int = 900) -> dict:
        if actor == OWNER:
            raise ValidationFailed("owner uses CRUD, not manifests")
        conn = self.store.get(actor)
        if conn.get("status") == "revoked":
            raise Revoked()
        scoped = selectors.get("project")
        search_result = self.search("", project_id=scoped, actor=actor, purpose=purpose)
        entities = search_result["results"]
        redactions = search_result["redactions"]
        # also include project itself if allowed
        manifest = build_manifest(actor, purpose, requested, selectors, entities, redactions, ttl)
        payload = manifest.model_dump(mode="json")
        payload.update({
            "type": "manifest",
            "owner": self.person_id(),
            "labels": [],
            "classification": "private",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "source_refs": [],
            "confidence": 1.0,
            "authority": "user_confirmed",
            "retention": {"mode": "expires", "at": manifest.expires_at},
            "policy_tags": [],
            "version": 1,
        })
        with self.engine.tx():
            self.store.put(payload)
            self.ledger.append(EventKind.CONTEXT_DISCLOSE, actor, f"manifest {purpose}", [manifest.id])
        return payload

    def get_manifest(self, manifest_id: str, actor: str) -> dict:
        man = self.store.get(manifest_id)
        if man.get("status") == "invalidated":
            raise Revoked("manifest invalidated")
        expires = man.get("expires_at")
        if expires and expires < now_iso():
            man["status"] = "expired"
            self.store.put(man)
            raise Revoked("manifest expired")
        if actor != OWNER and man.get("connection_id") != actor:
            raise PolicyDenied()
        return man

    # --- shared state ---

    def set_state(self, key: str, value: Any, ttl: int, visibility: str, actor: str) -> dict:
        if actor != OWNER:
            grants = self.grants_for(actor)
            result = evaluate(PolicyInput(actor, False, grants, "shared_state", None, "personal", "state.write"))
            if result.decision.value != "allow":
                raise PolicyDenied(result.reason)
            if visibility == "shared":
                share = evaluate(PolicyInput(actor, False, grants, "shared_state", None, "personal", "state.share"))
                # allow share if they have state.write and visibility requested; require state.share if present in vocab
                has_share = any("state.share" in [str(c) for c in g.capabilities] for g in grants)
                if not has_share:
                    # still allow if owner-equivalent write grant exists? spec says shared requires permission
                    raise PolicyDenied("missing state.share")
        expires = (datetime.now(UTC) + timedelta(seconds=ttl)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        state = SharedState(
            key=key, value=value, ttl_seconds=ttl, expires_at=expires,
            visibility=StateVisibility(visibility), created_by=actor,
        )
        payload = state.model_dump(mode="json")
        payload.update({
            "id": f"st_{key}",
            "type": "shared_state",
            "owner": self.person_id() if self._kv_get("person_id") else actor,
            "labels": [],
            "classification": "personal",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "source_refs": [],
            "confidence": 1.0,
            "authority": "agent_inferred",
            "retention": {"mode": "expires", "at": expires},
            "policy_tags": [],
            "version": 1,
        })
        with self.engine.tx():
            self.store.put(payload)
            self.ledger.append(EventKind.STATE_WRITE, actor, f"state {key}", [payload["id"]])
        return payload

    def get_state(self, key: str, actor: str) -> dict:
        payload = self.store.get(f"st_{key}")
        if payload.get("expires_at") and payload["expires_at"] < now_iso():
            raise NotFound("state expired")
        if actor != OWNER and payload.get("created_by") != actor and payload.get("visibility") != "shared":
            raise PolicyDenied()
        return payload

    # --- memory proposals ---

    def propose_memory(self, body: dict, actor: str, evidence_refs: list[str]) -> dict:
        if actor == OWNER:
            raise ValidationFailed("owner writes memories directly")
        mem_body = {**body}
        mem_body.setdefault("type", "memory")
        mem_body.setdefault("authority", "proposed")
        mem_body.setdefault("owner", self.person_id())
        mem_body.setdefault("id", new_id("memory"))
        mem_body.setdefault("space_id", "personal")
        mem_body.setdefault("created_at", now_iso())
        mem_body.setdefault("updated_at", now_iso())
        mem_body.setdefault("version", 1)
        mem_body.setdefault("labels", [])
        mem_body.setdefault("classification", "personal")
        mem_body.setdefault("source_refs", evidence_refs)
        mem_body.setdefault("confidence", 0.6)
        mem_body.setdefault("retention", {"mode": "until_revoked"})
        mem_body.setdefault("policy_tags", [])
        memory = Memory.model_validate(mem_body)
        existing = self.store.list("memory")
        proposal, conflicts = evaluate_proposal(memory, existing, actor, evidence_refs)
        if blocks_auto_accept(memory) and proposal.status == ProposalStatus.AUTO_ACCEPTED:
            proposal.status = ProposalStatus.PENDING
            proposal.policy_verdict = "needs_review"
        with self.engine.tx():
            p = proposal.model_dump(mode="json")
            p.update({
                "type": "proposal",
                "owner": self.person_id(),
                "labels": [],
                "classification": "personal",
                "created_at": proposal.created_at,
                "updated_at": now_iso(),
                "source_refs": evidence_refs,
                "confidence": memory.confidence,
                "authority": "proposed",
                "retention": {"mode": "until_revoked"},
                "policy_tags": [],
                "version": 1,
                "statement": memory.statement,
            })
            self.store.put(p)
            for c in conflicts:
                cp = c.model_dump(mode="json")
                cp.update({
                    "type": "conflict",
                    "owner": self.person_id(),
                    "labels": [],
                    "classification": "personal",
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                    "source_refs": [],
                    "confidence": 1.0,
                    "authority": "user_confirmed",
                    "retention": {"mode": "until_revoked"},
                    "policy_tags": [],
                    "version": 1,
                })
                self.store.put(cp)
            self.ledger.append(EventKind.MEMORY_PROPOSED, actor, "memory proposed", [proposal.id])
        return {**p, "conflicts": [c.model_dump(mode="json") for c in conflicts]}

    def decide_proposal(self, proposal_id: str, accept: bool, edits: dict | None = None) -> dict:
        with self.engine.tx():
            p = self.store.get(proposal_id)
            if accept:
                mem = p["proposed_memory"]
                if edits:
                    mem = {**mem, **edits}
                    mem["authority"] = "user_confirmed"
                else:
                    mem["authority"] = "agent_inferred"
                mem["type"] = "memory"
                stored = None
                subject = mem.get("subject_ref")
                if subject:
                    at = datetime.now(UTC)
                    for row in self.store.list("memory"):
                        if row.get("subject_ref") == subject and row_is_current(row, at):
                            result = self.supersede(row["id"], mem)
                            stored = result["successor"]
                            break
                if stored is None:
                    mem.setdefault("id", new_id("memory"))
                    stored = self.store.put(mem)
                p["status"] = "accepted"
                self.store.put(p)
                self.ledger.append(EventKind.MEMORY_ACCEPTED, OWNER, "proposal accepted", [stored["id"]])
                return stored
            p["status"] = "rejected"
            self.store.put(p)
            self.ledger.append(EventKind.MEMORY_REJECTED, OWNER, "proposal rejected", [proposal_id])
            return p

    def resolve_conflict(self, conflict_id: str, status: str) -> dict:
        with self.engine.tx():
            c = self.store.get(conflict_id)
            c["status"] = status
            return self.store.put(c)

    # --- actions ---

    def propose_action(self, actor: str, kind: str, summary: str, payload: dict,
                       basis_refs: list[str], idempotency_key: str) -> dict:
        existing = None
        for row in self.store.list("action_intent"):
            if row.get("connection_id") == actor and row.get("idempotency_key") == idempotency_key:
                existing = row
                break
        if existing:
            return existing
        intent = ActionIntent(
            id=new_id("action_intent"),
            connection_id=actor,
            kind=kind,
            summary_human=summary,
            payload=payload,
            basis_refs=basis_refs,
            idempotency_key=idempotency_key,
            status=IntentStatus.PENDING,
            created_at=now_iso(),
        )
        body = intent.model_dump(mode="json")
        body.update({
            "type": "action_intent",
            "owner": self.person_id(),
            "labels": [],
            "classification": "personal",
            "created_at": intent.created_at,
            "updated_at": now_iso(),
            "source_refs": basis_refs,
            "confidence": 1.0,
            "authority": "agent_inferred",
            "retention": {"mode": "until_revoked"},
            "policy_tags": [],
            "version": 1,
        })
        declined = [r for r in self.store.list("action_intent")
                    if r.get("connection_id") == actor and r.get("kind") == kind
                    and r.get("status") == "declined"]
        if declined:
            body["declined_parent_id"] = declined[-1]["id"]
        with self.engine.tx():
            self.store.put(body)
            self.ledger.append(EventKind.ACTION_INTENT, actor, summary, [intent.id])
        return body

    def decide_approval(self, intent_id: str, approved: bool) -> dict:
        with self.engine.tx():
            intent = self.store.get(intent_id)
            intent["status"] = "approved" if approved else "declined"
            intent["decided_at"] = now_iso()
            self.store.put(intent)
            approval = Approval(
                id=new_id("approval"),
                intent_ref=intent_id,
                decision=DecisionKind.APPROVED if approved else DecisionKind.DECLINED,
                decided_at=intent["decided_at"],
                context_shown={"summary": intent.get("summary_human"), "who": intent.get("connection_id")},
            )
            ap = approval.model_dump(mode="json")
            ap.update({
                "type": "approval",
                "owner": self.person_id(),
                "labels": [],
                "classification": "personal",
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "source_refs": [],
                "confidence": 1.0,
                "authority": "user_confirmed",
                "retention": {"mode": "until_revoked"},
                "policy_tags": [],
                "version": 1,
            })
            self.store.put(ap)
            self.ledger.append(EventKind.APPROVAL_DECIDED, OWNER,
                               "approved" if approved else "declined", [intent_id])
            return intent

    def action_result(self, intent_id: str, status: str, actor: str) -> dict:
        with self.engine.tx():
            intent = self.store.get(intent_id)
            if intent.get("status") != "approved" and status == "executed":
                raise PolicyDenied("cannot execute unapproved intent")
            intent["status"] = status
            self.store.put(intent)
            kind = EventKind.ACTION_EXECUTED if status == "executed" else EventKind.ACTION_FAILED
            self.ledger.append(kind, actor, f"action {status}", [intent_id])
            return intent

    def events(self, kind: str | None = None, actor: str | None = None) -> list[dict]:
        return [e.model_dump(mode="json") for e in self.ledger.list_events(kind, actor)]

    def verify_events(self) -> dict:
        return self.ledger.verify()

    def idempotency_get(self, key: str) -> tuple[int, str] | None:
        row = self.engine.conn.execute(
            "SELECT status, body FROM idempotency WHERE key = ?", (key,)
        ).fetchone()
        if row:
            return int(row["status"]), row["body"]
        return None

    def idempotency_set(self, key: str, status: int, body: str) -> None:
        self.engine.conn.execute(
            "INSERT OR REPLACE INTO idempotency (key, status, body, created_at) VALUES (?, ?, ?, ?)",
            (key, status, body, now_iso()),
        )
        self.engine.conn.commit()

    def _token_kv_key(self, connector_id: str) -> str:
        return f"connector_token:{connector_id}"

    def set_connector_token(self, connector_id: str, token_blob: str) -> None:
        self._kv_set(self._token_kv_key(connector_id), token_blob)

    def get_connector_token(self, connector_id: str) -> str | None:
        return self._kv_get(self._token_kv_key(connector_id))

    def delete_connector_token(self, connector_id: str) -> None:
        self.engine.conn.execute("DELETE FROM kv WHERE k = ?", (self._token_kv_key(connector_id),))
        self.engine.conn.commit()

    def kv_keys(self) -> list[str]:
        return [r["k"] for r in self.engine.conn.execute("SELECT k FROM kv").fetchall()]

    def create_connector(self, provider: str, kind: str, selection: dict | None = None) -> dict:
        cadence = 15 if kind == "calendar" else 60
        body = {
            "provider": provider,
            "kind": kind,
            "status": "pending_consent",
            "selection": selection or {},
            "cadence_minutes": cadence,
            "classification": "private",
            "account_label": "",
        }
        stored = self.create("connector_account", body)
        return stored

    def list_connectors(self) -> list[dict]:
        return [c for c in self.store.list("connector_account") if c.get("status") != "disconnected"]

    def patch_connector(self, connector_id: str, body: dict, if_match: int | None = None) -> dict:
        if body.get("kind") == "email" or self.store.get(connector_id).get("kind") == "email":
            selection = body.get("selection")
            if selection is not None and not _email_selection_ok(selection):
                raise ValidationFailed("email selection must include labels, senders, or a date range")
        return self.patch(connector_id, body, if_match)

    def upsert_by_source_key(self, payload: dict) -> tuple[dict, str]:
        with self.engine.tx():
            return self._upsert_by_source_key(payload)

    def _upsert_by_source_key(self, payload: dict) -> tuple[dict, str]:
        key = payload.get("source_key")
        if not key:
            raise ValidationFailed("source_key required")
        existing = self.store.get_by_source_key(key, include_deleted=True)
        if existing:
            payload["id"] = existing["id"]
            payload["version"] = int(existing.get("version", 1)) + 1
            payload["created_at"] = existing.get("created_at")
            return self.store.put(payload), "updated"
        return self.store.put(payload, new=True), "created"

    def tombstone_source_key(self, source_key: str) -> dict | None:
        existing = self.store.get_by_source_key(source_key)
        if not existing:
            return None
        with self.engine.tx():
            return self.store.tombstone(existing["id"])

    def apply_connector_items(
        self, connector_id: str, items: list[dict], deleted_keys: list[str] | None = None
    ) -> dict:
        created = updated = tombstoned = 0
        with self.engine.tx():
            for item in items:
                _, action = self._upsert_by_source_key(item)
                if action == "created":
                    created += 1
                else:
                    updated += 1
            for key in deleted_keys or []:
                existing = self.store.get_by_source_key(key)
                if existing:
                    self.store.tombstone(existing["id"])
                    tombstoned += 1
            connector = self.store.get(connector_id)
            last_sync = {
                "at": now_iso(),
                "outcome": "ok",
                "created": created,
                "updated": updated,
                "tombstoned": tombstoned,
            }
            connector["last_sync"] = last_sync
            self.store.put(connector)
            self.ledger.append(
                EventKind.CONNECTOR_SYNC,
                OWNER,
                f"sync {connector.get('kind')} {last_sync['outcome']}",
                [connector_id],
                extra=last_sync,
            )
        return last_sync

    def disconnect_connector(self, connector_id: str, *, purge: bool = False) -> dict:
        connector = self.store.get(connector_id)
        with self.engine.tx():
            connector["status"] = "disconnected"
            self.store.put(connector)
            self.delete_connector_token(connector_id)
            if purge:
                prefix = f"google:{connector_id}:"
                for row in self.store.list_by_source_prefix(prefix):
                    self.store.tombstone(row["id"])
            stored = self.store.tombstone(connector_id)
            self.ledger.append(
                EventKind.CONNECTOR_DISCONNECTED,
                OWNER,
                "connector disconnected",
                [connector_id],
                extra={"purge": purge},
            )
        return stored

    def recipe_issued(self, connection_id: str, assistant: str) -> None:
        self.ledger.append(
            EventKind.CONNECTION_RECIPE_ISSUED,
            OWNER,
            f"recipe issued for {assistant}",
            [connection_id],
        )

    def _plugin_secret_key(self, installation_id: str, name: str) -> str:
        return f"plugin_secret:{installation_id}:{name}"

    def _plugin_state_key(self, installation_id: str, name: str) -> str:
        return f"plugin_state:{installation_id}:{name}"

    def set_plugin_secret(self, installation_id: str, name: str, value: str) -> None:
        self._kv_set(self._plugin_secret_key(installation_id, name), value)

    def get_plugin_secret(self, installation_id: str, name: str) -> str | None:
        return self._kv_get(self._plugin_secret_key(installation_id, name))

    def delete_plugin_secrets(self, installation_id: str) -> None:
        prefix = f"plugin_secret:{installation_id}:"
        for key in list(self.kv_keys()):
            if key.startswith(prefix) or key.startswith(f"plugin_state:{installation_id}:"):
                self.engine.conn.execute("DELETE FROM kv WHERE k = ?", (key,))
        self.engine.conn.commit()

    def set_plugin_state_value(self, installation_id: str, name: str, value: str) -> None:
        self._kv_set(self._plugin_state_key(installation_id, name), value)

    def get_plugin_state_value(self, installation_id: str, name: str) -> str | None:
        return self._kv_get(self._plugin_state_key(installation_id, name))

    def list_plugins(self) -> list[dict]:
        return [p for p in self.store.list("plugin") if p.get("state") != "removed"]

    def get_plugin(self, installation_id: str) -> dict:
        payload = self.store.get(installation_id)
        if payload.get("type") != "plugin":
            raise NotFound(installation_id)
        return payload

    def create_plugin_installation(
        self,
        manifest: dict,
        *,
        origin: str = "bundled",
        package_sha256: str = "",
        isolation: str = "reduced",
        installation_id: str | None = None,
        selection: dict | None = None,
        source_account_id: str | None = None,
    ) -> dict:
        body = {
            "plugin_id": manifest["id"],
            "plugin_version": manifest["version"],
            "manifest": manifest,
            "origin": origin,
            "package_sha256": package_sha256,
            "state": "installed",
            "state_reason": "",
            "grant_id": None,
            "isolation": isolation,
            "last_run": None,
            "selection": selection or {},
            "sync_cursor": None,
            "source_account_id": source_account_id,
            "classification": "private",
        }
        if installation_id:
            body["id"] = installation_id
        stored = self.create("plugin", body)
        self.ledger.append(
            EventKind.PLUGIN_INSTALL,
            OWNER,
            f"installed {manifest['id']}",
            [stored["id"]],
            extra={"origin": origin, "version": manifest["version"]},
        )
        return stored

    def consent_plugin(self, installation_id: str, *, schedule: str | None = None) -> dict:
        inst = self.get_plugin(installation_id)
        if inst.get("state") in {"removed"}:
            raise ValidationFailed("plugin is removed")
        manifest = inst["manifest"]
        permissions = manifest.get("permissions") or {}
        grant = self.create_grant(
            f"plugin:{installation_id}",
            None,
            [],
            {
                "produces": json.dumps(permissions.get("produces") or []),
                "hosts": ",".join(permissions.get("hosts") or []),
                "schedule": schedule or permissions.get("schedule") or "manual",
                "approved_manifest_version": manifest.get("version", ""),
            },
            "sensitive",
        )
        inst["grant_id"] = grant["id"]
        inst["state"] = "enabled"
        inst["state_reason"] = ""
        if schedule:
            inst.setdefault("manifest", {}).setdefault("permissions", {})["schedule"] = schedule
        stored = self.store.put(inst)
        self.ledger.append(
            EventKind.PLUGIN_CONSENT,
            OWNER,
            f"consented {inst.get('plugin_id')}",
            [installation_id, grant["id"]],
        )
        self.engine.conn.commit()
        return stored

    def set_plugin_state(self, installation_id: str, state: str, reason: str = "") -> dict:
        inst = self.get_plugin(installation_id)
        inst["state"] = state
        inst["state_reason"] = reason
        stored = self.store.put(inst)
        self.ledger.append(
            EventKind.PLUGIN_LIFECYCLE,
            OWNER,
            f"plugin {state}",
            [installation_id],
            extra={"reason": reason},
        )
        self.engine.conn.commit()
        return stored

    def apply_plugin_items(
        self,
        installation_id: str,
        items: list[dict],
        deleted_keys: list[str] | None = None,
    ) -> dict:
        created = updated = tombstoned = 0
        with self.engine.tx():
            for item in items:
                item.setdefault("id", new_id(str(item.get("type") or "artifact")))
                item.setdefault("space_id", "personal")
                item.setdefault("owner", self.person_id())
                item.setdefault("labels", [])
                item.setdefault("created_at", now_iso())
                item.setdefault("updated_at", now_iso())
                item.setdefault("confidence", 1.0)
                item.setdefault("retention", {"mode": "until_revoked"})
                item.setdefault("policy_tags", [])
                item.setdefault("version", 1)
                item.setdefault("source_refs", [])
                if f"plugin:{installation_id}" not in item["source_refs"]:
                    item["source_refs"] = [*item["source_refs"], f"plugin:{installation_id}"]
                item.setdefault("authority", "source_imported")
                _, action = self._upsert_by_source_key(item)
                if action == "created":
                    created += 1
                else:
                    updated += 1
            for key in deleted_keys or []:
                existing = self.store.get_by_source_key(key)
                if existing and f"plugin:{installation_id}" in (existing.get("source_refs") or []):
                    self.store.tombstone(existing["id"])
                    tombstoned += 1
            inst = self.store.get(installation_id)
            last_run = {
                "at": now_iso(),
                "outcome": "ok",
                "created": created,
                "updated": updated,
                "tombstoned": tombstoned,
            }
            inst["last_run"] = last_run
            self.store.put(inst)
            self.ledger.append(
                EventKind.PLUGIN_SYNC,
                f"plugin:{installation_id}",
                f"sync {inst.get('plugin_id')} ok",
                [installation_id],
                extra=last_run,
            )
        return last_run

    def remove_plugin(self, installation_id: str, *, purge_data: bool = False) -> dict:
        inst = self.get_plugin(installation_id)
        with self.engine.tx():
            if inst.get("grant_id"):
                try:
                    self.revoke_grant(inst["grant_id"])
                except NotFound:
                    pass
            self.delete_plugin_secrets(installation_id)
            if purge_data:
                marker = f"plugin:{installation_id}"
                for row in self.store.list():
                    if marker in (row.get("source_refs") or []):
                        self.store.tombstone(row["id"])
            inst["state"] = "removed"
            stored = self.store.tombstone(installation_id)
            self.ledger.append(
                EventKind.PLUGIN_LIFECYCLE,
                OWNER,
                "plugin removed",
                [installation_id],
                extra={"purge_data": purge_data},
            )
        return stored

    def record_plugin_denied(self, installation_id: str, detail: str) -> None:
        self.ledger.append(
            EventKind.PLUGIN_DENIED,
            f"plugin:{installation_id}",
            detail,
            [installation_id],
        )


def _email_selection_ok(selection: dict) -> bool:
    labels = selection.get("labels") or []
    senders = selection.get("senders") or []
    return bool(labels or senders or selection.get("after") or selection.get("before"))
