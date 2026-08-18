# leetcode

Personal LeetCode practice repo with a small CLI (`lc`) that scaffolds
problems locally, tracks their status, and pushes solutions to GitHub.

## Setup

```bash
pip install -e .
```

This installs the `lc` command (via `lc_cli/`).

## Usage

```bash
# Scaffold a new problem — fetches title/difficulty/tags/description
# from leetcode.com when online, and writes a solution stub.
lc new 1                       # defaults to Python
lc new 1 --lang java
lc new 9999 "My Custom Title" --no-fetch   # offline / not-yet-public problem

# List problems you've scaffolded
lc list
lc list --status solved

# Mark progress
lc status 1 attempted
lc status 1 solved

# Inspect stored metadata for one problem
lc show 1

# Commit + push everything (or just one problem) to GitHub
lc push                        # commit all changes, confirm, then push
lc push --number 1             # commit only problems/0001-two-sum, with an auto message
lc push -m "custom message" -y # skip the confirmation prompt
```

Each problem lives under `problems/<number>-<slug>/`:

```
problems/0001-two-sum/
  problem.md     # description, tags, difficulty, link
  solution.py    # your solution
```

An `index.json` at the repo root tracks number, title, difficulty, tags,
language, and status (`todo` / `attempted` / `solved`) for every scaffolded
problem.

Supported `--lang` values: `python`, `javascript`, `java`, `cpp`, `go`.
