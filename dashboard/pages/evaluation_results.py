"""Model evaluation metrics and benchmark inspection dashboard page."""

import streamlit as st
import pandas as pd
from src.database.session import SessionLocal
from src.database.models import EvaluationResults


def render():
    st.markdown("<h1 class='main-title'>Model Evaluation Benchmark Results</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-title'>Empirical quantitative evaluation of extraction precision, recall, and grounding.</p>",
        unsafe_allow_html=True,
    )

    db = SessionLocal()
    try:
        results = db.query(EvaluationResults).order_by(EvaluationResults.created_at.desc()).all()

        if not results:
            st.info("No evaluation runs recorded in the database yet. Run `python scripts/evaluate_models.py` or `python scripts/run_pipeline.py` to populate real evaluation benchmarks.")
            return

        rows = []
        for r in results:
            rows.append({
                "Model / Provider": r.model_name,
                "Dataset": r.dataset_name,
                "Precision": f"{r.precision:.2f}",
                "Recall": f"{r.recall:.2f}",
                "F1 Score": f"{r.f1_score:.2f}",
                "Owner Acc": f"{r.owner_accuracy:.2f}",
                "Deadline Acc": f"{r.deadline_accuracy:.2f}",
                "Grounding Score": f"{r.evidence_grounding_score:.2f}",
                "Latency (s)": f"{r.processing_time:.2f}",
                "Timestamp": r.created_at.strftime("%Y-%m-%d %H:%M"),
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

        st.subheader("Benchmark Metrics Guide")
        st.markdown(
            """
            - **Precision**: Proportion of extracted action items that were genuine tasks.
            - **Recall**: Proportion of true reference action items captured.
            - **F1 Score**: Harmonic mean of Precision and Recall.
            - **Owner Accuracy**: Accuracy of attributing tasks to correct individual/team or Unassigned.
            - **Deadline Accuracy**: Accuracy of extracting and normalizing relative/absolute dates.
            - **Grounding Score**: Proportion of tasks backed by exact segment quotations.
            """
        )

    finally:
        db.close()
