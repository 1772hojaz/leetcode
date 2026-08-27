#!/bin/python3

class ListNode():
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def list_to_linked(values):
        dummy = ListNode()
        current = dummy
        for v in values:
            current.next = ListNode(v)
            current = current.next
        return dummy.next

    def linked_to_list(node):
        result = []
        while node:
            result.append(node.val)
            node = node.next
        return result
