import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.core.events import event_bus, DomainEvent, EventTypes
from app.core.websocket_manager import ws_manager
from app.crm.models import Activity, ActivityType, ActivityPriority, ActivityStatus
from app.communications.providers import email_provider, sms_provider, whatsapp_provider
from app.automation.models import (
    Workflow, WorkflowExecution,
    WorkflowTriggerType, WorkflowActionType, ExecutionStatus
)
from app.automation.schemas import WorkflowCreate, WorkflowUpdate

logger = logging.getLogger(__name__)


def evaluate_condition(condition: Dict[str, Any], payload: Dict[str, Any]) -> bool:
    """Evaluate single condition rule against domain event payload"""
    field = condition.get("field")
    operator = condition.get("operator", "equals")
    target_val = condition.get("value")

    actual_val = payload.get(field)
    if actual_val is None:
        return False

    try:
        if operator == "equals":
            return actual_val == target_val
        elif operator == "greater_than":
            return float(actual_val) > float(target_val)
        elif operator == "less_than":
            return float(actual_val) < float(target_val)
        elif operator == "contains":
            return str(target_val).lower() in str(actual_val).lower()
        elif operator == "in":
            return actual_val in target_val
    except Exception as e:
        logger.warning(f"Error evaluating workflow condition {condition}: {e}")
        return False

    return False


class AutomationService:
    @classmethod
    async def evaluate_and_execute_workflows(cls, db: AsyncSession, event: DomainEvent) -> List[WorkflowExecution]:
        """
        Main Event-Driven Automation Engine.
        Matches event type to active workflows, evaluates conditions, and fires actions.
        """
        trigger_name = event.event_type
        # Find active workflows matching trigger
        query = await db.execute(
            select(Workflow).where(
                and_(
                    Workflow.organization_id == event.organization_id,
                    Workflow.is_active == True,
                    Workflow.is_deleted == False
                )
            )
        )
        all_workflows = query.scalars().all()
        matching_workflows = [w for w in all_workflows if w.trigger_type.value == trigger_name]

        execution_results = []
        now = datetime.now(timezone.utc)

        for wf in matching_workflows:
            exec_log = []
            exec_log.append(f"Evaluating workflow '{wf.name}' for event {trigger_name} on entity {event.entity_id}")

            # Evaluate conditions
            conditions_met = True
            for cond in (wf.conditions or []):
                cond_result = evaluate_condition(cond, event.payload)
                exec_log.append(f"Condition: {cond.get('field')} {cond.get('operator')} {cond.get('value')} => {cond_result}")
                if not cond_result:
                    conditions_met = False
                    break

            if not conditions_met:
                exec_log.append("Conditions not satisfied. Skipping execution.")
                execution = WorkflowExecution(
                    organization_id=event.organization_id,
                    workflow_id=wf.id,
                    trigger_event_type=trigger_name,
                    entity_id=event.entity_id,
                    entity_type=event.entity_type,
                    status=ExecutionStatus.SKIPPED,
                    logs=exec_log,
                    started_at=now,
                    completed_at=now
                )
                db.add(execution)
                execution_results.append(execution)
                continue

            # Execute Actions
            exec_log.append("Conditions met. Executing actions...")
            action_status = ExecutionStatus.SUCCESS
            error_msg = None

            for act in (wf.actions or []):
                act_type = act.get("action_type")
                params = act.get("params", {})

                try:
                    if act_type == WorkflowActionType.CREATE_TASK.value or act_type == "CREATE_TASK":
                        task = Activity(
                            organization_id=event.organization_id,
                            customer_id=event.payload.get("customer_id") if event.entity_type != "customer" else event.entity_id,
                            lead_id=event.entity_id if event.entity_type == "lead" else None,
                            activity_type=ActivityType.TASK,
                            title=params.get("title", f"Automated Task: {wf.name}"),
                            description=params.get("description", "Generated automatically by workflow engine"),
                            priority=ActivityPriority.HIGH,
                            status=ActivityStatus.PENDING,
                            created_by_user_id="workflow-engine"
                        )
                        db.add(task)
                        exec_log.append(f"Action CREATE_TASK executed: '{task.title}'")

                    elif act_type == WorkflowActionType.SEND_EMAIL.value or act_type == "SEND_EMAIL":
                        to_email = params.get("to") or event.payload.get("email")
                        if to_email:
                            await email_provider.send_message(to_email, params.get("body", "Notification"), subject=params.get("subject", "Alert"))
                            exec_log.append(f"Action SEND_EMAIL executed to {to_email}")

                    elif act_type == WorkflowActionType.NOTIFY_SUPERVISOR.value or act_type == "NOTIFY_SUPERVISOR":
                        await ws_manager.broadcast_to_supervisors(event.organization_id, {
                            "type": "workflow_supervisor_alert",
                            "workflow_name": wf.name,
                            "event": trigger_name,
                            "message": params.get("message", "High priority automated workflow triggered")
                        })
                        exec_log.append("Action NOTIFY_SUPERVISOR executed")

                except Exception as e:
                    action_status = ExecutionStatus.FAILED
                    error_msg = str(e)
                    exec_log.append(f"Action error: {e}")

            wf.execution_count += 1
            wf.last_executed_at = now

            execution = WorkflowExecution(
                organization_id=event.organization_id,
                workflow_id=wf.id,
                trigger_event_type=trigger_name,
                entity_id=event.entity_id,
                entity_type=event.entity_type,
                status=action_status,
                logs=exec_log,
                error_message=error_msg,
                started_at=now,
                completed_at=now
            )
            db.add(execution)
            execution_results.append(execution)

        await db.commit()
        return execution_results
