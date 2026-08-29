import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.base_models import TenantBaseModel, utc_now


class FeedbackMetricType(str, enum.Enum):
    CSAT = "CSAT"
    NPS = "NPS"
    CES = "CES"


class FeedbackSurvey(TenantBaseModel):
    """Customer Feedback Survey form definition"""
    __tablename__ = "fb_surveys"

    title = Column(String(150), nullable=False)
    metric_type = Column(Enum(FeedbackMetricType), default=FeedbackMetricType.CSAT, nullable=False)
    description = Column(Text, nullable=True)
    questions = Column(JSON, default=list, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    responses = relationship("FeedbackResponse", back_populates="survey", cascade="all, delete-orphan")


class FeedbackResponse(TenantBaseModel):
    """Individual submitted customer feedback"""
    __tablename__ = "fb_responses"

    survey_id = Column(String(36), ForeignKey("fb_surveys.id", ondelete="CASCADE"), nullable=True, index=True)
    customer_id = Column(String(36), ForeignKey("crm_customers.id"), nullable=True, index=True)
    call_id = Column(String(36), nullable=True)
    ticket_id = Column(String(36), nullable=True)
    agent_user_id = Column(String(36), nullable=True, index=True)

    score = Column(Integer, nullable=False)  # 1-5 for CSAT, 0-10 for NPS, 1-7 for CES
    comment = Column(Text, nullable=True)
    sentiment = Column(String(20), default="POSITIVE", nullable=False) # POSITIVE, NEUTRAL, NEGATIVE
    
    agent_rating = Column(Integer, nullable=True)
    resolution_rating = Column(Integer, nullable=True)
    communication_rating = Column(Integer, nullable=True)
    
    is_escalated = Column(Boolean, default=False, nullable=False)
    escalation_reason = Column(String(255), nullable=True)

    survey = relationship("FeedbackSurvey", back_populates="responses")


class QAScorecard(TenantBaseModel):
    """Quality Assurance standard scorecard template"""
    __tablename__ = "qa_scorecards"

    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    passing_score = Column(Float, default=80.0, nullable=False) # e.g. 80 out of 100
    
    # 7 Standard Section Criteria & Weights
    criteria = Column(JSON, default=lambda: [
        {"name": "Greeting & Verification", "max_points": 20, "description": "Clear greeting and accurate caller ID check"},
        {"name": "Communication & Empathy", "max_points": 15, "description": "Active listening, tone, and empathy"},
        {"name": "Product Knowledge", "max_points": 15, "description": "Accurate details and policy explanations"},
        {"name": "Problem Resolution", "max_points": 20, "description": "Effective troubleshooting and first call resolution"},
        {"name": "Compliance & Security", "max_points": 15, "description": "Mandatory disclosures and data privacy"},
        {"name": "Closing & Next Steps", "max_points": 15, "description": "Polite recap, next actions, and survey mention"}
    ], nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)

    evaluations = relationship("QAEvaluation", back_populates="scorecard", cascade="all, delete-orphan")


class QAEvaluation(TenantBaseModel):
    """Evaluated call record scored by QA Analyst or Supervisor"""
    __tablename__ = "qa_evaluations"

    scorecard_id = Column(String(36), ForeignKey("qa_scorecards.id"), nullable=False, index=True)
    call_id = Column(String(36), ForeignKey("cc_calls.id"), nullable=False, index=True)
    agent_user_id = Column(String(36), nullable=False, index=True)
    evaluator_user_id = Column(String(36), nullable=False)
    
    total_score = Column(Float, nullable=False)  # 0.0 to 100.0
    passed = Column(Boolean, nullable=False)
    
    section_scores = Column(JSON, default=dict, nullable=False) # {"Greeting": 18, "Communication": 14, ...}
    feedback_notes = Column(Text, nullable=True)
    coaching_required = Column(Boolean, default=False, nullable=False)

    scorecard = relationship("QAScorecard", back_populates="evaluations")


class AgentCoachingSession(TenantBaseModel):
    """Coaching action plan assigned to agent based on QA results"""
    __tablename__ = "qa_coaching_sessions"

    agent_user_id = Column(String(36), nullable=False, index=True)
    supervisor_user_id = Column(String(36), nullable=False)
    evaluation_id = Column(String(36), ForeignKey("qa_evaluations.id"), nullable=True)
    
    focus_area = Column(String(150), nullable=False) # e.g. "Problem Resolution & FCR"
    action_items = Column(JSON, default=list, nullable=False)
    supervisor_notes = Column(Text, nullable=True)
    agent_comments = Column(Text, nullable=True)
    
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
