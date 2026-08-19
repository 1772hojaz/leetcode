"""Best-effort fetching of problem metadata from LeetCode's public endpoints.

Everything here is optional: if the network is unavailable or the shape of
the response changes, callers fall back to a blank scaffold.
"""
from __future__ import annotations

import ast
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional

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
    param_names: list = field(default_factory=list)
    examples: list = field(default_factory=list)
    hints: list = field(default_factory=list)


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


def _split_top_level(text: str, sep: str = ",") -> list[str]:
    """Split on `sep` but ignore separators nested inside brackets."""
    parts, depth, current = [], 0, []
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return [p.strip() for p in parts if p.strip()]


def _parse_value(raw: str) -> Any:
    raw = raw.strip()
    if "=" in raw.split("(")[0]:
        raw = raw.split("=", 1)[1].strip()
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return raw


_EXAMPLE_RE = re.compile(r"Input:\s*(.+?)\s*\nOutput:\s*(.+?)(?:\n|$)")


def parse_examples(content_text: str) -> list[dict]:
    """Best-effort extraction of (input, output) pairs from the prose examples."""
    examples = []
    for m in _EXAMPLE_RE.finditer(content_text or ""):
        input_raw, output_raw = m.groups()
        try:
            output = ast.literal_eval(output_raw.strip())
        except (ValueError, SyntaxError):
            continue
        args = [_parse_value(p) for p in _split_top_level(input_raw)]
        if not args:
            continue
        examples.append({"input": args, "output": output})
    return examples


def parse_param_names(meta_data_raw: str, arity: int) -> list[str]:
    try:
        meta = json.loads(meta_data_raw or "{}")
    except (ValueError, TypeError):
        meta = {}
    names = [p.get("name") for p in meta.get("params", []) if p.get("name")]
    if len(names) == arity:
        return names
    return [f"arg{i}" for i in range(arity)]


def fetch_by_slug(slug: str) -> Optional[ProblemMeta]:
    query = {
        "query": (
            "query questionData($titleSlug: String!) { "
            "question(titleSlug: $titleSlug) { "
            "questionFrontendId title titleSlug difficulty content "
            "metaData topicTags { name } hints } }"
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
    content_text = _strip_html(q.get("content", ""))
    examples = parse_examples(content_text)
    param_names = parse_param_names(q.get("metaData", ""), len(examples[0]["input"])) if examples else []
    hints = [_strip_html(h) for h in (q.get("hints") or [])]
    return ProblemMeta(
        number=number,
        slug=q.get("titleSlug", slug),
        title=q.get("title", slug),
        difficulty=q.get("difficulty", "Unknown"),
        tags=[t["name"] for t in q.get("topicTags", [])],
        content_text=content_text,
        param_names=param_names,
        examples=examples,
        hints=hints,
    )


def fetch_by_number(number: int) -> Optional[ProblemMeta]:
    slug = lookup_slug_by_number(number)
    if not slug:
        return None
    return fetch_by_slug(slug)
