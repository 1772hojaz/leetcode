"""
2. Add Two Numbers
https://leetcode.com/problems/add-two-numbers/
"""

class Solution:
    def solve(self, l1, l2):
        raise NotImplementedError


if __name__ == "__main__":
    sol = Solution()

    tests = [
        (([2, 4, 3], [5, 6, 4]), [7, 0, 8]),
        (([0], [0]), [0]),
        (([9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]), [8, 9, 9, 9, 0, 0, 0, 1]),
    ]

    for args, expected in tests:
        result = sol.solve(*args)
        assert result == expected, f"solve{args} = {result}, expected {expected}"

    print("All tests passed.")
