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
