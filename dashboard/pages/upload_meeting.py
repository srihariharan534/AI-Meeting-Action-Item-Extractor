"""Meeting upload and interactive ingestion page."""

from datetime import datetime
import streamlit as st
from src.database.session import SessionLocal
from src.services.meeting_service import MeetingService
from src.services.extraction_service import ExtractionService
from src.ingestion.loaders import load_transcript_file


def render():
    st.markdown("<h1 class='main-title'>Upload Meeting Transcript</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-title'>Ingest audio transcripts (TXT, PDF, DOCX) or paste raw conversation text.</p>",
        unsafe_allow_html=True,
    )

    tab_paste, tab_file = st.tabs(["📝 Paste Transcript", "📁 Upload File"])

    transcript_content = ""
    source_filename = None

    with tab_paste:
        pasted_text = st.text_area(
            "Meeting Transcript",
            placeholder="Priya: We need to finalize the marketing report.\nArun: I will prepare the report by Friday.\nMeena: I will review it next Monday.",
            height=240,
        )
        if pasted_text.strip():
            transcript_content = pasted_text.strip()

    with tab_file:
        uploaded_file = st.file_uploader(
            "Upload transcript document (.txt, .pdf, .docx)",
            type=["txt", "pdf", "docx"],
        )
        if uploaded_file is not None:
            source_filename = uploaded_file.name
            bytes_data = uploaded_file.read()
            try:
                transcript_content = load_transcript_file(bytes_data, uploaded_file.name)
                st.success(f"Loaded {len(transcript_content)} characters from '{uploaded_file.name}'")
            except Exception as e:
                st.error(f"Error parsing file: {e}")

    # Metadata Form
    st.subheader("Meeting Metadata")
    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Meeting Title", value="Sprint Planning & Q3 Review")
        meeting_date = st.date_input("Meeting Date", value=datetime.utcnow().date())
        meeting_type = st.selectbox(
            "Meeting Type",
            [
                "Sprint review",
                "Stand-up",
                "Project review",
                "Planning meeting",
                "Client meeting",
                "Brainstorming",
                "Retrospective",
                "General meeting",
            ],
        )

    with col2:
        organizer = st.text_input("Organizer", value="Priya")
        participants_str = st.text_input("Participants (comma-separated)", value="Priya, Arun, Meena, Rohan")
        project_name = st.text_input("Project / Team Name", value="Core Engine")

    provider_choice = st.selectbox(
        "AI Provider Engine",
        ["mock", "rule", "openai"],
        help="Select 'mock' or 'rule' for instant offline extraction without API keys. Select 'openai' for cloud LLM.",
    )

    if st.button("🚀 Ingest & Extract Action Items", type="primary", use_container_width=True):
        if not transcript_content:
            st.warning("Please provide transcript text or upload a file.")
            return

        db = SessionLocal()
        try:
            with st.spinner("Segmenting transcript and running AI extraction pipeline..."):
                participants_list = [p.strip() for p in participants_str.split(",") if p.strip()]
                meeting_dt = datetime.combine(meeting_date, datetime.min.time())

                meeting_svc = MeetingService(db)
                meeting = meeting_svc.create_meeting(
                    title=title,
                    transcript_text=transcript_content,
                    meeting_date=meeting_dt,
                    meeting_type=meeting_type,
                    organizer=organizer,
                    participants=participants_list,
                    project_name=project_name,
                    source_filename=source_filename,
                )

                extraction_svc = ExtractionService(db)
                summary = extraction_svc.process_meeting(meeting.meeting_id, provider_name=provider_choice)

                st.success("Meeting processed successfully!")
                st.balloons()

                st.json(summary)
                st.info(f"Navigate to 'Meeting Details' or 'Action Items' to inspect extracted items.")
        except Exception as e:
            st.error(f"Processing failed: {e}")
        finally:
            db.close()
