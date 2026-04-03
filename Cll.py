


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None  # Points to next node (last node points back to head)


class CircularLinkedList:
    def __init__(self):
        self.head = None
        self._size = 0

    # ── Size 

    def size(self):
        return self._size

    def is_empty(self):
        return self.head is None

    # ── Insert 

    def insert_at_beginning(self, data):
        """Insert a new node before the current head."""
        new_node = Node(data)
        if self.head is None:
            new_node.next = new_node          # Points to itself (circular)
            self.head = new_node
        else:
            # Find the last node (whose .next is head)
            last = self._get_last_node()
            new_node.next = self.head
            last.next = new_node              # Last node now points to new head
            self.head = new_node
        self._size += 1
        return new_node

    def insert_at_end(self, data):
        """Insert a new node after the last node."""
        new_node = Node(data)
        if self.head is None:
            new_node.next = new_node
            self.head = new_node
        else:
            last = self._get_last_node()
            new_node.next = self.head         # New node points back to head
            last.next = new_node              # Old last now points to new node
        self._size += 1
        return new_node

    def insert_at_position(self, data, position):
        """
        Insert at a specific position (0-indexed).
        Position 0 = beginning, position >= size = end.
        """
        if position <= 0:
            return self.insert_at_beginning(data)
        if position >= self._size:
            return self.insert_at_end(data)

        new_node = Node(data)
        current = self.head
        for _ in range(position - 1):        # Walk to node just before position
            current = current.next
        new_node.next = current.next
        current.next = new_node
        self._size += 1
        return new_node

    # ── Delete 

    def delete_by_value(self, data):
        """
        Remove the first node with matching data.
        Returns the deleted node's data, or None if not found.
        """
        if self.head is None:
            return None

        # Special case: only one node
        if self._size == 1:
            if self.head.data == data:
                deleted = self.head.data
                self.head = None
                self._size -= 1
                return deleted
            return None

        # Deleting the head node
        if self.head.data == data:
            last = self._get_last_node()
            deleted = self.head.data
            last.next = self.head.next        # Last node now points to new head
            self.head = self.head.next
            self._size -= 1
            return deleted

        # Search for the node
        current = self.head
        while current.next != self.head:
            if current.next.data == data:
                deleted = current.next.data
                current.next = current.next.next
                self._size -= 1
                return deleted
            current = current.next

        return None                           # Not found

    def delete_at_position(self, position):
        """Delete node at a specific position (0-indexed)."""
        if self.head is None or position < 0 or position >= self._size:
            return None

        if position == 0:
            return self.delete_by_value(self.head.data)

        current = self.head
        for _ in range(position - 1):
            current = current.next

        deleted = current.next.data
        current.next = current.next.next
        self._size -= 1
        return deleted

    # ── Search & Traverse 

    def search(self, data):
        """
        Search for a value.
        Returns (found: bool, position: int, steps: list of node data visited).
        """
        if self.head is None:
            return False, -1, []

        steps = []
        current = self.head
        position = 0

        while True:
            steps.append(current.data)
            if current.data == data:
                return True, position, steps
            current = current.next
            position += 1
            if current == self.head:          # Completed one full loop
                break

        return False, -1, steps

    def to_list(self):
        """Return all node values as a Python list (head first)."""
        if self.head is None:
            return []
        result = []
        current = self.head
        while True:
            result.append(current.data)
            current = current.next
            if current == self.head:
                break
        return result

    def get_nodes(self):
        """Return all Node objects in order (for the visualizer)."""
        if self.head is None:
            return []
        nodes = []
        current = self.head
        while True:
            nodes.append(current)
            current = current.next
            if current == self.head:
                break
        return nodes

    # ── Reverse 

    def reverse(self):
        """
        Reverse the circular linked list in-place.
        Returns a list of (prev, current, next_node) tuples for step animation.
        """
        if self.head is None or self._size == 1:
            return []

        steps = []                            # For step-by-step animation
        prev = None
        current = self.head
        next_node = None
        original_head = self.head

        for _ in range(self._size):
            next_node = current.next
            current.next = prev
            steps.append((
                prev.data if prev else None,
                current.data,
                next_node.data if next_node != original_head else "HEAD"
            ))
            prev = current
            current = next_node

        # Fix the circular connections
        self.head.next = prev                 # Old head's next → new last (prev)
        self.head = prev                      # New head is the old last node
        # Find new last node and point it back to new head
        new_last = original_head
        new_last.next = self.head

        return steps

    # ── Internal Helpers 

    def _get_last_node(self):
        """Traverse to the last node (the one pointing back to head)."""
        if self.head is None:
            return None
        current = self.head
        while current.next != self.head:
            current = current.next
        return current

    def __str__(self):
        if self.head is None:
            return "Empty list"
        values = self.to_list()
        return " → ".join(str(v) for v in values) + f" → (back to {values[0]})"