"""Analytics and cross-meeting duplicate intelligence dashboard page."""

import streamlit as st
import pandas as pd
from src.database.session import SessionLocal
from src.services.analytics_service import AnalyticsService
from src.deduplication.duplicate_detector import detect_duplicates_and_conflicts
from src.database.models import ActionItem
from dashboard.components import (
    plot_status_distribution,
    plot_owner_workload,
    plot_priority_distribution,
)


def render():
    st.markdown("<h1 class='main-title'>Analytics & Intelligence</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-title'>In-depth metrics on team workload, completion velocity, and cross-meeting duplicates.</p>",
        unsafe_allow_html=True,
    )

    db = SessionLocal()
    try:
        analytics_svc = AnalyticsService(db)
        owner_metrics = analytics_svc.get_owner_analytics()
        dist_metrics = analytics_svc.get_status_and_priority_distributions()

        tab_workload, tab_duplicates = st.tabs(["📊 Workload & Distribution", "🔍 Cross-Meeting Duplicates"])

        with tab_workload:
            col1, col2 = st.columns(2)
            with col1:
                fig_owner = plot_owner_workload(owner_metrics)
                if fig_owner:
                    st.plotly_chart(fig_owner, use_container_width=True)
                else:
                    st.info("No owner data available.")

            with col2:
                fig_status = plot_status_distribution(dist_metrics["status_counts"])
                if fig_status:
                    st.plotly_chart(fig_status, use_container_width=True)
                else:
                    st.info("No status distribution available.")

            st.subheader("Team Member Task Breakdown")
            if owner_metrics:
                st.dataframe(pd.DataFrame(owner_metrics), use_container_width=True)
            else:
                st.info("No tasks recorded yet.")

        with tab_duplicates:
            st.subheader("Detected Cross-Meeting Duplicates & Conflicts")
            all_items = db.query(ActionItem).all()
            task_dicts = [
                {
                    "task_id": item.task_id,
                    "task": item.task,
                    "owner": item.owner,
                    "deadline": item.deadline,
                    "meeting_id": item.meeting_id,
                }
                for item in all_items
            ]
            dups = detect_duplicates_and_conflicts(task_dicts, task_dicts)

            # De-duplicate symmetric pairs
            seen = set()
            unique_dups = []
            for d in dups:
                pair = tuple(sorted([d["task_id_1"], d["task_id_2"]]))
                if pair not in seen:
                    seen.add(pair)
                    unique_dups.append(d)

            if not unique_dups:
                st.success("No cross-meeting duplicates or task conflicts detected.")
            else:
                dup_table = []
                for d in unique_dups:
                    dup_table.append({
                        "Task A": d["task_1"],
                        "Task B": d["task_2"],
                        "Similarity": f"{d['similarity_score'] * 100:.1f}%",
                        "Suggested Relationship": d["suggested_relationship"],
                    })
                st.dataframe(pd.DataFrame(dup_table), use_container_width=True)

    finally:
        db.close()
