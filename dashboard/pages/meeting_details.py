"""Detailed meeting view with transcript evidence viewer and task management."""

import streamlit as st
import pandas as pd
from src.database.session import SessionLocal
from src.services.meeting_service import MeetingService
from src.services.export_service import ExportService


def render():
    st.markdown("<h1 class='main-title'>Meeting Details & Evidence Inspector</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-title'>Deep inspection of transcript segments, evidence grounding, and decisions.</p>",
        unsafe_allow_html=True,
    )

    db = SessionLocal()
    try:
        meeting_svc = MeetingService(db)
        export_svc = ExportService(db)

        all_meetings = meeting_svc.list_meetings(limit=100)
        if not all_meetings:
            st.info("No meetings found.")
            return

        meeting_options = {f"{m.title} ({m.meeting_date.strftime('%Y-%m-%d')})": m.meeting_id for m in all_meetings}
        selected_label = st.selectbox("Select Meeting", list(meeting_options.keys()))
        selected_id = meeting_options[selected_label]

        meeting = meeting_svc.get_meeting(selected_id)
        if not meeting:
            st.error("Meeting not found.")
            return

        # Header Info
        col1, col2, col3, col4 = st.columns(4)
        col1.write(f"**Date:** {meeting.meeting_date.strftime('%Y-%m-%d')}")
        col2.write(f"**Type:** {meeting.meeting_type}")
        col3.write(f"**Organizer:** {meeting.organizer or 'Unspecified'}")
        col4.write(f"**Status:** `{meeting.processing_status}`")

        # Export Buttons
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            csv_data = export_svc.export_action_items_csv(meeting.meeting_id)
            st.download_button("📥 Export Action Items (CSV)", csv_data, f"meeting_{meeting.meeting_id}_tasks.csv", "text/csv")
        with col_e2:
            json_data = export_svc.export_meeting_json(meeting.meeting_id)
            st.download_button("📥 Export Meeting (JSON)", json_data, f"meeting_{meeting.meeting_id}.json", "application/json")
        with col_e3:
            md_data = export_svc.export_meeting_markdown(meeting.meeting_id)
            st.download_button("📥 Export Summary (Markdown)", md_data, f"meeting_{meeting.meeting_id}.md", "text/markdown")

        st.divider()

        # Tabs
        tab_tasks, tab_decisions, tab_transcript = st.tabs(["✅ Action Items", "💡 Key Decisions", "📜 Segmented Transcript"])

        with tab_tasks:
            if not meeting.action_items:
                st.info("No action items extracted for this meeting.")
            else:
                for idx, task in enumerate(meeting.action_items):
                    with st.expander(f"**{task.task}** — Owner: `{task.owner or 'Unassigned'}` | Due: `{task.deadline.strftime('%Y-%m-%d') if task.deadline else 'None'}`", expanded=(idx == 0)):
                        st.write(f"**Description:** {task.description}")
                        st.write(f"**Priority:** `{task.priority}` | **Status:** `{task.status}` | **Confidence:** `{task.confidence * 100:.0f}%`")
                        if task.validation_flags:
                            st.warning(f"Validation Flags: {', '.join(task.validation_flags)}")

                        st.markdown(
                            f"<div class='evidence-quote'><b>Grounding Evidence:</b> \"{task.evidence}\"<br>"
                            f"<small>Source Segments: {task.evidence_segment_ids}</small></div>",
                            unsafe_allow_html=True,
                        )

        with tab_decisions:
            if not meeting.decisions:
                st.info("No explicit decisions recorded.")
            else:
                for dec in meeting.decisions:
                    st.markdown(f"- **Decision:** {dec.decision}")
                    st.caption(f"Evidence: \"{dec.evidence}\" | Segments: {dec.evidence_segment_ids}")

        with tab_transcript:
            if not meeting.segments:
                st.info("No transcript segments found.")
            else:
                for seg in meeting.segments:
                    st.markdown(
                        f"**[{seg.segment_id}] {seg.speaker}** ({seg.timestamp_start or ''}): {seg.cleaned_text}"
                    )

    finally:
        db.close()
