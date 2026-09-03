#!/bin/python3
from node import ListNode as LinkedList
"""
This is a solution for adding two linked lists.
Args:
    l1: is the first linked list
    l2: is the second linked list

Return:
    head.next: Is the head of the actual linked list solution because head is the dummy one
"""

class Solution:
    def add(self, l1, l2):
        head = LinkedList()
        current = head
        carry = 0

        while l1 or l2 or carry:
            x  = l1.val if l1 else 0
            y = l2.val if l2 else 0

            total = x + y + carry
            carry = total//10

            current.next = LinkedList(total%10)
            current = current.next

            #Do not forget the to change the linked lists that ou are adding
            if l1:
                l1 = l1.next
            if l2:
                l2 = l2.next

        return head.next
