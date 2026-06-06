"""
app.py - Task Scheduler Optimization System
Streamlit Web Interface

Run:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import io
import csv

from src.task      import Task
from src.validator import validate_tasks
from src.scheduler import greedy_schedule, priority_queue_schedule

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="Task Scheduler Optimization System",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# CUSTOM CSS
# ──────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .scheduled-badge {
        background: #d4edda;
        color: #155724;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .missed-badge {
        background: #f8d7da;
        color: #721c24;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .algo-box {
        background: #e8f4f8;
        border-left: 4px solid #1f77b4;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────

st.markdown('<div class="main-header">⚙️ Task Scheduler Optimization System</div>',
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">Greedy Algorithm + Priority Queue | DSA Project</div>',
            unsafe_allow_html=True)
st.divider()

# ──────────────────────────────────────────────
# HELPER FUNCTIONS
# ──────────────────────────────────────────────

def df_to_tasks(df):
    """Convert a Pandas DataFrame to list of Task objects."""
    tasks = []
    for _, row in df.iterrows():
        tasks.append(Task(
            task_id   = int(row["task_id"]),
            name      = str(row["name"]),
            priority  = int(row["priority"]),
            deadline  = int(row["deadline"]),
            exec_time = int(row["exec_time"]),
            profit    = int(row["profit"])
        ))
    return tasks


def reset_tasks(tasks):
    """Reset scheduling state before re-running algorithm."""
    for t in tasks:
        t.scheduled  = False
        t.start_time = None
        t.end_time   = None
    return tasks


def calculate_unoptimized_score(tasks):
    """Simulate a random baseline scheduler."""
    shuffled     = tasks[:]
    random.shuffle(shuffled)
    current_time = 0
    score        = 0
    for task in shuffled:
        if current_time + task.exec_time <= task.deadline:
            score        += task.profit
            current_time += task.exec_time
    return score


def tasks_to_dataframe(scheduled, missed):
    """Convert scheduled + missed tasks to a single DataFrame."""
    rows = []
    for t in scheduled:
        rows.append({
            "Status"    : "✅ Scheduled",
            "Task ID"   : t.task_id,
            "Task Name" : t.name,
            "Priority"  : t.priority,
            "Deadline"  : t.deadline,
            "Exec Time" : t.exec_time,
            "Profit"    : t.profit,
            "Start Time": t.start_time,
            "End Time"  : t.end_time
        })
    for t in missed:
        rows.append({
            "Status"    : "❌ Missed",
            "Task ID"   : t.task_id,
            "Task Name" : t.name,
            "Priority"  : t.priority,
            "Deadline"  : t.deadline,
            "Exec Time" : t.exec_time,
            "Profit"    : t.profit,
            "Start Time": "—",
            "End Time"  : "—"
        })
    return pd.DataFrame(rows)


def build_gantt_chart(scheduled):
    """Build a Plotly Gantt chart from scheduled tasks."""
    if not scheduled:
        return None

    colors = {
        "high"   : "#e74c3c",
        "medium" : "#f39c12",
        "low"    : "#2ecc71"
    }

    fig = go.Figure()

    for task in scheduled:
        if task.priority >= 8:
            color = colors["high"]
            level = "High Priority"
        elif task.priority >= 5:
            color = colors["medium"]
            level = "Medium Priority"
        else:
            color = colors["low"]
            level = "Low Priority"

        fig.add_trace(go.Bar(
            name       = task.name,
            x          = [task.end_time - task.start_time],
            y          = [task.name],
            base       = [task.start_time],
            orientation= "h",
            marker_color = color,
            hovertemplate = (
                f"<b>{task.name}</b><br>"
                f"Priority: {task.priority}<br>"
                f"Time: {task.start_time} → {task.end_time}<br>"
                f"Profit: {task.profit}<br>"
                f"Level: {level}<br>"
                "<extra></extra>"
            )
        ))

    fig.update_layout(
        title       = "📅 Gantt Chart — Execution Timeline",
        xaxis_title = "Time Units",
        yaxis_title = "Tasks",
        barmode     = "overlay",
        height      = max(300, len(scheduled) * 45 + 100),
        showlegend  = False,
        plot_bgcolor= "#f9f9f9",
        xaxis       = dict(showgrid=True, gridcolor="#ddd"),
        yaxis       = dict(showgrid=False),
        margin      = dict(l=20, r=20, t=50, b=40)
    )
    return fig


def build_profit_chart(scheduled, missed):
    """Bar chart comparing profit: scheduled vs missed."""
    all_tasks = scheduled + missed
    names     = [t.name[:15] for t in all_tasks]
    profits   = [t.profit for t in all_tasks]
    statuses  = ["Scheduled" if t.scheduled else "Missed"
                 for t in all_tasks]

    df = pd.DataFrame({
        "Task"  : names,
        "Profit": profits,
        "Status": statuses
    })

    fig = px.bar(
        df, x="Task", y="Profit", color="Status",
        color_discrete_map={
            "Scheduled": "#2ecc71",
            "Missed"   : "#e74c3c"
        },
        title="💰 Profit Distribution — Scheduled vs Missed",
        labels={"Profit": "Profit Value", "Task": "Task Name"},
        height=400
    )
    fig.update_layout(
        plot_bgcolor = "#f9f9f9",
        xaxis_tickangle = -35,
        legend_title = "Status"
    )
    return fig


def build_score_comparison_chart(unoptimized, greedy_score, pq_score=None):
    """Horizontal bar chart comparing algorithm scores."""
    labels = ["Random (Baseline)", "Greedy Algorithm"]
    values = [unoptimized, greedy_score]
    colors = ["#95a5a6", "#2ecc71"]

    if pq_score is not None:
        labels.append("Priority Queue")
        values.append(pq_score)
        colors.append("#3498db")

    fig = go.Figure(go.Bar(
        x           = values,
        y           = labels,
        orientation = "h",
        marker_color= colors,
        text        = values,
        textposition= "outside"
    ))
    fig.update_layout(
        title       = "📊 Algorithm Score Comparison",
        xaxis_title = "Total Profit Score",
        height      = 300,
        plot_bgcolor= "#f9f9f9",
        margin      = dict(l=20, r=60, t=50, b=40)
    )
    return fig


def generate_csv_download(scheduled, missed):
    """Generate CSV bytes for download button."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Status", "Task ID", "Task Name", "Priority",
                     "Deadline", "Exec Time", "Profit",
                     "Start Time", "End Time"])
    for t in scheduled:
        writer.writerow(["SCHEDULED", t.task_id, t.name,
                         t.priority, t.deadline, t.exec_time,
                         t.profit, t.start_time, t.end_time])
    for t in missed:
        writer.writerow(["MISSED", t.task_id, t.name,
                         t.priority, t.deadline, t.exec_time,
                         t.profit, "N/A", "N/A"])
    return output.getvalue().encode("utf-8")

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("📂 Data Source")
    data_source = st.radio(
        "Choose input method:",
        ["Use sample dataset", "Upload CSV", "Manual entry"],
        index=0
    )

    st.divider()

    st.subheader("🧠 Algorithm")
    algorithm = st.selectbox(
        "Scheduling algorithm:",
        ["Greedy Job Sequencing", "Priority Queue", "Compare Both"],
        index=0
    )

    st.divider()

    st.subheader("ℹ️ About")
    st.markdown("""
    **DSA Concepts:**
    - 🔺 Max-Heap / Priority Queue
    - 🟢 Greedy Algorithm
    - 📊 Job Sequencing
    - 🔃 Sorting (O n log n)

    **Author:** Raksh  
    **College:** ACS College of Engineering  
    **VTU | 6th Semester**
    """)

