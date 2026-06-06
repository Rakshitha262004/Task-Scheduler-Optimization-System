"""
validator.py - Input validation
Ensures all tasks have valid fields before processing.
"""

def validate_tasks(tasks):
    """
    Validates a list of Task objects.
    Returns (valid_tasks, rejected_tasks) tuple.
    """
    valid    = []
    rejected = []

    for task in tasks:
        errors = []

        if not task.name or not isinstance(task.name, str):
            errors.append("Invalid name")
        if not (1 <= task.priority <= 10):
            errors.append(f"Priority {task.priority} out of range [1-10]")
        if task.deadline <= 0:
            errors.append(f"Deadline {task.deadline} must be > 0")
        if task.exec_time <= 0:
            errors.append(f"Exec time {task.exec_time} must be > 0")
        if task.exec_time > task.deadline:
            errors.append("Exec time exceeds deadline — impossible to schedule")
        if task.profit < 0:
            errors.append("Profit cannot be negative")

        if errors:
            print(f"  [REJECTED] Task '{task.name}': {', '.join(errors)}")
            rejected.append((task, errors))
        else:
            valid.append(task)

    return valid, rejected