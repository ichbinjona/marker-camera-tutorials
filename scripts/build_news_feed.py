#!/usr/bin/env python3
"""Builds news/feed.json from news/posts/*.md (N.1.3).

Validation is strict on REQUIRED fields and date logic (a broken post must
never go live), but lenient on unknown fields: every frontmatter key is passed
through to the feed untouched. That is the future-proofing contract (N.9.6):
older app versions ignore keys they don't know, and posts can carry a
minAppVersion so old clients skip them entirely.
"""

import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "news" / "posts"
OUT_PATH = ROOT / "news" / "feed.json"

KNOWN_AUDIENCES = {"all", "free", "pro", "pro_no_team"}
KNOWN_SECTIONS = {"news", "academy"}


def fail(message: str) -> None:
    print(f"::error::{message}")
    sys.exit(1)


def normalize(value):
    """YAML dates/datetimes -> ISO-8601 strings (UTC for datetimes)."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def parse_post(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not match:
        fail(f"{path.name}: missing frontmatter block (--- ... ---)")
    try:
        meta = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        fail(f"{path.name}: YAML error: {exc}")
    if not isinstance(meta, dict):
        fail(f"{path.name}: frontmatter must be a mapping")

    for field in ("id", "title", "date", "summary"):
        if not meta.get(field):
            fail(f"{path.name}: missing required field '{field}'")

    if not isinstance(meta["date"], (date, datetime)):
        fail(f"{path.name}: 'date' must be a YAML date (YYYY-MM-DD)")

    audience = meta.get("audience", "all")
    if audience not in KNOWN_AUDIENCES:
        print(f"::warning::{path.name}: unknown audience '{audience}' "
              f"(1.6 clients treat unknown audiences as 'skip')")

    section = meta.get("section", "news")
    if section not in KNOWN_SECTIONS:
        print(f"::warning::{path.name}: unknown section '{section}'")

    offer = meta.get("offer")
    if offer is not None:
        if not isinstance(offer, dict):
            fail(f"{path.name}: 'offer' must be a mapping")
        starts, ends = offer.get("startsAt"), offer.get("endsAt")
        if not isinstance(starts, datetime) or not isinstance(ends, datetime):
            fail(f"{path.name}: offer.startsAt/endsAt must be ISO datetimes")
        if ends <= starts:
            fail(f"{path.name}: offer.endsAt must be after offer.startsAt")

    push = meta.get("push")
    if push is not None and not isinstance(push, dict):
        fail(f"{path.name}: 'push' must be a mapping")

    entry = normalize(meta)
    entry.setdefault("audience", "all")
    entry.setdefault("section", "news")
    entry["body"] = match.group(2).strip()
    return entry


def main() -> None:
    if not POSTS_DIR.is_dir():
        fail(f"posts directory missing: {POSTS_DIR}")

    posts, seen_ids = [], set()
    for path in sorted(POSTS_DIR.glob("*.md")):
        entry = parse_post(path)
        post_id = str(entry["id"])
        if post_id in seen_ids:
            fail(f"{path.name}: duplicate id '{post_id}'")
        seen_ids.add(post_id)
        posts.append(entry)

    posts.sort(key=lambda p: str(p["date"]), reverse=True)
    feed = {
        "version": 1,
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "posts": posts,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(f"Wrote {OUT_PATH.relative_to(ROOT)} with {len(posts)} post(s)")


if __name__ == "__main__":
    main()
