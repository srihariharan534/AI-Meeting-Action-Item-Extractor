"""UI helper styling, badge formatters, and icons."""

import streamlit as st


def apply_custom_styles():
    """Inject custom modern CSS for clean typography, cards, and badges."""
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.2rem;
        }
        .sub-title {
            font-size: 1.05rem;
            color: #64748B;
            margin-bottom: 1.5rem;
        }
        .metric-card {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        .badge-priority-high {
            background-color: #FEE2E2;
            color: #991B1B;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        .badge-priority-medium {
            background-color: #FEF3C7;
            color: #92400E;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        .badge-priority-low {
            background-color: #E0F2FE;
            color: #075985;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        .badge-review {
            background-color: #FEE2E2;
            color: #DC2626;
            padding: 3px 8px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.8rem;
        }
        .evidence-quote {
            background-color: #F1F5F9;
            border-left: 4px solid #3B82F6;
            padding: 8px 12px;
            font-style: italic;
            font-size: 0.9rem;
            color: #334155;
            margin-top: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_priority_badge(priority: str) -> str:
    p = (priority or "medium").lower()
    if p in ["high", "critical"]:
        return f"<span class='badge-priority-high'>{p.upper()}</span>"
    elif p == "low":
        return f"<span class='badge-priority-low'>{p.upper()}</span>"
    return f"<span class='badge-priority-medium'>{p.upper()}</span>"
