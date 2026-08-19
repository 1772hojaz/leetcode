"""
1. Two Sum
https://leetcode.com/problems/two-sum/
"""

class Solution:
    def solve(self, nums, target):
        raise NotImplementedError


if __name__ == "__main__":
    sol = Solution()

    tests = [
        (([2, 7, 11, 15], 9), [0, 1]),
        (([3, 2, 4], 6), [1, 2]),
        (([3, 3], 6), [0, 1]),
    ]

    for args, expected in tests:
        result = sol.solve(*args)
        assert result == expected, f"solve{args} = {result}, expected {expected}"

    print("All tests passed.")
