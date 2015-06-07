class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def add(self, node):
        if self.head is None:
            self.head = node
            self.tail = node
            return

        self.tail.next = node
        node.prev = self.tail
        self.tail = node

    def remove(self, node):
        prev_node = node.prev
        next_node = node.next

        if prev_node is None:
            if self.head != node:
                raise (RuntimeError, "Node contained no previous node and was not the head of the list.")
            self.head = next_node
            next_node.prev = None

        elif next_node is None:
            if self.tail != node:
                raise (RuntimeError, "Node contained no next node and was not the tail of the list.")
            self.tail = prev_node
            prev_node.next = None

        else:
            prev_node.next = next_node
            next_node.prev = prev_node

        node.prev = None
        node.next = None

    def insert(self, node, before):
        prev_node = before.prev

        if prev_node is None:
            if self.head != before:
                raise (RuntimeError, "Before contained no previous node and was not the head of the list.")
            self.head.prev = node
            self.head = node
            node.prev = None
            node.next = before
        else:
            prev_node.next = node
            node.prev = prev_node
            before.prev = node
            node.next = before


if __name__ == "__main__":
    def print_forward(linked_list):
        print('-' * 20 + 'Forwards' + '-' * 20)
        curr_node = linked_list.head
        while curr_node is not None:
            print(curr_node.value, end=" ")
            curr_node = curr_node.next
        print("")

    def print_backwards(linked_list):
        print('-' * 20 + 'Backwards' + '-' * 20)
        curr_node = linked_list.tail
        while curr_node is not None:
            print(curr_node.value, end=" ")
            curr_node = curr_node.prev
        print("")

    print('-' * 20 + 'Linked List' + '-' * 20)
    linked_list = LinkedList()
    [linked_list.add(Node(x)) for x in range(1, 11)]

    print_forward(linked_list)
    print_backwards(linked_list)

    print('-' * 20 + 'Remove Middle' + '-' * 20)
    curr_node = linked_list.head
    while curr_node is not None and curr_node.value != 5:
        curr_node = curr_node.next
    linked_list.remove(curr_node)
    print('curr_node: ' + str(curr_node.value) + ' next: ' + str(curr_node.next) + ' prev: ' + str(curr_node.prev))

    print_forward(linked_list)
    print_backwards(linked_list)

    print('-' * 20 + 'Remove Head' + '-' * 20)
    curr_node = linked_list.head
    linked_list.remove(curr_node)
    print('curr_node: ' + str(curr_node.value) + ' next: ' + str(curr_node.next) + ' prev: ' + str(curr_node.prev))

    print_forward(linked_list)
    print_backwards(linked_list)

    print('-' * 20 + 'Remove Tail' + '-' * 20)
    curr_node = linked_list.tail
    linked_list.remove(curr_node)
    print('curr_node: ' + str(curr_node.value) + ' next: ' + str(curr_node.next) + ' prev: ' + str(curr_node.prev))

    print_forward(linked_list)
    print_backwards(linked_list)

    print('-' * 20 + 'Insert Middle' + '-' * 20)
    curr_node = linked_list.head
    while curr_node is not None and curr_node.value != 6:
        curr_node = curr_node.next
    linked_list.insert(Node(5), curr_node)

    print_forward(linked_list)
    print_backwards(linked_list)

    print('-' * 20 + 'Insert Head' + '-' * 20)
    linked_list.insert(Node(1), linked_list.head)

    print_forward(linked_list)
    print_backwards(linked_list)

    print('-' * 20 + 'Insert Tail' + '-' * 20)
    linked_list.insert(Node(8.5), linked_list.tail)

    print_forward(linked_list)
    print_backwards(linked_list)
