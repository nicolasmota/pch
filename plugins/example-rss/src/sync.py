from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET

from pcl_sdk.plugin_runtime import hub

DEFAULT_FEED = "https://feeds.bbci.co.uk/news/rss.xml"


def main() -> dict:
    selection = hub.run_params.get("selection") or {}
    url = str(selection.get("feed_url") or DEFAULT_FEED)
    response = hub.http_fetch(url)
    body = response.get("body") or ""
    items = _parse(body)[:50]
    if items:
        hub.items_upsert(items)
    return {"created": len(items), "updated": 0}


def _parse(xml_text: str) -> list[dict]:
    if not xml_text.strip():
        return []
    root = ET.fromstring(xml_text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    found = root.findall(".//item") or root.findall(".//atom:entry", ns)
    out: list[dict] = []
    for node in found:
        title = _text(node, "title") or _text(node, "{http://www.w3.org/2005/Atom}title") or "(untitled)"
        link = _text(node, "link") or (node.find("{http://www.w3.org/2005/Atom}link") or {}).get("href") if False else _link(node)
        guid = _text(node, "guid") or link or title
        digest = hashlib.sha256(guid.encode()).hexdigest()[:16]
        out.append({
            "type": "artifact",
            "title": title,
            "body": _text(node, "description") or _text(node, "{http://www.w3.org/2005/Atom}summary") or "",
            "source_key": f"rss:{digest}",
            "classification": "personal",
            "authority": "source_imported",
        })
    return out


def _text(node: ET.Element, tag: str) -> str:
    child = node.find(tag)
    return (child.text or "").strip() if child is not None and child.text else ""


def _link(node: ET.Element) -> str:
    child = node.find("link")
    if child is not None and (child.text or child.get("href")):
        return (child.get("href") or child.text or "").strip()
    atom = node.find("{http://www.w3.org/2005/Atom}link")
    if atom is not None:
        return (atom.get("href") or "").strip()
    return ""
