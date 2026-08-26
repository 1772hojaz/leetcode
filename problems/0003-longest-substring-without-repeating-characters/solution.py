"""
3. Longest Substring Without Repeating Characters
https://leetcode.com/problems/longest-substring-without-repeating-characters/
"""

class Solution:
    def solve(self, s):
        raise NotImplementedError


if __name__ == "__main__":
    sol = Solution()

    tests = [
        (('abcabcbb',), 3),
        (('bbbbb',), 1),
        (('pwwkew',), 3),
    ]

    for args, expected in tests:
        result = sol.solve(*args)
        assert result == expected, f"solve{args} = {result}, expected {expected}"

    print("All tests passed.")
