"""Solution file stubs per language."""
from __future__ import annotations


def _pascal_case(slug: str) -> str:
    return "".join(part.capitalize() for part in slug.split("-"))


def _python_template(number, slug, title, param_names=None, examples=None) -> str:
    header = f'"""\n{number}. {title}\nhttps://leetcode.com/problems/{slug}/\n"""\n\n\n'
    params = ", ".join(param_names) if param_names else ""
    sig = f"    def solve(self{', ' + params if params else ''}):"

    lines = [header.rstrip("\n"), "", "class Solution:", sig, "        raise NotImplementedError", "", ""]
    lines += ['if __name__ == "__main__":', "    sol = Solution()"]

    if examples:
        lines.append("")
        lines.append("    tests = [")
        for ex in examples:
            args = ex["input"]
            args_repr = ", ".join(repr(v) for v in args)
            if len(args) == 1:
                args_repr += ","
            lines.append(f"        (({args_repr}), {ex['output']!r}),")
        lines.append("    ]")
        lines.append("")
        lines.append("    for args, expected in tests:")
        lines.append("        result = sol.solve(*args)")
        lines.append("        assert result == expected, f\"solve{args} = {result}, expected {expected}\"")
        lines.append("")
        lines.append('    print("All tests passed.")')

    return "\n".join(lines) + "\n"


SOLUTION_TEMPLATES = {
    "python": _python_template,
    "javascript": lambda number, slug, title, param_names=None, examples=None: f"""/**
 * {number}. {title}
 * https://leetcode.com/problems/{slug}/
 */

var solve = function () {{

}};

module.exports = solve;
""",
    "java": lambda number, slug, title, param_names=None, examples=None: f"""// {number}. {title}
// https://leetcode.com/problems/{slug}/

class Solution {{
    public void solve() {{

    }}
}}
""",
    "cpp": lambda number, slug, title, param_names=None, examples=None: f"""// {number}. {title}
// https://leetcode.com/problems/{slug}/

class Solution {{
public:
    void solve() {{

    }}
}};
""",
    "go": lambda number, slug, title, param_names=None, examples=None: f"""// {number}. {title}
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


def render_solution(
    language: str,
    number: int,
    slug: str,
    title: str,
    param_names: list[str] | None = None,
    examples: list[dict] | None = None,
) -> str:
    try:
        template = SOLUTION_TEMPLATES[language]
    except KeyError:
        raise ValueError(
            f"Unsupported language '{language}'. Choose from: {', '.join(SOLUTION_TEMPLATES)}"
        )
    return template(number, slug, title, param_names, examples)


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
