"""
heap_manager.py - Priority Queue using Python's heapq
Implements a max-heap by negating priority values.
"""

import heapq

class PriorityQueue:
    def __init__(self):
        self._heap = []
        self._counter = 0  # Tie-breaker for equal priorities

    def push(self, task):
        """
        Push task onto heap.
        We negate priority so heapq (min-heap) behaves as max-heap.
        """
        # (-priority, counter, task) — counter breaks ties
        heapq.heappush(self._heap, (-task.priority, self._counter, task))
        self._counter += 1

    def pop(self):
        """Pop and return highest-priority task."""
        if self.is_empty():
            return None
        _, _, task = heapq.heappop(self._heap)
        return task

    def peek(self):
        """Return highest-priority task without removing."""
        if self.is_empty():
            return None
        return self._heap[0][2]

    def is_empty(self):
        return len(self._heap) == 0

    def size(self):
        return len(self._heap)

    def __repr__(self):
        tasks = sorted(self._heap, key=lambda x: x[0])
        return "PQ[" + " → ".join(t[2].name for t in tasks) + "]"