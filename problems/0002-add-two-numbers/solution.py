#!/bin/python3
from node import ListNode

class Solution:
    """
    Represents the solution for adding two linked lists
    """
    def solve(self, l1,l2):
        """
        Adds two linked lists

        Args:
        l1: the fist linked list
        l2: the seconde linked list

        Returns: the sum of l1 and l2
        """
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
        return dummy_head.next
