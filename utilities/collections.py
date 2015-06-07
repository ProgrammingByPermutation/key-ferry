class Node:
    """
    Class presenting a single node in a doubly linked list.
    """

    def __init__(self, value):
        """
        Initializes a new instance of the Node class.
        :param value: The value to store in the node.
        """
        self.value = value
        self.next = None
        self.prev = None


class LinkedList:
    """
    Class presenting a doubly linked list.
    """

    def __init__(self, copy=None):
        """
        Initializes a new instance of the LinkedList class.
        :param copy: The collection to copy.
        """
        self.head = None
        self.tail = None

        # Copy the collection
        if copy is not None:
            [self.add_data(x) for x in copy]

    def add_data(self, data):
        """
        Creates a new node from the passed in data and appends it to the end of the list.
        :param data: The data to store in the Node object.
        """
        self.add_node(Node(data))

    def remove_data(self, data):
        """
        Removes the node with the passed in data from the list. If multiple nodes contain the same data, only the first
        will be removed.
        :param data: The data to remove.
        """
        node = self.find(data)
        if node is None:
            raise RuntimeError("Attempt to remove nonexistent data from the collection: " + str(data))
        self.remove_node(node)

    def insert_data(self, data, before):
        """
        Creates a new node from the passed in data and attaches it before the passed in data.
        :param data: The data to store in the Node object.
        :param before: The data that the new node should be inserted before.
        """
        node = self.find(before)
        if node is None:
            raise RuntimeError("Attempt to insert before nonexistent data from the collection: " + str(data))
        self.insert_node(Node(data), node)

    def add_node(self, node):
        """
        Appends a node to the end of the collection.
        :param node: The node to append to the collection.
        """
        if self.head is None:
            self.head = node
            self.tail = node
            return

        self.tail.next = node
        node.prev = self.tail
        self.tail = node

    def remove_node(self, node):
        """
        Removes a node from the collection.
        :param node: The node to remove.
        """
        prev_node = node.prev
        next_node = node.next

        if prev_node is None:
            if self.head != node:
                raise RuntimeError("Node contained no previous node and was not the head of the list.")
            self.head = next_node
            next_node.prev = None

        elif next_node is None:
            if self.tail != node:
                raise RuntimeError("Node contained no next node and was not the tail of the list.")
            self.tail = prev_node
            prev_node.next = None

        else:
            prev_node.next = next_node
            next_node.prev = prev_node

        node.prev = None
        node.next = None

    def insert_node(self, node, before):
        """
        Inserts a node before another node in the collection.
        :param node: The node to insert.
        :param before: The node it should be inserted before.
        """
        prev_node = before.prev

        if prev_node is None:
            if self.head != before:
                raise RuntimeError("Before contained no previous node and was not the head of the list.")
            self.head.prev = node
            self.head = node
            node.prev = None
            node.next = before
        else:
            prev_node.next = node
            node.prev = prev_node
            before.prev = node
            node.next = before

    def find(self, data):
        """
        Finds the node with a given piece of data in the collection. If multiple nodes contains the same data only the
        first node will be returned.
        :param data: The data to search for in the collection.
        """
        node = self.head
        while node is not None:
            if node.value == data:
                return node
            node = node.next


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

    def verify_forward(linked_list, expected_list):
        curr_node = linked_list.head
        msg = ""
        for value in expected_list:
            if value != curr_node.value:
                raise RuntimeError("Expected: " + str(value) + " Received: " + str(curr_node.value))
            curr_node = curr_node.next
            msg += ' ' + str(value)
        if curr_node is not None:
            raise RuntimeError("More entries in actual value than expected")
        print('Successfully verified: ' + msg)

    def verify_backwards(linked_list, expected_list):
        curr_node = linked_list.tail
        msg = ""
        for value in expected_list:
            if value != curr_node.value:
                raise RuntimeError("Expected: " + str(value) + " Received: " + str(curr_node.value))
            curr_node = curr_node.prev
            msg += ' ' + str(value)
        if curr_node is not None:
            raise RuntimeError("More entries in actual value than expected")
        print('Successfully verified: ' + msg)

    print('-' * 20 + 'Linked List Node Methods' + '-' * 20)
    linked_list = LinkedList()
    [linked_list.add_node(Node(x)) for x in range(1, 11)]

    verify_forward(linked_list, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    verify_backwards(linked_list, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])

    print('-' * 20 + 'Remove Middle' + '-' * 20)
    curr_node = linked_list.head
    while curr_node is not None and curr_node.value != 5:
        curr_node = curr_node.next
    linked_list.remove_node(curr_node)

    verify_forward(linked_list, [1, 2, 3, 4, 6, 7, 8, 9, 10])
    verify_backwards(linked_list, [10, 9, 8, 7, 6, 4, 3, 2, 1])

    print('-' * 20 + 'Remove Head' + '-' * 20)
    curr_node = linked_list.head
    linked_list.remove_node(curr_node)

    verify_forward(linked_list, [2, 3, 4, 6, 7, 8, 9, 10])
    verify_backwards(linked_list, [10, 9, 8, 7, 6, 4, 3, 2])

    print('-' * 20 + 'Remove Tail' + '-' * 20)
    curr_node = linked_list.tail
    linked_list.remove_node(curr_node)

    verify_forward(linked_list, [2, 3, 4, 6, 7, 8, 9])
    verify_backwards(linked_list, [9, 8, 7, 6, 4, 3, 2])

    print('-' * 20 + 'Insert Middle' + '-' * 20)
    curr_node = linked_list.head
    while curr_node is not None and curr_node.value != 6:
        curr_node = curr_node.next
    linked_list.insert_node(Node(5), curr_node)

    verify_forward(linked_list, [2, 3, 4, 5, 6, 7, 8, 9])
    verify_backwards(linked_list, [9, 8, 7, 6, 5, 4, 3, 2])

    print('-' * 20 + 'Insert Head' + '-' * 20)
    linked_list.insert_node(Node(1), linked_list.head)

    verify_forward(linked_list, [1, 2, 3, 4, 5, 6, 7, 8, 9])
    verify_backwards(linked_list, [9, 8, 7, 6, 5, 4, 3, 2, 1])

    print('-' * 20 + 'Insert Tail' + '-' * 20)
    linked_list.insert_node(Node(8.5), linked_list.tail)

    verify_forward(linked_list, [1, 2, 3, 4, 5, 6, 7, 8, 8.5, 9])
    verify_backwards(linked_list, [9, 8.5, 8, 7, 6, 5, 4, 3, 2, 1])

    print('-' * 20 + 'Linked List Data Methods' + '-' * 20)
    linked_list = LinkedList()
    [linked_list.add_data(x) for x in range(1, 11)]

    verify_forward(linked_list, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    verify_backwards(linked_list, [10, 9, 8, 7, 6, 5, 4, 3, 2, 1])

    print('-' * 20 + 'Remove Middle' + '-' * 20)
    linked_list.remove_data(5)

    verify_forward(linked_list, [1, 2, 3, 4, 6, 7, 8, 9, 10])
    verify_backwards(linked_list, [10, 9, 8, 7, 6, 4, 3, 2, 1])

    print('-' * 20 + 'Remove Head' + '-' * 20)
    linked_list.remove_data(1)

    verify_forward(linked_list, [2, 3, 4, 6, 7, 8, 9, 10])
    verify_backwards(linked_list, [10, 9, 8, 7, 6, 4, 3, 2])

    print('-' * 20 + 'Remove Tail' + '-' * 20)
    linked_list.remove_data(10)

    verify_forward(linked_list, [2, 3, 4, 6, 7, 8, 9])
    verify_backwards(linked_list, [9, 8, 7, 6, 4, 3, 2])

    print('-' * 20 + 'Insert Middle' + '-' * 20)
    linked_list.insert_data(5, 6)

    verify_forward(linked_list, [2, 3, 4, 5, 6, 7, 8, 9])
    verify_backwards(linked_list, [9, 8, 7, 6, 5, 4, 3, 2])

    print('-' * 20 + 'Insert Head' + '-' * 20)
    linked_list.insert_data(1, 2)

    verify_forward(linked_list, [1, 2, 3, 4, 5, 6, 7, 8, 9])
    verify_backwards(linked_list, [9, 8, 7, 6, 5, 4, 3, 2, 1])

    print('-' * 20 + 'Insert Tail' + '-' * 20)
    linked_list.insert_data(8.5, 9)

    verify_forward(linked_list, [1, 2, 3, 4, 5, 6, 7, 8, 8.5, 9])
    verify_backwards(linked_list, [9, 8.5, 8, 7, 6, 5, 4, 3, 2, 1])
