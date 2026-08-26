"""
4. Median of Two Sorted Arrays
https://leetcode.com/problems/median-of-two-sorted-arrays/
"""

class Solution:
    def solve(self, nums1, nums2):
        raise NotImplementedError


if __name__ == "__main__":
    sol = Solution()

    tests = [
        (([1, 3], [2]), 2.0),
        (([1, 2], [3, 4]), 2.5),
    ]

    for args, expected in tests:
        result = sol.solve(*args)
        assert result == expected, f"solve{args} = {result}, expected {expected}"

    print("All tests passed.")
