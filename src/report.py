"""
report.py - Report Generator
Saves schedule results to CSV and text files.
"""

import csv
import os
from datetime import datetime

def save_schedule_csv(scheduled, missed, output_dir="outputs"):
    """Saves the optimized schedule to a CSV file."""

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "schedule_report.csv")

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(["Status", "Task ID", "Task Name", "Priority",
                          "Deadline", "Exec Time", "Profit",
                          "Start Time", "End Time"])

        # Scheduled tasks
        for task in scheduled:
            writer.writerow([
                "SCHEDULED",
                task.task_id, task.name, task.priority,
                task.deadline, task.exec_time, task.profit,
                task.start_time, task.end_time
            ])

        # Missed tasks
        for task in missed:
            writer.writerow([
                "MISSED",
                task.task_id, task.name, task.priority,
                task.deadline, task.exec_time, task.profit,
                "N/A", "N/A"
            ])

    print(f"\n  ✅ Schedule report saved: {filepath}")
    return filepath


def save_performance_stats(scheduled, missed, optimized_score,
                           unoptimized_score, output_dir="outputs"):
    """Saves performance statistics to a text file."""

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "performance_stats.txt")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(filepath, "w") as f:
        f.write("="*60 + "\n")
        f.write("   TASK SCHEDULER OPTIMIZATION SYSTEM — REPORT\n")
        f.write(f"   Generated: {timestamp}\n")
        f.write("="*60 + "\n\n")

        f.write(f"Total Tasks         : {len(scheduled) + len(missed)}\n")
        f.write(f"Tasks Scheduled     : {len(scheduled)}\n")
        f.write(f"Tasks Missed        : {len(missed)}\n")
        f.write(f"Optimized Score     : {optimized_score}\n")
        f.write(f"Unoptimized Score   : {unoptimized_score}\n")

        if unoptimized_score > 0:
            pct = (optimized_score - unoptimized_score) / unoptimized_score * 100
            f.write(f"Improvement         : +{pct:.1f}%\n")

        f.write("\n--- SCHEDULED TASKS ---\n")
        for task in scheduled:
            f.write(f"  [{task.start_time}-{task.end_time}] "
                    f"{task.name} (P={task.priority}, Profit={task.profit})\n")

        f.write("\n--- MISSED TASKS ---\n")
        for task in missed:
            f.write(f"  MISSED: {task.name} "
                    f"(deadline={task.deadline}, profit={task.profit})\n")

    print(f"  ✅ Performance stats saved: {filepath}")
    return filepath