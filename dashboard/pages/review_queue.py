"""Human-in-the-Loop review queue for ambiguous and flagged tasks."""

import streamlit as st
from datetime import datetime
from src.database.session import SessionLocal
from src.services.action_item_service import ActionItemService


def render():
    st.markdown("<h1 class='main-title'>Human Review Queue</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-title'>Resolve low-confidence, unassigned, or ambiguous action items flagged by the validation engine.</p>",
        unsafe_allow_html=True,
    )

    db = SessionLocal()
    try:
        action_svc = ActionItemService(db)
        review_items = action_svc.list_action_items(requires_review=True, limit=100)

        if not review_items:
            st.success("🎉 All caught up! No action items currently require human review.")
            return

        st.warning(f"⚠️ {len(review_items)} item(s) require human review and approval.")

        for item in review_items:
            with st.container():
                st.markdown(f"### Task: **{item.task}**")
                st.markdown(
                    f"**Current Owner:** `{item.owner or 'Unassigned'}` | "
                    f"**Deadline:** `{item.deadline.strftime('%Y-%m-%d') if item.deadline else 'None'}` | "
                    f"**Confidence:** `{item.confidence * 100:.0f}%`"
                )

                if item.validation_flags:
                    st.error(f"Validation Flags: {', '.join(item.validation_flags)}")

                st.markdown(
                    f"<div class='evidence-quote'><b>Grounding Evidence:</b> \"{item.evidence}\"</div>",
                    unsafe_allow_html=True,
                )

                # Review actions form
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    corrected_owner = st.text_input(
                        "Assign / Correct Owner",
                        value=item.owner or "",
                        key=f"owner_{item.task_id}",
                    )
                with col2:
                    corrected_priority = st.selectbox(
                        "Priority",
                        ["low", "medium", "high", "critical"],
                        index=["low", "medium", "high", "critical"].index(item.priority.lower() if item.priority.lower() in ["low", "medium", "high", "critical"] else "medium"),
                        key=f"pri_{item.task_id}",
                    )
                with col3:
                    review_note = st.text_input(
                        "Review Note",
                        value="",
                        placeholder="e.g., Assigned to Meena",
                        key=f"note_{item.task_id}",
                    )

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅ Approve & Save Corrections", key=f"app_{item.task_id}", use_container_width=True):
                        updates = {
                            "owner": corrected_owner.strip() if corrected_owner.strip() else None,
                            "priority": corrected_priority,
                        }
                        action_svc.execute_review_action(
                            task_id=item.task_id,
                            action="edit",
                            reviewer_note=review_note or "Approved with human review edits",
                            updated_fields=updates,
                        )
                        st.success("Task updated and marked approved!")
                        st.rerun()

                with col_btn2:
                    if st.button("❌ Reject Action Item", key=f"rej_{item.task_id}", use_container_width=True):
                        action_svc.execute_review_action(
                            task_id=item.task_id,
                            action="reject",
                            reviewer_note=review_note or "Rejected by human reviewer",
                        )
                        st.warning("Action item rejected.")
                        st.rerun()

                st.divider()

    finally:
        db.close()
