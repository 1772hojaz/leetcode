#!/bin/python3

class Solution:
    def solve(l1,l2):
        dummy_head = ListNode()
        current = dummy_head
        carry = 0

        while l1 or l2 or carry:
            x = l1.val if l1 else 0
            y = l2.val if l2 else 0

            total = x + y + carry

            current.next = ListNode(total%10)
            current = current.next

            carry = total//10

            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next
        return head.next

if __name__ == "__main__":
    sol = Solution()

    tests = [
        (([2, 4, 3], [5, 6, 4]), [7, 0, 8]),
        (([0], [0]), [0]),
        (([9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9]), [8, 9, 9, 9, 0, 0, 0, 1]),
    ]

    for args, expected in tests:
        l1, l2 = [L.list_to_linked(a) for a in args]
        result = sol.solve(l1, l2)
        result_list = L.linked_to_list(result)
        assert result_list == expected, f"solve{args} = {result_list}, expected {expected}"

    print("All tests passed.")

