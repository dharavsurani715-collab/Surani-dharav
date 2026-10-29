import json
from datetime import date, datetime
from io import StringIO

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="LifePattern AI",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
<style>
.block-container {max-width: 1100px; padding-top: 2rem; padding-bottom: 3rem;}
.hero {padding: 1.5rem; border-radius: 18px; background: linear-gradient(120deg,#182848,#4b6cb7); color: white;}
.small-muted {color: #6b7280; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

if "records" not in st.session_state:
    st.session_state.records = []
if "feedback" not in st.session_state:
    st.session_state.feedback = []

st.markdown(
    '<div class="hero"><h1>🧠 LifePattern AI</h1>'
    '<p>Notice your patterns. Test small changes. Learn from your outcomes.</p></div>',
    unsafe_allow_html=True,
)
st.caption("V1 prototype • Insights are based only on the records you enter; they are not predictions or professional advice.")

with st.sidebar:
    st.header("Your workspace")
    st.write("Your records are kept in this browser session.")
    st.warning("For this prototype, data is temporary and may disappear when the session resets. Export your data to keep a copy. Do not enter sensitive personal information.")
    st.subheader("Backup / restore")
    export_obj = {"records": st.session_state.records, "feedback": st.session_state.feedback}
    st.download_button(
        "Download my backup (JSON)",
        data=json.dumps(export_obj, indent=2, ensure_ascii=False),
        file_name="lifepattern_backup.json",
        mime="application/json",
        use_container_width=True,
    )
    uploaded = st.file_uploader("Restore a JSON backup", type=["json"])
    if uploaded is not None:
        try:
            loaded = json.load(uploaded)
            if not isinstance(loaded.get("records", []), list) or not isinstance(loaded.get("feedback", []), list):
                raise ValueError("Unexpected backup format")
            st.session_state.records = loaded.get("records", [])
            st.session_state.feedback = loaded.get("feedback", [])
            st.success("Backup restored into this session.")
        except Exception:
            st.error("That backup file could not be read.")
    if st.button("Clear this session's data", use_container_width=True):
        st.session_state.records = []
        st.session_state.feedback = []
        st.rerun()

tab_log, tab_insights, tab_feedback, tab_history = st.tabs(
    ["✍️ Daily log", "🔎 Patterns", "🧪 Suggestion feedback", "📚 History"]
)

with tab_log:
    st.subheader("Record an experience")
    with st.form("daily_log_form", clear_on_submit=True):
        log_date = st.date_input("Date", value=date.today())
        goal = st.text_input("Goal or project", placeholder="e.g., Study Python")
        planned = st.number_input("Tasks planned", min_value=0, max_value=100, value=3, step=1)
        completed = st.number_input("Tasks completed", min_value=0, max_value=100, value=2, step=1)
        obstacle = st.selectbox(
            "Main obstacle (if any)",
            ["None / not sure", "Task felt too large", "Distractions", "Low energy", "Not enough time", "Unclear next step", "Other"],
        )
        note = st.text_area("Optional note", placeholder="What did you notice? Avoid private or sensitive details.")
        submitted = st.form_submit_button("Save record", type="primary", use_container_width=True)
    if submitted:
        if not goal.strip():
            st.error("Please enter a goal or project.")
        elif completed > planned:
            st.error("Tasks completed cannot exceed tasks planned.")
        else:
            st.session_state.records.append({
                "date": log_date.isoformat(),
                "goal": goal.strip(),
                "planned": int(planned),
                "completed": int(completed),
                "obstacle": obstacle,
                "note": note.strip(),
            })
            st.success("Record added to this session.")
            st.rerun()

with tab_insights:
    st.subheader("Patterns from your records")
    records = st.session_state.records
    if not records:
        st.info("Add at least one daily log to begin. More records make patterns more meaningful.")
    else:
        df = pd.DataFrame(records)
        planned_total = int(df["planned"].sum())
        completed_total = int(df["completed"].sum())
        rate = (completed_total / planned_total * 100) if planned_total else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Days / logs recorded", len(df))
        c2.metric("Tasks completed", f"{completed_total} / {planned_total}")
        c3.metric("Overall completion", f"{rate:.0f}%" if planned_total else "No planned tasks")
        st.write("**Completion by date**")
        by_date = df.groupby("date", as_index=False)[["planned", "completed"]].sum().sort_values("date")
        by_date = by_date.set_index("date")
        st.bar_chart(by_date)
        st.write("**Goal summary**")
        by_goal = df.groupby("goal", as_index=False)[["planned", "completed"]].sum()
        by_goal["completion_rate_%"] = by_goal.apply(
            lambda row: round(row["completed"] / row["planned"] * 100, 1) if row["planned"] else None,
            axis=1,
        )
        st.dataframe(by_goal, use_container_width=True, hide_index=True)

        st.write("**Evidence-based observations**")
        if len(df) < 3:
            st.info("This is an early sample. Add records on more days before treating any pattern as reliable.")
        else:
            obstacle_df = df[df["obstacle"] != "None / not sure"]
            if not obstacle_df.empty:
                counts = obstacle_df["obstacle"].value_counts()
                top_obstacle = counts.index[0]
                st.write(f"- Your most frequently recorded obstacle is **{top_obstacle}** ({int(counts.iloc[0])} log(s)).")
            goal_rates = df.groupby("goal").apply(
                lambda g: (g["completed"].sum() / g["planned"].sum() * 100) if g["planned"].sum() else None,
                include_groups=False,
            ).dropna()
            if not goal_rates.empty:
                st.write(f"- Among goals with planned tasks, **{goal_rates.idxmax()}** has the highest recorded completion rate ({goal_rates.max():.0f}%). This is descriptive, not proof that the goal is easier.")
            st.write("- Compare similar days and goals before deciding what caused a result. These records show associations, not necessarily causes.")

        st.write("**A small experiment to try**")
        if planned_total == 0:
            st.write("Try recording one small, measurable task next time.")
        elif rate < 50:
            st.write("For your next log, try planning fewer tasks or breaking one large task into smaller steps. Record the outcome to see whether it helps.")
        elif rate < 80:
            st.write("For your next log, choose the single most important task first and leave a little buffer time. Compare the result with your previous logs.")
        else:
            st.write("Your recorded completion rate is relatively high. Keep the plan realistic and test whether the same approach works across different days.")

with tab_feedback:
    st.subheader("Did a suggestion help?")
    st.write("Feedback lets you compare recommendations with what happened afterward.")
    with st.form("feedback_form", clear_on_submit=True):
        suggestion = st.text_input("Suggestion you tried", placeholder="e.g., Break a project into 3 smaller tasks")
        outcome = st.radio("What happened?", ["Helped", "No noticeable difference", "Made things harder", "Not tried yet"], horizontal=False)
        feedback_note = st.text_area("Optional note")
        feedback_submit = st.form_submit_button("Save feedback", type="primary", use_container_width=True)
    if feedback_submit:
        if not suggestion.strip():
            st.error("Please enter the suggestion.")
        else:
            st.session_state.feedback.append({
                "date": date.today().isoformat(),
                "suggestion": suggestion.strip(),
                "outcome": outcome,
                "note": feedback_note.strip(),
            })
            st.success("Feedback saved to this session.")
            st.rerun()
    if st.session_state.feedback:
        st.divider()
        st.dataframe(pd.DataFrame(st.session_state.feedback), use_container_width=True, hide_index=True)
        helped = sum(1 for item in st.session_state.feedback if item["outcome"] == "Helped")
        decided = sum(1 for item in st.session_state.feedback if item["outcome"] != "Not tried yet")
        st.metric("Suggestions marked as helpful", f"{helped} / {decided}" if decided else "No tried suggestions yet")

with tab_history:
    st.subheader("Your saved-in-session records")
    if st.session_state.records:
        st.dataframe(pd.DataFrame(st.session_state.records), use_container_width=True, hide_index=True)
        csv_data = pd.DataFrame(st.session_state.records).to_csv(index=False)
        st.download_button("Download records as CSV", csv_data, "lifepattern_records.csv", "text/csv")
    else:
        st.info("Your history will appear here after you add a record.")

st.divider()
st.caption("LifePattern AI V1 • This is a prototype, not a medical, mental-health, financial, or other professional decision-making system.")
