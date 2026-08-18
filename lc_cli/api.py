"""Best-effort fetching of problem metadata from LeetCode's public endpoints.

Everything here is optional: if the network is unavailable or the shape of
the response changes, callers fall back to a blank scaffold.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Optional

ALL_PROBLEMS_URL = "https://leetcode.com/api/problems/all/"
GRAPHQL_URL = "https://leetcode.com/graphql"
TIMEOUT = 8
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; lc-cli/0.1)",
    "Content-Type": "application/json",
}


@dataclass
class ProblemMeta:
    number: int
    slug: str
    title: str
    difficulty: str = "Unknown"
    tags: list = field(default_factory=list)
    content_text: str = ""


def _get_json(url: str, data: Optional[dict] = None) -> Optional[dict]:
    try:
        if data is not None:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=HEADERS,
                method="POST",
            )
        else:
            req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None


def lookup_slug_by_number(number: int) -> Optional[str]:
    """Look up a problem's title-slug from its frontend id via the bulk list."""
    payload = _get_json(ALL_PROBLEMS_URL)
    if not payload:
        return None
    for entry in payload.get("stat_status_pairs", []):
        stat = entry.get("stat", {})
        if stat.get("frontend_question_id") == number:
            return stat.get("question__title_slug")
    return None


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", "", html or "")
    text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'")
    lines = [line.strip() for line in text.splitlines()]
    cleaned = []
    for line in lines:
        if line or (cleaned and cleaned[-1]):
            cleaned.append(line)
    return "\n".join(cleaned).strip()


def fetch_by_slug(slug: str) -> Optional[ProblemMeta]:
    query = {
        "query": (
            "query questionData($titleSlug: String!) { "
            "question(titleSlug: $titleSlug) { "
            "questionFrontendId title titleSlug difficulty content "
            "topicTags { name } } }"
        ),
        "variables": {"titleSlug": slug},
    }
    payload = _get_json(GRAPHQL_URL, query)
    if not payload:
        return None
    q = (payload.get("data") or {}).get("question")
    if not q:
        return None
    try:
        number = int(q["questionFrontendId"])
    except (KeyError, TypeError, ValueError):
        return None
    return ProblemMeta(
        number=number,
        slug=q.get("titleSlug", slug),
        title=q.get("title", slug),
        difficulty=q.get("difficulty", "Unknown"),
        tags=[t["name"] for t in q.get("topicTags", [])],
        content_text=_strip_html(q.get("content", "")),
    )


def fetch_by_number(number: int) -> Optional[ProblemMeta]:
    slug = lookup_slug_by_number(number)
    if not slug:
        return None
    return fetch_by_slug(slug)
