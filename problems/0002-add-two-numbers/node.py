#!/bin/python3

class ListNode():
    """
    the class of a linked list
    Attributes:
        val: the value of the node
        next: the pointer of the node
    """
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def list_to_linked(values):
        """
        makes an array into a linked list
        Args:
            values: the array
        Retutrns:
            dummy.next:the linked list
        """
        dummy = ListNode()
        current = dummy
        for v in values:
            current.next = ListNode(v)
            current = current.next
        return dummy.next

    def linked_to_list(node):
        """
        changes a linked list into an array
        Args:
            node: the linked list
        Returns:
            results: the array
        """
        result = []
        while node:
            result.append(node.val)
            node = node.next
        return result
