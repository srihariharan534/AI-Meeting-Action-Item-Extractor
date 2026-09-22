"""Service for calculating real-time analytics from stored database records."""

from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
from sqlalchemy.orm import Session
from src.database.models import Meeting, ActionItem, Decision


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def get_overview(self) -> Dict[str, Any]:
        """Compute system-wide KPIs from actual database records."""
        total_meetings = self.db.query(Meeting).count()
        total_tasks = self.db.query(ActionItem).count()
        total_decisions = self.db.query(Decision).count()

        completed = self.db.query(ActionItem).filter(ActionItem.status == "completed").count()
        pending = self.db.query(ActionItem).filter(ActionItem.status == "pending").count()
        in_prog = self.db.query(ActionItem).filter(ActionItem.status == "in_progress").count()
        blocked = self.db.query(ActionItem).filter(ActionItem.status == "blocked").count()
        review_req = self.db.query(ActionItem).filter(ActionItem.requires_review == True).count()
        high_pri = self.db.query(ActionItem).filter(ActionItem.priority.in_(["high", "critical"])).count()

        all_tasks = self.db.query(ActionItem).all()
        now = datetime.utcnow()

        overdue = sum(1 for t in all_tasks if t.deadline and t.deadline < now and t.status not in ["completed", "rejected"])
        unassigned = sum(1 for t in all_tasks if not t.owner or t.owner.lower() in ["unassigned", "none", "unknown", "someone"])

        avg_conf = (
            round(sum(t.confidence for t in all_tasks) / len(all_tasks), 2)
            if all_tasks else 0.0
        )

        return {
            "total_meetings": total_meetings,
            "total_action_items": total_tasks,
            "total_decisions": total_decisions,
            "completed_tasks": completed,
            "pending_tasks": pending,
            "in_progress_tasks": in_prog,
            "blocked_tasks": blocked,
            "overdue_tasks": overdue,
            "unassigned_tasks": unassigned,
            "review_required_tasks": review_req,
            "high_priority_tasks": high_pri,
            "average_confidence": avg_conf,
        }

    def get_owner_analytics(self) -> List[Dict[str, Any]]:
        """Group task metrics by responsible owner."""
        all_tasks = self.db.query(ActionItem).all()
        owner_data = defaultdict(lambda: {"total": 0, "completed": 0, "pending": 0, "overdue": 0})
        now = datetime.utcnow()

        for t in all_tasks:
            owner = t.owner if t.owner and t.owner.strip() else "Unassigned"
            owner_data[owner]["total"] += 1
            if t.status == "completed":
                owner_data[owner]["completed"] += 1
            elif t.status in ["pending", "in_progress", "needs_review"]:
                owner_data[owner]["pending"] += 1

            if t.deadline and t.deadline < now and t.status not in ["completed", "rejected"]:
                owner_data[owner]["overdue"] += 1

        results = []
        for owner, stats in sorted(owner_data.items(), key=lambda x: x[1]["total"], reverse=True):
            results.append({
                "owner": owner,
                "total_tasks": stats["total"],
                "completed_tasks": stats["completed"],
                "pending_tasks": stats["pending"],
                "overdue_tasks": stats["overdue"],
            })
        return results

    def get_status_and_priority_distributions(self) -> Dict[str, Any]:
        """Distribution of status, priority, and action types."""
        all_tasks = self.db.query(ActionItem).all()

        status_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        type_counts = defaultdict(int)

        for t in all_tasks:
            status_counts[t.status or "pending"] += 1
            priority_counts[t.priority or "medium"] += 1
            type_counts[t.action_type or "other"] += 1

        return {
            "status_counts": dict(status_counts),
            "priority_counts": dict(priority_counts),
            "action_type_counts": dict(type_counts),
        }

    def get_trends(self) -> List[Dict[str, Any]]:
        """Temporal trends of tasks created vs completed."""
        all_tasks = self.db.query(ActionItem).all()
        day_stats = defaultdict(lambda: {"created": 0, "completed": 0})

        for t in all_tasks:
            if t.created_at:
                c_day = t.created_at.strftime("%Y-%m-%d")
                day_stats[c_day]["created"] += 1
            if t.status == "completed" and t.updated_at:
                u_day = t.updated_at.strftime("%Y-%m-%d")
                day_stats[u_day]["completed"] += 1

        trends = []
        for day in sorted(day_stats.keys()):
            trends.append({
                "date": day,
                "created_count": day_stats[day]["created"],
                "completed_count": day_stats[day]["completed"],
            })
        return trends
