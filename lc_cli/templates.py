"""Solution file stubs per language."""
from __future__ import annotations


def _pascal_case(slug: str) -> str:
    return "".join(part.capitalize() for part in slug.split("-"))


SOLUTION_TEMPLATES = {
    "python": lambda number, slug, title: f'''"""
{number}. {title}
https://leetcode.com/problems/{slug}/
"""


class Solution:
    def solve(self):
        raise NotImplementedError


if __name__ == "__main__":
    sol = Solution()
''',
    "javascript": lambda number, slug, title: f"""/**
 * {number}. {title}
 * https://leetcode.com/problems/{slug}/
 */

var solve = function () {{

}};

module.exports = solve;
""",
    "java": lambda number, slug, title: f"""// {number}. {title}
// https://leetcode.com/problems/{slug}/

class Solution {{
    public void solve() {{

    }}
}}
""",
    "cpp": lambda number, slug, title: f"""// {number}. {title}
// https://leetcode.com/problems/{slug}/

class Solution {{
public:
    void solve() {{

    }}
}};
""",
    "go": lambda number, slug, title: f"""// {number}. {title}
// https://leetcode.com/problems/{slug}/

package main

func solve() {{

}}
""",
}

EXTENSIONS = {
    "python": "py",
    "javascript": "js",
    "java": "java",
    "cpp": "cpp",
    "go": "go",
}


def render_solution(language: str, number: int, slug: str, title: str) -> str:
    try:
        template = SOLUTION_TEMPLATES[language]
    except KeyError:
        raise ValueError(
            f"Unsupported language '{language}'. Choose from: {', '.join(SOLUTION_TEMPLATES)}"
        )
    return template(number, slug, title)


def render_problem_md(
    number: int,
    slug: str,
    title: str,
    difficulty: str,
    tags: list[str],
    content_text: str,
) -> str:
    tag_line = ", ".join(tags) if tags else "-"
    body = content_text if content_text else "_Description not fetched. Add notes manually or re-run `lc new` with network access._"
    return f"""# {number}. {title}

- **Difficulty:** {difficulty}
- **Tags:** {tag_line}
- **Link:** https://leetcode.com/problems/{slug}/

## Problem

{body}

## Notes

_Approach, complexity, edge cases..._
"""
