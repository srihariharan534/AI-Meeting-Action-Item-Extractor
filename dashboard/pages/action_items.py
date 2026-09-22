"""Global action-item directory with status tracking and CSV export."""

import streamlit as st
import pandas as pd
from src.database.session import SessionLocal
from src.services.action_item_service import ActionItemService
from src.services.export_service import ExportService


def render():
    st.markdown("<h1 class='main-title'>Action Items Master Table</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-title'>Filter, search, update status, and track execution across all meetings.</p>",
        unsafe_allow_html=True,
    )

    db = SessionLocal()
    try:
        action_svc = ActionItemService(db)
        export_svc = ExportService(db)

        # Filters
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "pending", "in_progress", "completed", "needs_review", "blocked", "rejected"],
            )
        with col_f2:
            search_query = st.text_input("Search Tasks / Owners / Evidence", "")
        with col_f3:
            export_csv = export_svc.export_action_items_csv()
            st.download_button(
                "📥 Export All Tasks (CSV)",
                export_csv,
                "all_action_items.csv",
                "text/csv",
                use_container_width=True,
            )

        status_val = None if status_filter == "All" else status_filter
        items = action_svc.list_action_items(
            status=status_val,
            search=search_query if search_query.strip() else None,
            limit=300,
        )

        if not items:
            st.info("No matching action items found.")
            return

        table_data = []
        for i in items:
            table_data.append({
                "Task ID": i.task_id[:8] + "...",
                "Task": i.task,
                "Owner": i.owner or "Unassigned",
                "Deadline": i.deadline.strftime("%Y-%m-%d") if i.deadline else "None",
                "Priority": i.priority,
                "Status": i.status,
                "Review Status": i.review_status,
                "Confidence": f"{i.confidence * 100:.0f}%",
                "Evidence": i.evidence[:60] + ("..." if len(i.evidence) > 60 else ""),
            })

        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

        st.divider()

        # Task Quick Action Form
        st.subheader("⚡ Quick Task Status Update")
        col_u1, col_u2, col_u3 = st.columns([2, 1, 1])
        with col_u1:
            task_options = {f"{t.task} ({t.owner or 'Unassigned'})": t.task_id for t in items}
            sel_label = st.selectbox("Select Task to Update", list(task_options.keys()))
            sel_id = task_options[sel_label]

        with col_u2:
            new_status = st.selectbox("New Status", ["pending", "in_progress", "completed", "blocked", "rejected"])

        with col_u3:
            st.write("")
            st.write("")
            if st.button("Update Status"):
                action_svc.update_action_item(sel_id, {"status": new_status})
                st.success(f"Status updated to '{new_status}'!")
                st.rerun()

    finally:
        db.close()
