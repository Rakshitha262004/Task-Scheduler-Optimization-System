"""
timeline.py - Execution Timeline Visualizer
Builds and displays a visual execution timeline.
"""

from colorama import Fore, Style, init
init(autoreset=True)

def build_timeline(scheduled, missed, max_time=20):
    """
    Builds a visual timeline of scheduled tasks.
    
    Args:
        scheduled: List of scheduled Task objects
        missed:    List of missed Task objects
        max_time:  Width of timeline display
    """

    print("\n" + "="*65)
    print("          ⏱  EXECUTION TIMELINE")
    print("="*65)

    if not scheduled:
        print("  No tasks were scheduled.")
        return

    # Print column headers
    print(f"  {'TASK NAME':<25} {'START':>5} {'END':>5} {'PRIORITY':>8} {'PROFIT':>7}")
    print("  " + "-"*60)

    for task in scheduled:
        bar_start  = task.start_time
        bar_end    = task.end_time
        bar_length = bar_end - bar_start

        # Color by priority level
        if task.priority >= 8:
            color = Fore.RED
        elif task.priority >= 5:
            color = Fore.YELLOW
        else:
            color = Fore.GREEN

        bar = color + "█" * min(bar_length * 3, 20) + Style.RESET_ALL

        print(f"  {task.name:<25} {bar_start:>5} {bar_end:>5} "
              f"{task.priority:>8} {task.profit:>7}  {bar}")

    # Visual Gantt-style bar
    print("\n  GANTT CHART:")
    print("  Time:", end=" ")
    for i in range(max_time + 1):
        print(f"{i:<3}", end="")
    print()

    for task in scheduled:
        label = task.name[:12].ljust(14)
        print(f"  {label}", end="")
        for t in range(max_time):
            if task.start_time <= t < task.end_time:
                print(Fore.CYAN + "███" + Style.RESET_ALL, end="")
            else:
                print("   ", end="")
        print()

    # Missed tasks
    if missed:
        print(f"\n  {Fore.RED}✗ MISSED TASKS:{Style.RESET_ALL}")
        for task in missed:
            print(f"    - {task.name} (deadline={task.deadline}, "
                  f"profit={task.profit})")

    print("="*65)


def print_comparison(unoptimized_score, optimized_score, total_tasks,
                     scheduled_count, missed_count):
    """Prints performance comparison between random and optimized."""

    print("\n" + "="*65)
    print("          📊 PERFORMANCE COMPARISON")
    print("="*65)
    print(f"  Total Tasks Submitted  : {total_tasks}")
    print(f"  Tasks Scheduled        : {Fore.GREEN}{scheduled_count}{Style.RESET_ALL}")
    print(f"  Tasks Missed           : {Fore.RED}{missed_count}{Style.RESET_ALL}")
    print(f"  Unoptimized Score      : {Fore.YELLOW}{unoptimized_score}{Style.RESET_ALL}")
    print(f"  Optimized Score        : {Fore.GREEN}{optimized_score}{Style.RESET_ALL}")

    if unoptimized_score > 0:
        improvement = ((optimized_score - unoptimized_score)
                       / unoptimized_score * 100)
        print(f"  Improvement            : "
              f"{Fore.CYAN}+{improvement:.1f}%{Style.RESET_ALL}")

    print("="*65)