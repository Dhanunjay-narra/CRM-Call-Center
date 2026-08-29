import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.core.base_models import TenantBaseModel, utc_now


class RoutingStrategy(str, enum.Enum):
    ROUND_ROBIN = "ROUND_ROBIN"
    LEAST_BUSY = "LEAST_BUSY"
    LONGEST_IDLE = "LONGEST_IDLE"
    SKILL_BASED = "SKILL_BASED"
    LANGUAGE_BASED = "LANGUAGE_BASED"
    PRIORITY_BASED = "PRIORITY_BASED"
    CUSTOMER_BASED = "CUSTOMER_BASED"
    CAMPAIGN_BASED = "CAMPAIGN_BASED"


class IVRNodeType(str, enum.Enum):
    PLAY_MESSAGE = "PLAY_MESSAGE"
    GATHER_DTMF = "GATHER_DTMF"
    LANGUAGE_SELECT = "LANGUAGE_SELECT"
    BRANCH = "BRANCH"
    TRANSFER_QUEUE = "TRANSFER_QUEUE"
    TRANSFER_AGENT = "TRANSFER_AGENT"
    VOICEMAIL = "VOICEMAIL"
    DISCONNECT = "DISCONNECT"


class CallQueue(TenantBaseModel):
    """Inbound Call Queue with SLA thresholds and overflow routing"""
    __tablename__ = "cc_call_queues"

    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    strategy = Column(Enum(RoutingStrategy), default=RoutingStrategy.LONGEST_IDLE, nullable=False)
    
    sla_threshold_seconds = Column(Integer, default=20, nullable=False)  # 20 seconds standard SLA
    max_queue_size = Column(Integer, default=50, nullable=False)
    timeout_seconds = Column(Integer, default=300, nullable=False)        # 5 minutes max wait
    
    # Required skills and languages for queue
    required_skills = Column(JSON, default=list, nullable=False)
    default_language = Column(String(10), default="en", nullable=False)
    
    overflow_queue_id = Column(String(36), nullable=True)
    enable_callback = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    members = relationship("QueueMember", back_populates="queue", cascade="all, delete-orphan")


class QueueMember(TenantBaseModel):
    """Mapping agents to Queues with priority and skill weights"""
    __tablename__ = "cc_queue_members"

    queue_id = Column(String(36), ForeignKey("cc_call_queues.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(String(36), ForeignKey("cc_agent_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), nullable=False)
    priority = Column(Integer, default=1, nullable=False)  # Higher number = higher priority
    weight = Column(Integer, default=100, nullable=False)

    queue = relationship("CallQueue", back_populates="members")


class IVRFlow(TenantBaseModel):
    """Visual IVR Tree definition"""
    __tablename__ = "cc_ivr_flows"

    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    entry_node_id = Column(String(50), nullable=True)
    
    # Full Visual Flow graph stored as JSON nodes and edges
    flow_data = Column(JSON, default=dict, nullable=False)

    nodes = relationship("IVRNode", back_populates="flow", cascade="all, delete-orphan")


class IVRNode(TenantBaseModel):
    """Individual node within an IVR flow"""
    __tablename__ = "cc_ivr_nodes"

    flow_id = Column(String(36), ForeignKey("cc_ivr_flows.id", ondelete="CASCADE"), nullable=False, index=True)
    node_key = Column(String(50), nullable=False, index=True)  # e.g. "welcome_node", "language_menu"
    node_type = Column(Enum(IVRNodeType), nullable=False)
    
    prompt_text = Column(Text, nullable=True)
    prompt_audio_url = Column(String(500), nullable=True)
    tts_voice = Column(String(50), default="female_1", nullable=False)
    
    # DTMF options mapping: {"1": "sales_queue", "2": "support_queue", "0": "operator"}
    dtmf_options = Column(JSON, default=dict, nullable=False)
    target_queue_id = Column(String(36), nullable=True)
    
    flow = relationship("IVRFlow", back_populates="nodes")
