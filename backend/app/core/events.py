import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, Dict, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class DomainEvent(BaseModel):
    """Base model for all domain events across CallSphere CRM"""
    event_type: str
    organization_id: str
    entity_id: str
    entity_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str = "system"


# Core Event Names
class EventTypes:
    # Leads
    LEAD_CREATED = "LeadCreated"
    LEAD_UPDATED = "LeadUpdated"
    LEAD_ASSIGNED = "LeadAssigned"
    LEAD_CONVERTED = "LeadConverted"

    # Contacts & Customers
    CONTACT_CREATED = "ContactCreated"
    CUSTOMER_CREATED = "CustomerCreated"
    CUSTOMER_UPDATED = "CustomerUpdated"

    # Sales & Opportunities
    OPPORTUNITY_CREATED = "OpportunityCreated"
    OPPORTUNITY_STAGE_CHANGED = "OpportunityStageChanged"
    OPPORTUNITY_WON = "OpportunityWon"
    OPPORTUNITY_LOST = "OpportunityLost"

    # Calls & Telephony
    CALL_INITIATED = "CallInitiated"
    CALL_RINGING = "CallRinging"
    CALL_ANSWERED = "CallAnswered"
    CALL_TRANSFERRED = "CallTransferred"
    CALL_COMPLETED = "CallCompleted"
    CALL_DISPOSED = "CallDisposed"

    # Agent & Workforce
    AGENT_STATUS_CHANGED = "AgentStatusChanged"
    AGENT_BREAK_STARTED = "AgentBreakStarted"
    AGENT_BREAK_ENDED = "AgentBreakEnded"

    # Support & Tickets
    TICKET_CREATED = "TicketCreated"
    TICKET_ASSIGNED = "TicketAssigned"
    TICKET_RESOLVED = "TicketResolved"
    TICKET_SLA_WARNING = "SLAWarning"
    TICKET_SLA_BREACHED = "SLABreached"

    # Omnichannel Communication
    MESSAGE_RECEIVED = "MessageReceived"
    MESSAGE_SENT = "MessageSent"

    # Feedback & QA
    FEEDBACK_SUBMITTED = "FeedbackSubmitted"
    QA_EVALUATED = "QAEvaluated"

    # Workflows & Timeline
    WORKFLOW_TRIGGERED = "WorkflowTriggered"
    TIMELINE_RECORDED = "TimelineRecorded"


EventHandler = Callable[[DomainEvent], Coroutine[Any, Any, None]]


class EventBus:
    """
    Asynchronous event bus that decouples domain producers
    from subscribers (Analytics, Notifications, Automation, Timeline).
    """
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._all_event_subscribers: List[EventHandler] = []

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to a specific event type"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        """Subscribe a handler to all events (useful for Audit and Timeline)"""
        self._all_event_subscribers.append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event to all interested handlers concurrently"""
        handlers = self._subscribers.get(event.event_type, []).copy()
        handlers.extend(self._all_event_subscribers)

        if not handlers:
            return

        tasks = []
        for h in handlers:
            tasks.append(self._safe_execute(h, event))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute(self, handler: EventHandler, event: DomainEvent) -> None:
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error handling event {event.event_type} in {handler.__name__}: {str(e)}", exc_info=True)


# Global event bus singleton
event_bus = EventBus()
