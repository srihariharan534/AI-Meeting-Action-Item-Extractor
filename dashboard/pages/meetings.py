"""Meeting repository exploration page."""

import streamlit as st
import pandas as pd
from src.database.session import SessionLocal
from src.services.meeting_service import MeetingService


def render():
    st.markdown("<h1 class='main-title'>Meetings Directory</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-title'>Browse all recorded meetings and view extraction summaries.</p>",
        unsafe_allow_html=True,
    )

    db = SessionLocal()
    try:
        meeting_svc = MeetingService(db)
        meetings = meeting_svc.list_meetings(limit=100)

        if not meetings:
            st.info("No meetings recorded. Please upload a meeting first.")
            return

        search = st.text_input("🔍 Search Meetings by Title or Project", "")

        filtered = [
            m for m in meetings
            if search.lower() in m.title.lower() or (m.project_name and search.lower() in m.project_name.lower())
        ]

        table_rows = []
        for m in filtered:
            table_rows.append({
                "Meeting ID": m.meeting_id,
                "Title": m.title,
                "Date": m.meeting_date.strftime("%Y-%m-%d"),
                "Type": m.meeting_type,
                "Organizer": m.organizer or "N/A",
                "Project": m.project_name or "N/A",
                "Status": m.processing_status,
                "Action Items": len(m.action_items),
                "Decisions": len(m.decisions),
            })

        df = pd.DataFrame(table_rows)
        st.dataframe(df, use_container_width=True)

        st.caption("Copy a Meeting ID to inspect full transcript segments and tasks in the 'Meeting Details' page.")

    finally:
        db.close()
