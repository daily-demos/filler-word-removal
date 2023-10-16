from __future__ import annotations


class Timestamp:
    next: Timestamp = None
    prev: Timestamp = None
    start = 0
    end = 0

    def __init__(self, start, end):
        self.start = start
        self.end = end


class Timestamps:
    head: Timestamp = None
    tail: Timestamp = None
    count = 0

    def add(self, start, end):
        self.count += 1
        if not self.head:
            self.head = Timestamp(start, end)
            self.tail = self.head
            return self.tail
        new_tail = Timestamp(start, end)
        self.tail.next = new_tail
        new_tail.prev = self.tail
        self.tail = new_tail
        return self.tail
