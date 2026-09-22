"""SQLAlchemy ORM models for AI Meeting Action-Item Extractor."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Float,
    Boolean,
    Integer,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    """Generate a random UUID string."""
    return str(uuid.uuid4())


class Meeting(Base):
    """Represents an ingested meeting and its metadata."""

    __tablename__ = "meetings"

    meeting_id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    meeting_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    meeting_type = Column(String(100), default="General meeting")
    organizer = Column(String(255), nullable=True)
    participants = Column(JSON, default=list)  # List of participant strings
    project_name = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    source_filename = Column(String(255), nullable=True)
    transcript_text = Column(Text, nullable=False)
    processing_status = Column(String(50), default="pending")  # pending | processing | completed | failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    segments = relationship("TranscriptSegment", back_populates="meeting", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="meeting", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="meeting", cascade="all, delete-orphan")


class TranscriptSegment(Base):
    """Represents a discrete speaker turn or sentence in a transcript."""

    __tablename__ = "transcript_segments"

    segment_id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.meeting_id"), nullable=False)
    speaker = Column(String(255), default="Unknown")
    timestamp_start = Column(String(50), nullable=True)
    timestamp_end = Column(String(50), nullable=True)
    original_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=False)
    sequence_number = Column(Integer, nullable=False)

    meeting = relationship("Meeting", back_populates="segments")


class ActionItem(Base):
    """Represents a structured, grounded action item."""

    __tablename__ = "action_items"

    task_id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.meeting_id"), nullable=False)
    task = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    owner = Column(String(255), nullable=True)  # Null if unassigned
    owner_confidence = Column(Float, default=1.0)
    deadline = Column(DateTime, nullable=True)  # Normalized ISO date
    deadline_text_original = Column(String(255), nullable=True)
    deadline_type = Column(String(50), default="missing")  # exact_date | relative_date | inferred_date | ambiguous | missing
    priority = Column(String(50), default="medium")  # low | medium | high | critical | unknown
    status = Column(String(50), default="pending")  # pending | in_progress | completed | blocked | rejected | needs_review
    action_type = Column(String(50), default="other")  # create | review | fix | send | prepare | analyze | approve | schedule | contact | research | update | test | deploy | follow_up | other
    confidence = Column(Float, default=1.0)
    evidence = Column(Text, nullable=False)
    evidence_segment_ids = Column(JSON, default=list)  # List of segment_id strings
    ambiguities = Column(JSON, default=list)  # List of strings
    validation_flags = Column(JSON, default=list)  # List of strings
    requires_review = Column(Boolean, default=False)
    review_status = Column(String(50), default="pending")  # pending | approved | edited | rejected
    review_comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="action_items")
    review_histories = relationship("ReviewHistory", back_populates="action_item", cascade="all, delete-orphan")


class Decision(Base):
    """Represents a key decision extracted from a meeting."""

    __tablename__ = "decisions"

    decision_id = Column(String(36), primary_key=True, default=generate_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.meeting_id"), nullable=False)
    decision = Column(Text, nullable=False)
    decision_date = Column(DateTime, nullable=True)
    decision_owner = Column(String(255), nullable=True)
    evidence = Column(Text, nullable=False)
    evidence_segment_ids = Column(JSON, default=list)
    confidence = Column(Float, default=1.0)
    requires_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    meeting = relationship("Meeting", back_populates="decisions")


class TaskRelationship(Base):
    """Represents dependencies and relationships between tasks."""

    __tablename__ = "task_relationships"

    relationship_id = Column(String(36), primary_key=True, default=generate_uuid)
    source_task_id = Column(String(36), ForeignKey("action_items.task_id"), nullable=False)
    target_task_id = Column(String(36), ForeignKey("action_items.task_id"), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # depends_on | blocks | related_to | blocked_by | duplicate_of
    confidence = Column(Float, default=1.0)
    evidence = Column(Text, nullable=True)
    requires_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ReviewHistory(Base):
    """Maintains an audit trail of human review actions."""

    __tablename__ = "review_history"

    review_id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("action_items.task_id"), nullable=False)
    previous_values = Column(JSON, nullable=False)
    updated_values = Column(JSON, nullable=False)
    action = Column(String(50), nullable=False)  # approve | edit | reject | complete
    reviewer_note = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    action_item = relationship("ActionItem", back_populates="review_histories")


class EvaluationResults(Base):
    """Stores quantitative model evaluation metrics."""

    __tablename__ = "evaluation_results"

    evaluation_id = Column(String(36), primary_key=True, default=generate_uuid)
    model_name = Column(String(100), nullable=False)
    dataset_name = Column(String(100), nullable=False)
    precision = Column(Float, nullable=False)
    recall = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    owner_accuracy = Column(Float, nullable=False)
    deadline_accuracy = Column(Float, nullable=False)
    evidence_grounding_score = Column(Float, nullable=False)
    duplicate_f1 = Column(Float, default=0.0)
    processing_time = Column(Float, nullable=False)
    metrics_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
