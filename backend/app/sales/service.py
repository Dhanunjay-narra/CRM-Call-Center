from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.events import event_bus, DomainEvent, EventTypes
from app.crm.models import Customer, CustomerTimelineEvent
from app.sales.models import (
    Pipeline, PipelineStage, Opportunity, Campaign, CampaignAudienceMember,
    OpportunityStatus, CampaignStatus
)
from app.sales.schemas import (
    PipelineCreate, OpportunityCreate, OpportunityUpdate,
    CampaignCreate, CampaignUpdate, SalesForecastResponse
)


class SalesService:
    @staticmethod
    async def create_default_pipeline(db: AsyncSession, org_id: str) -> Pipeline:
        """Create standard sales pipeline with default stages for a tenant"""
        pipeline = Pipeline(
            organization_id=org_id,
            name="Standard Sales Pipeline",
            description="Default B2B sales pipeline",
            is_default=True
        )
        db.add(pipeline)
        await db.flush()

        stages_data = [
            {"name": "Discovery", "order": 1, "default_probability": 10, "is_won": False, "is_lost": False},
            {"name": "Qualification", "order": 2, "default_probability": 25, "is_won": False, "is_lost": False},
            {"name": "Proposal / Quote", "order": 3, "default_probability": 50, "is_won": False, "is_lost": False},
            {"name": "Negotiation", "order": 4, "default_probability": 80, "is_won": False, "is_lost": False},
            {"name": "Closed Won", "order": 5, "default_probability": 100, "is_won": True, "is_lost": False},
            {"name": "Closed Lost", "order": 6, "default_probability": 0, "is_won": False, "is_lost": True},
        ]

        for s in stages_data:
            stage = PipelineStage(
                organization_id=org_id,
                pipeline_id=pipeline.id,
                name=s["name"],
                order=s["order"],
                default_probability=s["default_probability"],
                is_won_stage=s["is_won"],
                is_lost_stage=s["is_lost"]
            )
            db.add(stage)

        await db.commit()
        
        # Reload with stages loaded
        reloaded = await db.execute(
            select(Pipeline).options(selectinload(Pipeline.stages)).where(Pipeline.id == pipeline.id)
        )
        return reloaded.scalar_one()

    @classmethod
    async def create_opportunity(cls, db: AsyncSession, org_id: str, req: OpportunityCreate, user_id: str) -> Opportunity:
        """Create new sales deal and record in Customer 360 timeline"""
        probability = req.probability
        if probability is None:
            stage_query = await db.execute(select(PipelineStage).where(PipelineStage.id == req.stage_id))
            stage = stage_query.scalar_one_or_none()
            probability = stage.default_probability if stage else 20

        opp = Opportunity(
            organization_id=org_id,
            pipeline_id=req.pipeline_id,
            stage_id=req.stage_id,
            customer_id=req.customer_id,
            contact_id=req.contact_id,
            lead_id=req.lead_id,
            title=req.title,
            amount=req.amount,
            currency=req.currency,
            probability=probability,
            status=OpportunityStatus.OPEN,
            expected_close_date=req.expected_close_date,
            owner_user_id=req.owner_user_id or user_id,
            products=req.products or [],
            competitors=req.competitors or [],
            next_step=req.next_step,
            custom_fields=req.custom_fields or {}
        )
        db.add(opp)
        await db.flush()

        # Update customer open opportunities count
        if req.customer_id:
            cust_query = await db.execute(select(Customer).where(Customer.id == req.customer_id))
            cust = cust_query.scalar_one_or_none()
            if cust:
                cust.open_opportunities_count += 1
                cust.last_interaction_at = datetime.now(timezone.utc)

            timeline = CustomerTimelineEvent(
                organization_id=org_id,
                customer_id=req.customer_id,
                contact_id=req.contact_id,
                channel="SALES",
                event_type="OpportunityCreated",
                title=f"Deal Created: {opp.title} (${opp.amount:,.2f})",
                description=f"Sales opportunity opened with {probability}% win probability.",
                metadata_json={"opportunity_id": opp.id, "amount": opp.amount},
                actor_user_id=user_id,
                actor_name="Sales Executive"
            )
            db.add(timeline)

        await db.commit()
        await db.refresh(opp)

        await event_bus.publish(DomainEvent(
            event_type=EventTypes.OPPORTUNITY_CREATED,
            organization_id=org_id,
            entity_id=opp.id,
            entity_type="opportunity",
            payload={"title": opp.title, "amount": opp.amount},
            user_id=user_id
        ))

        return opp

    @classmethod
    async def update_opportunity(cls, db: AsyncSession, org_id: str, opp_id: str, req: OpportunityUpdate, user_id: str) -> Opportunity:
        """Update opportunity details, stage movement, and win/loss status"""
        res = await db.execute(select(Opportunity).where(and_(Opportunity.id == opp_id, Opportunity.organization_id == org_id)))
        opp = res.scalar_one_or_none()
        if not opp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

        old_stage_id = opp.stage_id
        update_dict = req.model_dump(exclude_unset=True)

        for k, v in update_dict.items():
            setattr(opp, k, v)

        if req.stage_id and req.stage_id != old_stage_id:
            stage_query = await db.execute(select(PipelineStage).where(PipelineStage.id == req.stage_id))
            stage = stage_query.scalar_one_or_none()
            if stage:
                opp.probability = stage.default_probability
                if stage.is_won_stage:
                    opp.status = OpportunityStatus.WON
                    opp.actual_close_date = datetime.now(timezone.utc)
                    await event_bus.publish(DomainEvent(
                        event_type=EventTypes.OPPORTUNITY_WON,
                        organization_id=org_id,
                        entity_id=opp.id,
                        entity_type="opportunity",
                        payload={"amount": opp.amount},
                        user_id=user_id
                    ))
                elif stage.is_lost_stage:
                    opp.status = OpportunityStatus.LOST
                    opp.actual_close_date = datetime.now(timezone.utc)
                    await event_bus.publish(DomainEvent(
                        event_type=EventTypes.OPPORTUNITY_LOST,
                        organization_id=org_id,
                        entity_id=opp.id,
                        entity_type="opportunity",
                        payload={"amount": opp.amount},
                        user_id=user_id
                    ))
                else:
                    await event_bus.publish(DomainEvent(
                        event_type=EventTypes.OPPORTUNITY_STAGE_CHANGED,
                        organization_id=org_id,
                        entity_id=opp.id,
                        entity_type="opportunity",
                        payload={"old_stage_id": old_stage_id, "new_stage_id": stage.id, "stage_name": stage.name},
                        user_id=user_id
                    ))

        await db.commit()
        await db.refresh(opp)
        return opp

    @classmethod
    async def calculate_sales_forecast(cls, db: AsyncSession, org_id: str) -> Dict[str, Any]:
        """Compute sales revenue forecast, weighted pipeline value, and win rate analysis"""
        opps_res = await db.execute(
            select(Opportunity).where(and_(Opportunity.organization_id == org_id, Opportunity.is_deleted == False))
        )
        opps = opps_res.scalars().all()

        total_value = 0.0
        weighted_value = 0.0
        open_count = 0
        won_count = 0
        won_revenue = 0.0
        lost_count = 0

        for o in opps:
            if o.status == OpportunityStatus.OPEN:
                open_count += 1
                total_value += o.amount
                weighted_value += (o.amount * (o.probability / 100.0))
            elif o.status == OpportunityStatus.WON:
                won_count += 1
                won_revenue += o.amount
            elif o.status == OpportunityStatus.LOST:
                lost_count += 1

        total_closed = won_count + lost_count
        win_rate = (won_count / total_closed * 100.0) if total_closed > 0 else 0.0

        stages_res = await db.execute(
            select(PipelineStage).where(PipelineStage.organization_id == org_id).order_by(PipelineStage.order)
        )
        stages = stages_res.scalars().all()
        stage_breakdown = []
        for stg in stages:
            stg_opps = [o for o in opps if o.stage_id == stg.id]
            stg_amount = sum(o.amount for o in stg_opps)
            stage_breakdown.append({
                "stage_id": stg.id,
                "stage_name": stg.name,
                "deal_count": len(stg_opps),
                "total_amount": stg_amount,
                "weighted_amount": stg_amount * (stg.default_probability / 100.0)
            })

        return {
            "total_pipeline_value": total_value,
            "weighted_forecast_value": weighted_value,
            "open_deals_count": open_count,
            "won_deals_count": won_count,
            "won_revenue": won_revenue,
            "lost_deals_count": lost_count,
            "win_rate_percent": round(win_rate, 2),
            "stage_breakdown": stage_breakdown
        }

    @classmethod
    async def execute_campaign(cls, db: AsyncSession, org_id: str, campaign_id: str, user_id: str) -> Campaign:
        """Simulate campaign execution: blast messages to audience and track delivery rates"""
        res = await db.execute(select(Campaign).where(and_(Campaign.id == campaign_id, Campaign.organization_id == org_id)))
        campaign = res.scalar_one_or_none()
        if not campaign:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")

        campaign.status = CampaignStatus.RUNNING
        campaign.executed_at = datetime.now(timezone.utc)

        cust_res = await db.execute(select(Customer).where(and_(Customer.organization_id == org_id, Customer.is_deleted == False)))
        customers = cust_res.scalars().all()

        recipient_count = max(len(customers), 5)
        campaign.total_audience = recipient_count
        campaign.total_sent = recipient_count
        campaign.total_delivered = int(recipient_count * 0.96)
        campaign.total_opened = int(recipient_count * 0.45)
        campaign.total_clicked = int(recipient_count * 0.18)
        campaign.total_converted = max(1, int(recipient_count * 0.08))
        campaign.revenue_generated = campaign.total_converted * 1250.0
        campaign.status = CampaignStatus.COMPLETED

        await db.commit()
        await db.refresh(campaign)
        return campaign
