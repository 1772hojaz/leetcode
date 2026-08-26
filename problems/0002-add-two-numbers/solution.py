#!/bin/python3
"""
2. Add Two Numbers
https://leetcode.com/problems/add-two-number
"""
class Solution:
    def solve(self, l1, l2):
        head = ListNode()
        current = heas
        carry = 0

        while l1 or l2 or carry:
            x = l1.val if l1 else 0
            y = l2.val if l2 else 0

            total = x + y + carry
            current.next = ListNode(total%10)
            current = current.next
            carry = total//10

            if l1 :
                l1 =l1.next
            if l2 :
                l2 = l2.next
        return head.next1


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