# ──────────────────────────────────────────────
# DATA LOADING SECTION
# ──────────────────────────────────────────────

st.header("📥 Step 1 — Load Tasks")

df_input = None

# ── Option A: Sample dataset ──────────────────
if data_source == "Use sample dataset":
    sample_data = {
        "task_id"  : [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
        "name"     : ["Fix Critical Bug","Deploy to Production",
                      "Code Review","Write Unit Tests",
                      "Update Documentation","Security Audit",
                      "Database Optimization","UI Bug Fix",
                      "Performance Profiling","Team Meeting Prep",
                      "API Integration","Log Analysis",
                      "Backup Verification","Feature Flag Setup",
                      "Incident Report"],
        "priority" : [10,9,6,7,3,8,7,5,6,4,9,5,6,7,8],
        "deadline" : [3,5,7,4,10,6,8,5,9,2,7,11,4,6,3],
        "exec_time": [1,2,1,1,2,2,3,1,2,1,2,3,1,2,1],
        "profit"   : [100,90,50,70,20,80,65,45,55,30,85,40,60,75,95]
    }
    df_input = pd.DataFrame(sample_data)
    st.success("✅ Sample dataset loaded — 15 tasks")
    st.dataframe(df_input, use_container_width=True, hide_index=True)

# ── Option B: Upload CSV ──────────────────────
elif data_source == "Upload CSV":
    uploaded = st.file_uploader(
        "Upload your tasks CSV",
        type=["csv"],
        help="Required columns: task_id, name, priority, deadline, exec_time, profit"
    )
    if uploaded:
        df_input = pd.read_csv(uploaded)
        st.success(f"✅ Loaded {len(df_input)} tasks from uploaded file")
        st.dataframe(df_input, use_container_width=True, hide_index=True)
    else:
        st.info("⬆️ Please upload a CSV file with the required columns.")

# ── Option C: Manual entry ────────────────────
elif data_source == "Manual entry":
    st.markdown("**Add tasks manually using the form below:**")

    # Session state to accumulate manually entered tasks
    if "manual_tasks" not in st.session_state:
        st.session_state.manual_tasks = []

    with st.expander("➕ Add a New Task", expanded=True):
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        with col1:
            m_name = st.text_input("Task Name", placeholder="e.g. Fix Bug")
        with col2:
            m_priority = st.slider("Priority (1–10)", 1, 10, 5)
        with col3:
            m_deadline = st.number_input("Deadline (time units)",
                                          min_value=1, max_value=50, value=5)
        with col4:
            m_exec = st.number_input("Execution Time",
                                      min_value=1, max_value=20, value=1)
        with col5:
            m_profit = st.number_input("Profit / Score",
                                        min_value=1, max_value=200, value=50)
        with col6:
            st.write("")
            st.write("")
            if st.button("➕ Add Task", use_container_width=True):
                if m_name.strip():
                    new_id = len(st.session_state.manual_tasks) + 1
                    st.session_state.manual_tasks.append({
                        "task_id"  : new_id,
                        "name"     : m_name.strip(),
                        "priority" : m_priority,
                        "deadline" : m_deadline,
                        "exec_time": m_exec,
                        "profit"   : m_profit
                    })
                    st.success(f"Added: {m_name}")
                else:
                    st.warning("Please enter a task name.")

    if st.session_state.manual_tasks:
        df_input = pd.DataFrame(st.session_state.manual_tasks)
        st.dataframe(df_input, use_container_width=True, hide_index=True)

        if st.button("🗑️ Clear All Tasks"):
            st.session_state.manual_tasks = []
            st.rerun()
    else:
        st.info("No tasks added yet. Use the form above.")

# ──────────────────────────────────────────────
# RUN SCHEDULER
# ──────────────────────────────────────────────

st.divider()
st.header("▶️ Step 2 — Run Scheduler")

if df_input is None or df_input.empty:
    st.warning("⚠️ Please load tasks first using Step 1.")
    st.stop()

run_btn = st.button(
    "🚀 Run Scheduling Algorithm",
    type="primary",
    use_container_width=True
)

if run_btn or st.session_state.get("ran", False):
    st.session_state["ran"] = True

    # Convert DataFrame → Task objects
    tasks = df_to_tasks(df_input)

    # ── Validate ──────────────────────────────
    st.subheader("🔍 Step 3 — Validation")
    valid_tasks, rejected = validate_tasks(tasks)

    col_v1, col_v2 = st.columns(2)
    col_v1.metric("✅ Valid Tasks",    len(valid_tasks))
    col_v2.metric("❌ Rejected Tasks", len(rejected))

    if rejected:
        with st.expander("⚠️ View Rejected Tasks"):
            for task, errors in rejected:
                st.error(f"**{task.name}**: {', '.join(errors)}")

    if not valid_tasks:
        st.error("No valid tasks to schedule.")
        st.stop()

    # ── Baseline score ────────────────────────
    unoptimized_score = calculate_unoptimized_score(valid_tasks)

    # ── Run algorithm(s) ──────────────────────
    greedy_scheduled = greedy_missed = None
    pq_scheduled     = pq_missed     = None
    greedy_score     = pq_score      = 0

    if algorithm in ("Greedy Job Sequencing", "Compare Both"):
        reset_tasks(valid_tasks)
        greedy_scheduled, greedy_missed = greedy_schedule(valid_tasks)
        greedy_score = sum(t.profit for t in greedy_scheduled)

    if algorithm in ("Priority Queue", "Compare Both"):
        reset_tasks(valid_tasks)
        pq_scheduled, pq_missed = priority_queue_schedule(valid_tasks)
        pq_score = sum(t.profit for t in pq_scheduled)

    # Pick primary result for display
    if algorithm == "Priority Queue":
        primary_scheduled = pq_scheduled
        primary_missed    = pq_missed
        primary_score     = pq_score
        primary_label     = "Priority Queue"
    else:
        primary_scheduled = greedy_scheduled
        primary_missed    = greedy_missed
        primary_score     = greedy_score
        primary_label     = "Greedy"

    # ──────────────────────────────────────────
    # RESULTS TABS
    # ──────────────────────────────────────────

    st.divider()
    st.header("📊 Results")

    # ── Top KPI metrics ───────────────────────
    total   = len(valid_tasks)
    sched_n = len(primary_scheduled)
    miss_n  = len(primary_missed)
    improvement = (
        (primary_score - unoptimized_score) / unoptimized_score * 100
        if unoptimized_score > 0 else 0
    )

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Tasks",       total)
    kpi2.metric("✅ Scheduled",       sched_n)
    kpi3.metric("❌ Missed",          miss_n)
    kpi4.metric("💰 Optimized Score", primary_score)
    kpi5.metric("📈 Improvement",     f"+{improvement:.1f}%",
                delta=f"vs random: {unoptimized_score}")

    st.divider()

    # ── Tabs for detailed views ───────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📅 Gantt Chart",
        "📋 Schedule Table",
        "💰 Profit Analysis",
        "📊 Algorithm Comparison",
        "📥 Download Report"
    ])

    # ── TAB 1: Gantt Chart ────────────────────
    with tab1:
        st.subheader(f"Execution Timeline — {primary_label} Algorithm")

        if primary_scheduled:
            fig_gantt = build_gantt_chart(primary_scheduled)
            st.plotly_chart(fig_gantt, use_container_width=True)

            # Color legend
            col_l1, col_l2, col_l3 = st.columns(3)
            col_l1.markdown("🔴 **High Priority** (8–10)")
            col_l2.markdown("🟡 **Medium Priority** (5–7)")
            col_l3.markdown("🟢 **Low Priority** (1–4)")
        else:
            st.warning("No tasks were scheduled.")

        if primary_missed:
            st.subheader("❌ Missed Tasks")
            missed_df = pd.DataFrame([{
                "Task Name": t.name,
                "Priority" : t.priority,
                "Deadline" : t.deadline,
                "Exec Time": t.exec_time,
                "Profit"   : t.profit
            } for t in primary_missed])
            st.dataframe(missed_df, use_container_width=True, hide_index=True)

    # ── TAB 2: Schedule Table ─────────────────
    with tab2:
        st.subheader("Complete Schedule — All Tasks")

        result_df = tasks_to_dataframe(primary_scheduled, primary_missed)

        # Color rows by status
        def color_status(val):
            if "Scheduled" in str(val):
                return "background-color: #d4edda; color: #155724"
            elif "Missed" in str(val):
                return "background-color: #f8d7da; color: #721c24"
            return ""

        styled = result_df.style.applymap(
            color_status, subset=["Status"]
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

        # Summary boxes
        st.divider()
        sum_col1, sum_col2 = st.columns(2)

        with sum_col1:
            st.markdown("### ✅ Scheduled Tasks")
            for t in primary_scheduled:
                st.markdown(
                    f"**{t.name}** — Slot {t.start_time}→{t.end_time} "
                    f"| P={t.priority} | 💰{t.profit}"
                )

        with sum_col2:
            st.markdown("### ❌ Missed Tasks")
            if primary_missed:
                for t in primary_missed:
                    st.markdown(
                        f"**{t.name}** — Deadline: {t.deadline} "
                        f"| 💰{t.profit} lost"
                    )
            else:
                st.success("All tasks were successfully scheduled! 🎉")

    # ── TAB 3: Profit Analysis ────────────────
    with tab3:
        st.subheader("Profit Distribution")

        fig_profit = build_profit_chart(primary_scheduled, primary_missed)
        st.plotly_chart(fig_profit, use_container_width=True)

        # Profit breakdown stats
        total_possible  = sum(t.profit for t in valid_tasks)
        total_achieved  = primary_score
        total_lost      = sum(t.profit for t in primary_missed)
        efficiency      = (total_achieved / total_possible * 100
                           if total_possible > 0 else 0)

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Total Possible Profit", total_possible)
        p2.metric("Profit Achieved",       total_achieved)
        p3.metric("Profit Lost (missed)",  total_lost)
        p4.metric("Scheduling Efficiency", f"{efficiency:.1f}%")

        # Priority breakdown pie chart
        if primary_scheduled:
            pri_data = pd.DataFrame([{
                "Priority Level": (
                    "High (8-10)"   if t.priority >= 8 else
                    "Medium (5-7)"  if t.priority >= 5 else
                    "Low (1-4)"
                ),
                "Profit": t.profit
            } for t in primary_scheduled])

            pri_sum = pri_data.groupby("Priority Level")["Profit"].sum().reset_index()
            fig_pie = px.pie(
                pri_sum, names="Priority Level", values="Profit",
                title="Profit by Priority Level",
                color="Priority Level",
                color_discrete_map={
                    "High (8-10)"  : "#e74c3c",
                    "Medium (5-7)" : "#f39c12",
                    "Low (1-4)"    : "#2ecc71"
                },
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # ── TAB 4: Algorithm Comparison ───────────
    with tab4:
        st.subheader("Algorithm Performance Comparison")

        pq_s = pq_score if algorithm == "Compare Both" else None
        fig_cmp = build_score_comparison_chart(
            unoptimized_score, greedy_score, pq_s
        )
        st.plotly_chart(fig_cmp, use_container_width=True)

        # Detail comparison table
        comparison_rows = [
            {
                "Algorithm"       : "Random Baseline",
                "Score"           : unoptimized_score,
                "Tasks Scheduled" : "varies",
                "Improvement"     : "—"
            },
            {
                "Algorithm"       : "Greedy Job Sequencing",
                "Score"           : greedy_score if greedy_score else "—",
                "Tasks Scheduled" : len(greedy_scheduled) if greedy_scheduled else "—",
                "Improvement"     : (
                    f"+{(greedy_score-unoptimized_score)/unoptimized_score*100:.1f}%"
                    if greedy_score and unoptimized_score else "—"
                )
            }
        ]
        if algorithm == "Compare Both" and pq_score:
            comparison_rows.append({
                "Algorithm"       : "Priority Queue",
                "Score"           : pq_score,
                "Tasks Scheduled" : len(pq_scheduled),
                "Improvement"     : (
                    f"+{(pq_score-unoptimized_score)/unoptimized_score*100:.1f}%"
                    if unoptimized_score else "—"
                )
            })

        st.dataframe(
            pd.DataFrame(comparison_rows),
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.subheader("🧠 Algorithm Explanation")

        with st.expander("Greedy Job Sequencing with Deadlines"):
            st.markdown("""
            <div class="algo-box">
            <b>How it works:</b><br>
            1. Sort tasks by <b>profit descending</b> (greedy choice — most valuable first)<br>
            2. For each task, find the <b>latest free time slot ≤ deadline</b><br>
            3. Assign the task to that slot<br>
            4. If no free slot exists → task is <b>MISSED</b><br><br>
            <b>Time Complexity:</b> O(n²) | <b>Space:</b> O(n)<br>
            <b>Optimality:</b> Provably optimal for profit maximization
            </div>
            """, unsafe_allow_html=True)

        with st.expander("Priority Queue Scheduling"):
            st.markdown("""
            <div class="algo-box">
            <b>How it works:</b><br>
            1. Push all tasks into a <b>max-heap</b> by priority<br>
            2. Pop highest-priority task<br>
            3. If it fits before its deadline → schedule it<br>
            4. Move current time forward<br><br>
            <b>Time Complexity:</b> O(n log n) | <b>Space:</b> O(n)<br>
            <b>Trade-off:</b> Fast, but may miss more deadlines than greedy
            </div>
            """, unsafe_allow_html=True)

    # ── TAB 5: Download ───────────────────────
    with tab5:
        st.subheader("📥 Download Reports")

        csv_bytes = generate_csv_download(primary_scheduled, primary_missed)
        st.download_button(
            label     = "⬇️ Download schedule_report.csv",
            data      = csv_bytes,
            file_name = "schedule_report.csv",
            mime      = "text/csv",
            use_container_width=True
        )

        # Generate text report
        txt_lines = [
            "TASK SCHEDULER OPTIMIZATION SYSTEM — REPORT",
            "=" * 50,
            f"Algorithm      : {primary_label}",
            f"Total Tasks    : {total}",
            f"Scheduled      : {sched_n}",
            f"Missed         : {miss_n}",
            f"Optimized Score: {primary_score}",
            f"Random Score   : {unoptimized_score}",
            f"Improvement    : +{improvement:.1f}%",
            "",
            "--- SCHEDULED TASKS ---"
        ]
        for t in primary_scheduled:
            txt_lines.append(
                f"  [{t.start_time}→{t.end_time}] {t.name} "
                f"(P={t.priority}, Profit={t.profit})"
            )
        txt_lines.append("")
        txt_lines.append("--- MISSED TASKS ---")
        for t in primary_missed:
            txt_lines.append(
                f"  MISSED: {t.name} "
                f"(deadline={t.deadline}, profit={t.profit})"
            )

        txt_content = "\n".join(txt_lines).encode("utf-8")
        st.download_button(
            label     = "⬇️ Download performance_stats.txt",
            data      = txt_content,
            file_name = "performance_stats.txt",
            mime      = "text/plain",
            use_container_width=True
        )

        st.info("💡 Save these files in your `/outputs` folder and commit to GitHub as proof of output.")

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────

st.divider()
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.85rem;">
    Task Scheduler Optimization System &nbsp;|&nbsp;
    DSA Project &nbsp;|&nbsp; Greedy + Priority Queue &nbsp;|&nbsp;
    Built with Python & Streamlit
</div>
""", unsafe_allow_html=True)