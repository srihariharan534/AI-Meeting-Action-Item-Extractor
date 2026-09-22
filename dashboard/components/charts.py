"""Plotly visualization charts for meeting and task analytics."""

import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any


def plot_status_distribution(status_counts: Dict[str, int]):
    """Donut chart of action items by status."""
    if not status_counts:
        return None
    labels = list(status_counts.keys())
    values = list(status_counts.values())

    colors = {
        "completed": "#10B981",
        "in_progress": "#3B82F6",
        "pending": "#F59E0B",
        "needs_review": "#EF4444",
        "blocked": "#6B7280",
        "rejected": "#9CA3AF",
    }
    marker_colors = [colors.get(k.lower(), "#64748B") for k in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                marker=dict(colors=marker_colors),
                textinfo="label+value",
            )
        ]
    )
    fig.update_layout(
        title="Action Items by Status",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig


def plot_owner_workload(owner_data: List[Dict[str, Any]]):
    """Horizontal bar chart of tasks per owner."""
    if not owner_data:
        return None

    owners = [d["owner"] for d in owner_data][:10]
    totals = [d["total_tasks"] for d in owner_data][:10]
    completed = [d["completed_tasks"] for d in owner_data][:10]

    fig = go.Figure()
    fig.add_trace(go.Bar(y=owners, x=totals, name="Total Tasks", orientation="h", marker_color="#3B82F6"))
    fig.add_trace(go.Bar(y=owners, x=completed, name="Completed", orientation="h", marker_color="#10B981"))

    fig.update_layout(
        barmode="group",
        title="Owner Task Distribution",
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
    )
    return fig


def plot_priority_distribution(priority_counts: Dict[str, int]):
    """Bar chart for priority breakdown."""
    if not priority_counts:
        return None

    order = ["critical", "high", "medium", "low", "unknown"]
    labels = [k for k in order if k in priority_counts]
    values = [priority_counts[k] for k in labels]

    colors = ["#DC2626", "#F97316", "#FBBF24", "#38BDF8", "#94A3B8"]

    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=colors[:len(labels)])])
    fig.update_layout(
        title="Action Items by Priority",
        xaxis_title="Priority",
        yaxis_title="Count",
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    return fig
