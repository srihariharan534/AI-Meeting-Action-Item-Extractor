import sys
from pathlib import Path

# Ensure root directory is in sys.path so that `src` and `dashboard` can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from src.database.session import init_db
from dashboard.components import apply_custom_styles
from dashboard.pages import (
    overview,
    upload_meeting,
    meetings,
    meeting_details,
    action_items,
    review_queue,
    analytics,
    evaluation_results,
)

# Page configuration
st.set_page_config(
    page_title="AI Meeting Action-Item Extractor",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure DB is created
init_db()

# Apply CSS
apply_custom_styles()

# Sidebar Navigation
st.sidebar.title("📋 AI Meeting Action-Item Extractor")
st.sidebar.caption("Production-Style NLP & Information Extraction")

pages = {
    "📊 Overview": overview.render,
    "📤 Upload Meeting": upload_meeting.render,
    "📁 Meetings": meetings.render,
    "🔍 Meeting Details": meeting_details.render,
    "✅ Action Items": action_items.render,
    "⚠️ Review Queue": review_queue.render,
    "📈 Analytics": analytics.render,
    "🎯 Evaluation Results": evaluation_results.render,
}

selection = st.sidebar.radio("Navigation", list(pages.keys()))

st.sidebar.divider()
st.sidebar.markdown(
    """
    **System Status:**
    - **Engine**: SQLAlchemy 2.0 / SQLite
    - **Extraction Mode**: Grounded Evidence
    - **Validation**: Deterministic Rules Active
    """
)

# Render selected page
pages[selection]()
