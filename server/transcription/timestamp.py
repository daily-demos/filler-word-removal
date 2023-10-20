"""This module provides a linked list implementation to record start and end timestamps"""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class Timestamp:
    """Class representing a single timestamp"""
    next: Timestamp = None
    prev: Timestamp = None
    start = 0
    end = 0

    def __init__(self, start, end):
        self.start = start
        self.end = end


@dataclasses.dataclass
class Timestamps:
    """Class representing a rudimentary linked list of timestamps"""
    head: Timestamp = None
    tail: Timestamp = None
    count = 0

    def add(self, start, end):
        """Add a timestmp to the list"""
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
