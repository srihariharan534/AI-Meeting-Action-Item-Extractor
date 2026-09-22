"""Overview KPI dashboard page."""

import streamlit as st
import pandas as pd
from src.database.session import SessionLocal
from src.services.analytics_service import AnalyticsService
from src.services.meeting_service import MeetingService
from dashboard.components import plot_status_distribution, plot_priority_distribution


def render():
    st.markdown("<h1 class='main-title'>System Overview</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-title'>Real-time KPI metrics and action item execution health.</p>",
        unsafe_allow_html=True,
    )

    db = SessionLocal()
    try:
        analytics_svc = AnalyticsService(db)
        meeting_svc = MeetingService(db)

        kpis = analytics_svc.get_overview()

        # Row 1: KPI Cards
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Meetings", kpis["total_meetings"])
        col2.metric("Total Action Items", kpis["total_action_items"])
        col3.metric("Completed Tasks", kpis["completed_tasks"])
        col4.metric("Pending Tasks", kpis["pending_tasks"])
        col5.metric("Overdue Tasks", kpis["overdue_tasks"], delta_color="inverse")

        col6, col7, col8, col9, col10 = st.columns(5)
        col6.metric("In Progress", kpis["in_progress_tasks"])
        col7.metric("Unassigned Tasks", kpis["unassigned_tasks"])
        col8.metric("Review Queue", kpis["review_required_tasks"])
        col9.metric("High Priority", kpis["high_priority_tasks"])
        col10.metric("Avg Confidence", f"{kpis['average_confidence'] * 100:.0f}%")

        st.divider()

        # Row 2: Charts
        col_c1, col_c2 = st.columns(2)
        dist = analytics_svc.get_status_and_priority_distributions()
        with col_c1:
            fig_status = plot_status_distribution(dist["status_counts"])
            if fig_status:
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("No tasks recorded yet.")

        with col_c2:
            fig_pri = plot_priority_distribution(dist["priority_counts"])
            if fig_pri:
                st.plotly_chart(fig_pri, use_container_width=True)
            else:
                st.info("No tasks recorded yet.")

        st.divider()

        # Row 3: Recent Meetings
        st.subheader("Recent Ingested Meetings")
        recent = meeting_svc.list_meetings(limit=5)
        if recent:
            table_data = []
            for m in recent:
                table_data.append({
                    "Meeting ID": m.meeting_id[:8] + "...",
                    "Title": m.title,
                    "Date": m.meeting_date.strftime("%Y-%m-%d"),
                    "Type": m.meeting_type,
                    "Status": m.processing_status,
                    "Tasks Count": len(m.action_items),
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True)
        else:
            st.info("No meetings ingested yet. Go to 'Upload Meeting' to get started!")

    finally:
        db.close()
