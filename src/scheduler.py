"""
scheduler.py - Greedy Job Sequencing with Deadlines Algorithm
Maximizes total profit by scheduling highest-profit tasks
within their deadline constraints.
"""

from src.heap_manager import PriorityQueue

def greedy_schedule(tasks):
    """
    Greedy Job Sequencing Algorithm.
    
    Algorithm:
    1. Sort tasks by profit (descending) — greedy choice
    2. For each task, find the latest free time slot before deadline
    3. Assign task to that slot
    4. Track scheduled vs missed tasks
    
    Time Complexity:  O(n^2) naive, O(n log n) with Union-Find
    Space Complexity: O(n) for slot array
    
    Args:
        tasks: List of validated Task objects
    
    Returns:
        (scheduled, missed): Two lists of Task objects
    """

    if not tasks:
        return [], []

    # Find maximum deadline to size our time slot array
    max_deadline = max(t.deadline for t in tasks)

    # Time slot array: slots[i] = None means slot i is free
    # Slots are 1-indexed: slots[1] to slots[max_deadline]
    slots = [None] * (max_deadline + 1)

    # Sort tasks by profit descending (greedy: pick most valuable first)
    sorted_tasks = sorted(tasks, key=lambda t: t.profit, reverse=True)

    scheduled = []
    missed    = []

    for task in sorted_tasks:
        # Find the latest available slot before or at deadline
        # We go backwards from deadline to 1 (latest slot first)
        placed = False

        for slot in range(min(task.deadline, max_deadline), 0, -1):
            if slots[slot] is None:
                # Assign task to this slot
                slots[slot] = task
                task.scheduled  = True
                task.start_time = slot - 1   # 0-indexed start
                task.end_time   = slot        # 0-indexed end
                scheduled.append(task)
                placed = True
                break

        if not placed:
            missed.append(task)

    # Sort scheduled tasks by their time slot for timeline display
    scheduled.sort(key=lambda t: t.start_time)

    return scheduled, missed


def priority_queue_schedule(tasks):
    """
    Alternative: Priority Queue based scheduling.
    Schedules tasks in order of priority using a max-heap.
    Useful for comparing results with greedy approach.
    
    Returns:
        (scheduled, missed): Two lists of Task objects
    """
    pq = PriorityQueue()
    for task in tasks:
        pq.push(task)

    current_time = 0
    scheduled    = []
    missed       = []

    while not pq.is_empty():
        task = pq.pop()

        # Check if task can finish before its deadline
        if current_time + task.exec_time <= task.deadline:
            task.scheduled  = True
            task.start_time = current_time
            task.end_time   = current_time + task.exec_time
            current_time    = task.end_time
            scheduled.append(task)
        else:
            missed.append(task)

    return scheduled, missed