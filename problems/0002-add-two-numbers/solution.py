#!/bin/python3
"
This is a solution for adding two linked lists.
Args:
    l1: is the first linked list
    l2: is the second linked list

Return:
    head.next: Is the head of the actual linked list solution because head is the dummy one
"
class Solution:
    def add(self, l1, l2):
        dumy_node = LinkedList()
        head = dummy_node
        carry = 0

        while l1 or l2 or carry:
            x  = l1.value else 0
            y = l2.value else 0

            total = x + y + carry

            head.next = LinkedList(total%10)
            head = head.next

            carry = total//10
        return head.next
