from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from app.qa_feedback.models import FeedbackMetricType


# Feedback Schemas
class FeedbackSubmitRequest(BaseModel):
    survey_id: Optional[str] = None
    customer_id: Optional[str] = None
    call_id: Optional[str] = None
    ticket_id: Optional[str] = None
    agent_user_id: Optional[str] = None
    score: int
    comment: Optional[str] = None
    agent_rating: Optional[int] = None
    resolution_rating: Optional[int] = None
    communication_rating: Optional[int] = None


class FeedbackResponseModel(BaseModel):
    id: str
    organization_id: str
    survey_id: Optional[str] = None
    customer_id: Optional[str] = None
    call_id: Optional[str] = None
    ticket_id: Optional[str] = None
    agent_user_id: Optional[str] = None
    score: int
    comment: Optional[str] = None
    sentiment: str
    agent_rating: Optional[int] = None
    resolution_rating: Optional[int] = None
    communication_rating: Optional[int] = None
    is_escalated: bool
    escalation_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackMetricsSummary(BaseModel):
    average_csat: float
    nps_score: float
    promoters_count: int
    passives_count: int
    detractors_count: int
    total_responses: int
    negative_escalations_count: int


# QA Scorecard Schemas
class QAScorecardCreate(BaseModel):
    name: str
    description: Optional[str] = None
    passing_score: float = 80.0
    criteria: Optional[List[Dict[str, Any]]] = None


class QAScorecardResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    passing_score: float
    criteria: List[Dict[str, Any]]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QAEvaluationCreate(BaseModel):
    scorecard_id: str
    call_id: str
    agent_user_id: str
    section_scores: Dict[str, float]
    feedback_notes: Optional[str] = None
    coaching_required: bool = False


class QAEvaluationResponse(BaseModel):
    id: str
    organization_id: str
    scorecard_id: str
    call_id: str
    agent_user_id: str
    evaluator_user_id: str
    total_score: float
    passed: bool
    section_scores: Dict[str, float]
    feedback_notes: Optional[str] = None
    coaching_required: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Coaching Schemas
class CoachingSessionCreate(BaseModel):
    agent_user_id: str
    evaluation_id: Optional[str] = None
    focus_area: str
    action_items: List[str] = []
    supervisor_notes: Optional[str] = None
    scheduled_date: Optional[datetime] = None


class CoachingSessionResponse(BaseModel):
    id: str
    organization_id: str
    agent_user_id: str
    supervisor_user_id: str
    evaluation_id: Optional[str] = None
    focus_area: str
    action_items: List[str]
    supervisor_notes: Optional[str] = None
    agent_comments: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
