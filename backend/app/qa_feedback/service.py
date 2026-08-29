import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.events import event_bus, DomainEvent, EventTypes
from app.core.websocket_manager import ws_manager
from app.crm.models import Customer, Activity, ActivityType, ActivityPriority, ActivityStatus, CustomerTimelineEvent
from app.qa_feedback.models import (
    FeedbackSurvey, FeedbackResponse, QAScorecard, QAEvaluation, AgentCoachingSession,
    FeedbackMetricType
)
from app.qa_feedback.schemas import (
    FeedbackSubmitRequest, QAScorecardCreate, QAEvaluationCreate, CoachingSessionCreate,
    FeedbackMetricsSummary
)

logger = logging.getLogger(__name__)


class QAFeedbackService:
    # ----------------------------------------------------
    # Customer Feedback & Auto-Escalation Engine
    # ----------------------------------------------------
    @classmethod
    async def submit_feedback(cls, db: AsyncSession, org_id: str, req: FeedbackSubmitRequest) -> FeedbackResponse:
        """
        Record customer feedback (CSAT/NPS).
        Evaluates sentiment, auto-escalates negative ratings with supervisor task,
        and records on Customer 360 Timeline.
        """
        # Determine sentiment and escalation
        sentiment = "POSITIVE"
        is_escalated = False
        escalation_reason = None

        if req.score <= 2:  # CSAT low or NPS detractor
            sentiment = "NEGATIVE"
            is_escalated = True
            escalation_reason = f"Low customer rating ({req.score}/5). Requires immediate supervisor follow-up."
        elif req.score == 3:
            sentiment = "NEUTRAL"

        feedback = FeedbackResponse(
            organization_id=org_id,
            survey_id=req.survey_id,
            customer_id=req.customer_id,
            call_id=req.call_id,
            ticket_id=req.ticket_id,
            agent_user_id=req.agent_user_id,
            score=req.score,
            comment=req.comment,
            sentiment=sentiment,
            agent_rating=req.agent_rating or req.score,
            resolution_rating=req.resolution_rating,
            communication_rating=req.communication_rating,
            is_escalated=is_escalated,
            escalation_reason=escalation_reason
        )
        db.add(feedback)
        await db.flush()

        # If negative rating -> Auto-create Supervisor Follow-up Task
        if is_escalated and req.customer_id:
            task = Activity(
                organization_id=org_id,
                customer_id=req.customer_id,
                activity_type=ActivityType.FOLLOW_UP,
                title=f"URGENT: Customer Dissatisfaction Review ({req.score}/5)",
                description=f"Customer gave rating of {req.score}. Comment: '{req.comment or 'None'}'. Investigate root cause.",
                priority=ActivityPriority.URGENT,
                status=ActivityStatus.PENDING,
                created_by_user_id="feedback-engine"
            )
            db.add(task)

            # Alert Supervisor on WebSocket
            await ws_manager.broadcast_to_supervisors(org_id, {
                "type": "negative_feedback_alert",
                "customer_id": req.customer_id,
                "score": req.score,
                "comment": req.comment
            })

        # Append to Customer Timeline
        if req.customer_id:
            timeline_event = CustomerTimelineEvent(
                organization_id=org_id,
                customer_id=req.customer_id,
                channel="FEEDBACK",
                event_type="FeedbackSubmitted",
                title=f"Feedback Received: {req.score}/5 Stars ({sentiment})",
                description=req.comment or "Customer completed post-interaction survey.",
                metadata_json={"feedback_id": feedback.id, "score": req.score, "sentiment": sentiment},
                actor_name="Customer"
            )
            db.add(timeline_event)

        await db.commit()
        await db.refresh(feedback)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.FEEDBACK_SUBMITTED,
            organization_id=org_id,
            entity_id=feedback.id,
            entity_type="feedback",
            payload={"score": feedback.score, "sentiment": sentiment, "customer_id": req.customer_id},
            user_id="customer"
        ))

        return feedback

    @classmethod
    async def get_feedback_metrics(cls, db: AsyncSession, org_id: str) -> Dict[str, Any]:
        """Compute aggregate CSAT average, NPS score, and feedback distribution"""
        res = await db.execute(
            select(FeedbackResponse).where(and_(FeedbackResponse.organization_id == org_id, FeedbackResponse.is_deleted == False))
        )
        responses = res.scalars().all()

        total = len(responses)
        if total == 0:
            return {
                "average_csat": 0.0,
                "nps_score": 0.0,
                "promoters_count": 0,
                "passives_count": 0,
                "detractors_count": 0,
                "total_responses": 0,
                "negative_escalations_count": 0
            }

        avg_csat = sum(r.score for r in responses) / float(total)
        promoters = len([r for r in responses if r.score >= 4])
        passives = len([r for r in responses if r.score == 3])
        detractors = len([r for r in responses if r.score <= 2])
        escalations = len([r for r in responses if r.is_escalated])

        nps = ((promoters - detractors) / float(total)) * 100.0

        return {
            "average_csat": round(avg_csat, 2),
            "nps_score": round(nps, 1),
            "promoters_count": promoters,
            "passives_count": passives,
            "detractors_count": detractors,
            "total_responses": total,
            "negative_escalations_count": escalations
        }

    # ----------------------------------------------------
    # Quality Assurance (QA) Evaluations & Coaching
    # ----------------------------------------------------
    @classmethod
    async def create_evaluation(cls, db: AsyncSession, org_id: str, req: QAEvaluationCreate, evaluator_id: str) -> QAEvaluation:
        """Score a recorded call using 100-point scorecard criteria and evaluate pass/fail"""
        sc_res = await db.execute(select(QAScorecard).where(and_(QAScorecard.id == req.scorecard_id, QAScorecard.organization_id == org_id)))
        scorecard = sc_res.scalar_one_or_none()
        if not scorecard:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QA Scorecard not found")

        total_score = sum(req.section_scores.values())
        passed = total_score >= scorecard.passing_score
        coaching_req = not passed or req.coaching_required

        evaluation = QAEvaluation(
            organization_id=org_id,
            scorecard_id=req.scorecard_id,
            call_id=req.call_id,
            agent_user_id=req.agent_user_id,
            evaluator_user_id=evaluator_id,
            total_score=total_score,
            passed=passed,
            section_scores=req.section_scores,
            feedback_notes=req.feedback_notes,
            coaching_required=coaching_req
        )
        db.add(evaluation)
        await db.commit()
        await db.refresh(evaluation)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.QA_EVALUATED,
            organization_id=org_id,
            entity_id=evaluation.id,
            entity_type="qa_evaluation",
            payload={"total_score": total_score, "passed": passed, "agent_id": req.agent_user_id},
            user_id=evaluator_id
        ))

        return evaluation
