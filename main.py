"""
main.py - Task Scheduler Optimization System
Entry point: loads tasks, runs scheduling algorithms,
displays results, and saves reports.

Usage:
    python main.py
    python main.py --input data/tasks.csv --verbose
"""

import argparse
import csv
import random
from colorama import Fore, Style, init

from src.task       import Task
from src.validator  import validate_tasks
from src.scheduler  import greedy_schedule, priority_queue_schedule
from src.timeline   import build_timeline, print_comparison
from src.report     import save_schedule_csv, save_performance_stats

init(autoreset=True)

# ─────────────────────────────────────────────
# BANNER
# ─────────────────────────────────────────────

def print_banner():
    print(Fore.CYAN + """
╔══════════════════════════════════════════════════════════╗
║     TASK SCHEDULER OPTIMIZATION SYSTEM                  ║
║     DSA Project — Greedy Algorithm + Priority Queue     ║
║     Author: Raksh | VTU | ACS College of Engineering   ║
╚══════════════════════════════════════════════════════════╝
""" + Style.RESET_ALL)


# ─────────────────────────────────────────────
# LOAD TASKS FROM CSV
# ─────────────────────────────────────────────

def load_tasks_from_csv(filepath):
    """Loads tasks from a CSV file and returns list of Task objects."""
    tasks = []
    try:
        with open(filepath, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                task = Task(
                    task_id   = int(row["task_id"]),
                    name      = row["name"],
                    priority  = int(row["priority"]),
                    deadline  = int(row["deadline"]),
                    exec_time = int(row["exec_time"]),
                    profit    = int(row["profit"])
                )
                tasks.append(task)
        print(f"  ✅ Loaded {len(tasks)} tasks from '{filepath}'")
    except FileNotFoundError:
        print(f"  ❌ File not found: {filepath}")
    except KeyError as e:
        print(f"  ❌ Missing column in CSV: {e}")
    return tasks


# ─────────────────────────────────────────────
# DISPLAY TASK TABLE
# ─────────────────────────────────────────────

def display_task_table(tasks, title="TASK LIST"):
    """Prints a formatted table of tasks."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)
    print(f"  {'ID':<4} {'NAME':<25} {'PRI':>4} {'DL':>4} "
          f"{'EXEC':>5} {'PROFIT':>7}")
    print("  " + "-"*65)
    for t in tasks:
        print(f"  {t.task_id:<4} {t.name:<25} {t.priority:>4} "
              f"{t.deadline:>4} {t.exec_time:>5} {t.profit:>7}")
    print("="*70)


# ─────────────────────────────────────────────
# CALCULATE UNOPTIMIZED SCORE (baseline)
# ─────────────────────────────────────────────

def calculate_unoptimized_score(tasks):
    """
    Simulates a naive random scheduler to produce a baseline score.
    Shuffles tasks and takes them in random order until time runs out.
    """
    shuffled    = tasks[:]
    random.shuffle(shuffled)
    current_time = 0
    score        = 0

    for task in shuffled:
        if current_time + task.exec_time <= task.deadline:
            score        += task.profit
            current_time += task.exec_time

    return score


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Task Scheduler Optimization System"
    )
    parser.add_argument(
        "--input", default="data/tasks.csv",
        help="Path to task CSV file (default: data/tasks.csv)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show extra debug information"
    )
    parser.add_argument(
        "--algorithm", choices=["greedy", "priority", "both"],
        default="both",
        help="Scheduling algorithm to use (default: both)"
    )
    args = parser.parse_args()

    print_banner()

    # ── Step 1: Load tasks ──────────────────────────────
    print(f"\n{'─'*60}")
    print("  STEP 1: LOADING TASKS")
    print(f"{'─'*60}")
    tasks = load_tasks_from_csv(args.input)

    if not tasks:
        print("  No tasks to process. Exiting.")
        return

    display_task_table(tasks, "RAW TASK INPUT")

    # ── Step 2: Validate tasks ──────────────────────────
    print(f"\n{'─'*60}")
    print("  STEP 2: VALIDATING TASKS")
    print(f"{'─'*60}")
    valid_tasks, rejected = validate_tasks(tasks)
    print(f"  Valid: {len(valid_tasks)} | Rejected: {len(rejected)}")

    if not valid_tasks:
        print("  No valid tasks after validation. Exiting.")
        return

    # ── Step 3: Sort by deadline ────────────────────────
    print(f"\n{'─'*60}")
    print("  STEP 3: SORTING BY DEADLINE")
    print(f"{'─'*60}")
    sorted_by_deadline = sorted(valid_tasks, key=lambda t: t.deadline)
    display_task_table(sorted_by_deadline, "TASKS SORTED BY DEADLINE")

    # ── Step 4: Baseline score ──────────────────────────
    print(f"\n{'─'*60}")
    print("  STEP 4: CALCULATING BASELINE (UNOPTIMIZED) SCORE")
    print(f"{'─'*60}")
    unoptimized_score = calculate_unoptimized_score(valid_tasks)
    print(f"  Random/Unoptimized Score: {Fore.YELLOW}{unoptimized_score}{Style.RESET_ALL}")

    # ── Step 5: Greedy Scheduling ───────────────────────
    if args.algorithm in ("greedy", "both"):
        print(f"\n{'─'*60}")
        print("  STEP 5A: GREEDY JOB SEQUENCING ALGORITHM")
        print(f"{'─'*60}")

        # Reset scheduling state for fresh run
        for t in valid_tasks:
            t.scheduled  = False
            t.start_time = None
            t.end_time   = None

        greedy_scheduled, greedy_missed = greedy_schedule(valid_tasks)
        greedy_score = sum(t.profit for t in greedy_scheduled)

        print(f"  Scheduled: {len(greedy_scheduled)} tasks")
        print(f"  Missed   : {len(greedy_missed)} tasks")
        print(f"  Total Score: {Fore.GREEN}{greedy_score}{Style.RESET_ALL}")

        build_timeline(greedy_scheduled, greedy_missed)
        print_comparison(unoptimized_score, greedy_score,
                         len(valid_tasks), len(greedy_scheduled),
                         len(greedy_missed))

        save_schedule_csv(greedy_scheduled, greedy_missed)
        save_performance_stats(greedy_scheduled, greedy_missed,
                               greedy_score, unoptimized_score)

    # ── Step 6: Priority Queue Scheduling ──────────────
    if args.algorithm in ("priority", "both"):
        print(f"\n{'─'*60}")
        print("  STEP 5B: PRIORITY QUEUE SCHEDULING ALGORITHM")
        print(f"{'─'*60}")

        for t in valid_tasks:
            t.scheduled  = False
            t.start_time = None
            t.end_time   = None

        pq_scheduled, pq_missed = priority_queue_schedule(valid_tasks)
        pq_score = sum(t.profit for t in pq_scheduled)

        print(f"  Scheduled: {len(pq_scheduled)} tasks")
        print(f"  Missed   : {len(pq_missed)} tasks")
        print(f"  PQ Score : {Fore.CYAN}{pq_score}{Style.RESET_ALL}")

        if args.verbose:
            build_timeline(pq_scheduled, pq_missed)

    # ── Summary ─────────────────────────────────────────
    print(f"\n{'═'*60}")
    print("  ✅ SCHEDULER RUN COMPLETE")
    print(f"  Reports saved in: outputs/")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    main()