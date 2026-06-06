# Task Scheduler Optimization System

> A DSA-based task scheduling system that maximizes total profit/score
> using Greedy Job Sequencing and Priority Queue algorithms.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Algorithm](https://img.shields.io/badge/Algorithm-Greedy%20%2B%20Heap-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

---

## Problem Statement

Given N tasks, each with a deadline, execution time, and profit value,
schedule them to maximize total profit without missing any assigned deadline.

This mirrors real-world problems in:
- CPU process scheduling (OS)
- Cloud job queues (AWS Lambda, GCP)
- Project management (Jira, Asana)
- Hospital triage systems

---

## DSA Concepts Used

| Concept | Where Used |
|---|---|
| Max-Heap / Priority Queue | `heap_manager.py` — O(log n) task extraction |
| Greedy Algorithm | `scheduler.py` — profit-maximizing selection |
| Sorting | Tasks sorted by deadline and profit |
| Arrays | Time slot allocation array |
| OOP | `Task` class encapsulates all task data |

---

## Algorithm Explanation

### Greedy Job Sequencing with Deadlines

1. Sort all tasks by **profit descending** (greedy choice)
2. For each task, find the **latest free time slot ≤ deadline**
3. Assign the task to that slot
4. If no free slot exists → task is **missed**
5. Repeat for all tasks

**Time Complexity:** O(n²) | **Space Complexity:** O(n)

---

## Features

- Load tasks from CSV file
- Input validation with error reporting
- Greedy Job Sequencing algorithm
- Priority Queue scheduling (comparison)
- Visual Gantt chart in terminal
- Performance comparison (random vs optimized)
- CSV and text report generation
- CLI with `--algorithm`, `--input`, `--verbose` flags

---

## Folder Structure
Task-Scheduler-Optimization-System/
├── data/tasks.csv
├── src/
│   ├── task.py
│   ├── validator.py
│   ├── scheduler.py
│   ├── heap_manager.py
│   ├── timeline.py
│   └── report.py
├── outputs/
├── images/
├── main.py
├── requirements.txt
└── README.md

---

## How to Run

```bash
pip install -r requirements.txt
python main.py
python main.py --algorithm greedy --verbose
```

---

## Sample Output
Scheduled: 11 tasks | Missed: 4 tasks
Optimized Score : 765
Random Score    : 490
Improvement     : +56.1%

---

## Screenshots
|![dashboard]|![dashboard]|![dashboard]|
|------------|------------|------------|
|![Output](images/1.png)|![Output](images/2.png)|![Output](images/3.png)|
|![Output](images/4.png)|![Output](images/5.png)|![Output](images/6.png)|
|![Output](images/7.png)|![Output](images/8.png)|![Output](images/9.png)|

---
## Demo Video
link : https://drive.google.com/file/d/1moc9dfdvGYe5buRpGAcND1dD1SsThz2P/view?usp=sharing

---

## Learning Outcomes

- Implemented Max-Heap from scratch using `heapq`
- Applied Greedy algorithm to NP-adjacent scheduling problem
- Understood deadline-constrained optimization
- Practiced modular Python project structure
- Gained experience with CSV I/O and CLI argument parsing
