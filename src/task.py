"""
task.py - Task data model
Defines the Task class used throughout the scheduler system.
"""

class Task:
    def __init__(self, task_id, name, priority, deadline, exec_time, profit):
        """
        Args:
            task_id   (int): Unique identifier
            name      (str): Task name
            priority  (int): 1 (low) to 10 (high)
            deadline  (int): Must complete by this time unit
            exec_time (int): Units of time required to execute
            profit    (int): Score/value gained if completed
        """
        self.task_id   = task_id
        self.name      = name
        self.priority  = priority
        self.deadline  = deadline
        self.exec_time = exec_time
        self.profit    = profit
        self.scheduled = False       # Tracks if task was scheduled
        self.start_time = None       # Assigned start time slot
        self.end_time   = None       # Assigned end time slot

    def __repr__(self):
        return (f"Task(id={self.task_id}, name='{self.name}', "
                f"priority={self.priority}, deadline={self.deadline}, "
                f"exec={self.exec_time}, profit={self.profit})")

    # For heap comparison — compare by priority (higher = better)
    def __lt__(self, other):
        return self.priority > other.priority  # Max-heap behavior