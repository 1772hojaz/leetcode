#!/bin/python3
from node import ListNode as L
"""
2. Add Two Numbers
https://leetcode.com/problems/add-two-number
"""
class Solution:
    def solve(self, l1, l2):
        head = L()
        current = head
        carry = 0

        while l1 or l2 or carry:
            x = l1.val if l1 else 0
            y = l2.val if l2 else 0

            total = x + y + carry
            current.next = L(total%10)
            current = current.next
            carry = total//10

            if l1 :
                l1 =l1.next
            if l2 :
                l2 = l2.next
        return head.next
