#!/bin/python3
from node import ListNode
from solution import Solution

if __name__ == "__main__":
    sol = Solution()

    tests = [
        (([2, 4, 3], [5, 6, 4]), [7, 0, 8]),
        (([0], [0]), [0]),
        (([9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]), [8, 9, 9, 9, 0, 0, 0, 1]),
    ]

    for args, expected in tests:
        l1, l2 = [ListNode.list_to_linked(a) for a in args]
        result = sol.solve(l1, l2)
        result_list = ListNode.linked_to_list(result)
        assert result_list == expected, f"solve{args} = {result_list}, expected {expected}"

    print("All tests passed.")
