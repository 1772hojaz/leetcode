from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from . import api, storage, templates

REPO_ROOT = storage.REPO_ROOT


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def cmd_new(args: argparse.Namespace) -> int:
    number = args.number
    language = args.lang

    meta = None
    existing = storage.find(number)
    if existing and not args.force:
        print(f"Problem {number} already scaffolded at {existing['path']} "
              f"(use --force to re-fetch metadata, or --lang to add another language file).")
        folder = REPO_ROOT / existing["path"]
    else:
        if not args.no_fetch:
            print(f"Fetching metadata for problem {number}...")
            meta = api.fetch_by_number(number)
            if meta is None:
                print("  Could not fetch from leetcode.com (offline or rate-limited); "
                      "scaffolding a blank problem instead.")

        if meta is None:
            title = args.title or f"problem-{number}"
            slug = slugify(args.title) if args.title else f"problem-{number}"
            difficulty, tags, content = "Unknown", [], ""
        else:
            title, slug = meta.title, meta.slug
            difficulty, tags, content = meta.difficulty, meta.tags, meta.content_text

        folder = storage.PROBLEMS_DIR / f"{number:04d}-{slug}"
        folder.mkdir(parents=True, exist_ok=True)

        problem_md = folder / "problem.md"
        if not problem_md.exists():
            problem_md.write_text(
                templates.render_problem_md(number, slug, title, difficulty, tags, content)
            )

        record = storage.ProblemRecord(
            number=number,
            slug=slug,
            title=title,
            difficulty=difficulty,
            tags=tags,
            language=language,
            status="todo",
            path=str(folder.relative_to(REPO_ROOT)),
            hints=meta.hints if meta else [],
        )
        storage.upsert(record)

    ext = templates.EXTENSIONS.get(language)
    if ext is None:
        print(f"Unsupported language '{language}'. Choose from: {', '.join(templates.EXTENSIONS)}")
        return 1

    record = storage.find(number)
    sol_path = folder / f"solution.{ext}"
    if sol_path.exists() and not args.force:
        print(f"solution.{ext} already exists at {sol_path.relative_to(REPO_ROOT)}, leaving as-is.")
    else:
        param_names = meta.param_names if meta else None
        examples = meta.examples if meta else None
        sol_path.write_text(
            templates.render_solution(language, number, record["slug"], record["title"], param_names, examples)
        )
        print(f"Created {sol_path.relative_to(REPO_ROOT)}")
        if examples:
            print(f"  Baked in {len(examples)} example test case(s) from leetcode.com.")

    print(f"Problem {number} ({record['title']}) ready at {folder.relative_to(REPO_ROOT)}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    records = storage.load_index()
    if args.status:
        records = [r for r in records if r["status"] == args.status]
    if not records:
        print("No problems scaffolded yet. Try: lc new <number>")
        return 0
    width = max(len(r["title"]) for r in records)
    for r in sorted(records, key=lambda r: r["number"]):
        print(f"{r['number']:>4}  {r['title']:<{width}}  {r['difficulty']:<8}  "
              f"{r['status']:<10}  {r['language']:<10}  {r['path']}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    if not storage.set_status(args.number, args.state):
        print(f"Problem {args.number} not found. Run `lc new {args.number}` first.")
        return 1
    print(f"Problem {args.number} marked as {args.state}.")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    r = storage.find(args.number)
    if not r:
        print(f"Problem {args.number} not found. Run `lc new {args.number}` first.")
        return 1
    for k, v in r.items():
        print(f"{k:>12}: {v}")
    return 0


def cmd_hint(args: argparse.Namespace) -> int:
    record = storage.find(args.number)
    if not record:
        print(f"Problem {args.number} not found. Run `lc new {args.number}` first.")
        return 1

    if args.reset:
        storage.reset_hints(args.number)
        print(f"Hint progress reset for problem {args.number}.")
        if not args.all:
            return 0

    hints = record.get("hints") or []
    if not hints:
        print(f"Fetching hints for problem {args.number}...")
        meta = api.fetch_by_slug(record["slug"])
        if meta is None or not meta.hints:
            print("  No hints available (offline, rate-limited, or LeetCode has none for this problem).")
            return 0
        hints = meta.hints
        storage.set_hints(args.number, hints)
        record = storage.find(args.number)

    if args.all:
        print(f"All hints for problem {args.number} ({record['title']}):")
        for i, h in enumerate(hints, start=1):
            print(f"  {i}. {h}")
        return 0

    hint, revealed, total = storage.reveal_next_hint(args.number)
    if hint is None:
        print(f"No more hints left ({revealed}/{total} already revealed). "
              f"Use --reset to start over or --all to see them all.")
        return 0
    print(f"Hint {revealed}/{total}: {hint}")
    return 0


def _run_git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


def cmd_push(args: argparse.Namespace) -> int:
    status = _run_git(["status", "--porcelain"])
    if status.returncode != 0:
        print(status.stderr)
        return 1
    if not status.stdout.strip():
        print("Nothing to commit.")
        return 0

    add_target = args.path or "."
    add = _run_git(["add", add_target])
    if add.returncode != 0:
        print(add.stderr)
        return 1

    diff_cached = _run_git(["diff", "--cached", "--name-only"])
    if not diff_cached.stdout.strip():
        print("Nothing staged to commit.")
        return 0
    print("Staged files:")
    print(diff_cached.stdout)

    message = args.message
    if not message:
        if args.number is not None:
            record = storage.find(args.number)
            title = record["title"] if record else str(args.number)
            message = f"Add solution for {args.number}. {title}"
        else:
            message = "Update leetcode solutions"

    if not args.yes:
        confirm = input(f"Commit with message '{message}' and push to origin? [y/N] ")
        if confirm.strip().lower() != "y":
            print("Aborted (changes remain staged).")
            return 1

    commit = _run_git(["commit", "-m", message])
    print(commit.stdout)
    if commit.returncode != 0:
        print(commit.stderr)
        return 1

    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip() or "main"
    push = _run_git(["push", "origin", branch])
    print(push.stdout)
    print(push.stderr)
    return push.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lc",
        description="Personal LeetCode practice CLI: scaffold problems, track status, "
                     "get progressive hints, and push solutions to GitHub.",
        epilog="Run `lc <command> -h` for help on a specific command.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    p_new = sub.add_parser(
        "new",
        help="Scaffold a new problem",
        description="Scaffold a new problem: fetches title/difficulty/tags/description "
                     "from leetcode.com when online, and writes a solution stub.",
    )
    p_new.add_argument("number", type=int, help="LeetCode problem number, e.g. 1")
    p_new.add_argument("title", nargs="?", help="Title/slug hint used if fetching fails or --no-fetch is set")
    p_new.add_argument("--lang", default="python", choices=sorted(templates.EXTENSIONS),
                        help="Language for the solution stub (default: python)")
    p_new.add_argument("--no-fetch", action="store_true", help="Skip fetching metadata from leetcode.com")
    p_new.add_argument("--force", action="store_true", help="Overwrite an existing solution/metadata")
    p_new.set_defaults(func=cmd_new)

    p_list = sub.add_parser(
        "list",
        help="List scaffolded problems",
        description="List all problems that have been scaffolded with `lc new`.",
    )
    p_list.add_argument("--status", choices=storage.STATUSES, help="Only show problems with this status")
    p_list.set_defaults(func=cmd_list)

    p_status = sub.add_parser(
        "status",
        help="Update a problem's status",
        description="Update the status of a scaffolded problem (todo / attempted / solved).",
    )
    p_status.add_argument("number", type=int, help="LeetCode problem number")
    p_status.add_argument("state", choices=storage.STATUSES, help="New status to set")
    p_status.set_defaults(func=cmd_status)

    p_show = sub.add_parser(
        "show",
        help="Show stored metadata for a problem",
        description="Print everything stored in index.json for one problem.",
    )
    p_show.add_argument("number", type=int, help="LeetCode problem number")
    p_show.set_defaults(func=cmd_show)

    p_hint = sub.add_parser(
        "hint",
        help="Reveal hints for a problem, one at a time",
        description="Reveal LeetCode's official hints for a problem, one at a time so you "
                     "don't spoil more than you need. Hints are fetched from leetcode.com on "
                     "first use and cached in index.json; how many you've revealed is also "
                     "tracked there so repeated calls advance through the list.",
        epilog=(
            "Examples:\n"
            "  lc hint 1            # reveal the next not-yet-seen hint for problem 1\n"
            "  lc hint 1            # run again to reveal the one after that\n"
            "  lc hint 1 --all      # show every hint at once, without affecting progress\n"
            "  lc hint 1 --reset    # forget revealed progress and start over\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_hint.add_argument("number", type=int, help="LeetCode problem number")
    p_hint.add_argument("--all", action="store_true", help="Show all hints at once instead of just the next one")
    p_hint.add_argument("--reset", action="store_true",
                         help="Reset revealed-hint progress for this problem back to zero")
    p_hint.set_defaults(func=cmd_hint)

    p_push = sub.add_parser(
        "push",
        help="Commit local changes and push to GitHub",
        description="Commit local changes (optionally scoped to one problem) and push to origin.",
    )
    p_push.add_argument("-m", "--message", help="Commit message (default: auto-generated)")
    p_push.add_argument("-n", "--number", type=int, help="Problem number (used to build a default commit message)")
    p_push.add_argument("--path", help="Restrict `git add` to this path (default: whole repo)")
    p_push.add_argument("-y", "--yes", action="store_true", help="Skip the confirmation prompt")
    p_push.set_defaults(func=cmd_push)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
