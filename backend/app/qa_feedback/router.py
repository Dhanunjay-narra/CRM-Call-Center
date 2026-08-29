from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from app.core.database import get_db
from app.core.security import PermissionChecker, TokenPayload
from app.qa_feedback.models import FeedbackSurvey, FeedbackResponse, QAScorecard, QAEvaluation, AgentCoachingSession
from app.qa_feedback.schemas import (
    FeedbackSubmitRequest, FeedbackResponseModel, FeedbackMetricsSummary,
    QAScorecardCreate, QAScorecardResponse,
    QAEvaluationCreate, QAEvaluationResponse,
    CoachingSessionCreate, CoachingSessionResponse
)
from app.qa_feedback.service import QAFeedbackService

router = APIRouter()


# ----------------------------------------------------
# Customer Feedback & CSAT / NPS Endpoints
# ----------------------------------------------------

@router.post("/feedback/submit", response_model=FeedbackResponseModel, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    req: FeedbackSubmitRequest,
    auth: TokenPayload = Depends(PermissionChecker([])),
    db: AsyncSession = Depends(get_db)
):
    """Submit post-interaction customer rating (CSAT / NPS) with auto-escalation"""
    return await QAFeedbackService.submit_feedback(db, auth.organization_id, req)


@router.get("/feedback/metrics", response_model=FeedbackMetricsSummary)
async def get_feedback_metrics(
    auth: TokenPayload = Depends(PermissionChecker(["feedback.view"])),
    db: AsyncSession = Depends(get_db)
):
    """Get aggregate CSAT average, NPS score, and satisfaction breakdown"""
    return await QAFeedbackService.get_feedback_metrics(db, auth.organization_id)


# ----------------------------------------------------
# Quality Assurance (QA) Scorecards & Evaluations
# ----------------------------------------------------

@router.get("/qa/scorecards", response_model=List[QAScorecardResponse])
async def list_scorecards(
    auth: TokenPayload = Depends(PermissionChecker(["qa.view_scorecard"])),
    db: AsyncSession = Depends(get_db)
):
    """List QA scorecards"""
    res = await db.execute(
        select(QAScorecard).where(and_(QAScorecard.organization_id == auth.organization_id, QAScorecard.is_deleted == False))
    )
    scorecards = res.scalars().all()
    if not scorecards:
        # Initialize default standard 100-pt scorecard
        sc = QAScorecard(
            organization_id=auth.organization_id,
            name="Standard 100-Point Call Center QA Scorecard",
            description="Comprehensive call evaluation criteria across greeting, empathy, knowledge, resolution, and compliance",
            passing_score=80.0
        )
        db.add(sc)
        await db.commit()
        await db.refresh(sc)
        return [sc]
    return scorecards


@router.post("/qa/scorecards", response_model=QAScorecardResponse, status_code=status.HTTP_201_CREATED)
async def create_scorecard(
    req: QAScorecardCreate,
    auth: TokenPayload = Depends(PermissionChecker(["qa.manage_scorecard"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new customizable QA evaluation scorecard"""
    sc = QAScorecard(
        organization_id=auth.organization_id,
        name=req.name,
        description=req.description,
        passing_score=req.passing_score,
        criteria=req.criteria if req.criteria else undefined
    )
    db.add(sc)
    await db.commit()
    await db.refresh(sc)
    return sc


@router.post("/qa/evaluations", response_model=QAEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_qa_evaluation(
    req: QAEvaluationCreate,
    auth: TokenPayload = Depends(PermissionChecker(["qa.evaluate"])),
    db: AsyncSession = Depends(get_db)
):
    """Score a call recording against a QA scorecard"""
    return await QAFeedbackService.create_evaluation(db, auth.organization_id, req, evaluator_id=auth.sub)


@router.get("/qa/evaluations", response_model=List[QAEvaluationResponse])
async def list_evaluations(
    agent_user_id: Optional[str] = None,
    auth: TokenPayload = Depends(PermissionChecker(["qa.view_scorecard"])),
    db: AsyncSession = Depends(get_db)
):
    """List completed QA evaluations"""
    conditions = [QAEvaluation.organization_id == auth.organization_id, QAEvaluation.is_deleted == False]
    if agent_user_id:
        conditions.append(QAEvaluation.agent_user_id == agent_user_id)

    res = await db.execute(select(QAEvaluation).where(and_(*conditions)).order_by(desc(QAEvaluation.created_at)))
    return res.scalars().all()


# ----------------------------------------------------
# Agent Coaching Sessions
# ----------------------------------------------------

@router.post("/qa/coaching", response_model=CoachingSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_coaching_session(
    req: CoachingSessionCreate,
    auth: TokenPayload = Depends(PermissionChecker(["qa.coach"])),
    db: AsyncSession = Depends(get_db)
):
    """Create an agent coaching plan following a QA evaluation or low CSAT"""
    session = AgentCoachingSession(
        organization_id=auth.organization_id,
        agent_user_id=req.agent_user_id,
        supervisor_user_id=auth.sub,
        evaluation_id=req.evaluation_id,
        focus_area=req.focus_area,
        action_items=req.action_items,
        supervisor_notes=req.supervisor_notes,
        scheduled_date=req.scheduled_date
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session
