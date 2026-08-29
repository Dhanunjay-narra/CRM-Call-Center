import uuid
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Abstract interface for omnichannel delivery providers"""
    @abstractmethod
    async def send_message(self, to: str, content: str, subject: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass


class SimulatorEmailProvider(BaseProvider):
    async def send_message(self, to: str, content: str, subject: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        msg_id = f"sim_email_{uuid.uuid4().hex[:12]}"
        logger.info(f"[Simulator Email] To: {to} | Subject: '{subject}' | Body preview: '{content[:50]}...'")
        return {
            "success": True,
            "provider_message_id": msg_id,
            "provider": "simulator_email",
            "delivered_at": datetime.now(timezone.utc).isoformat()
        }


class SimulatorSMSProvider(BaseProvider):
    async def send_message(self, to: str, content: str, subject: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        msg_id = f"sim_sms_{uuid.uuid4().hex[:12]}"
        logger.info(f"[Simulator SMS] To: {to} | Body: '{content}'")
        return {
            "success": True,
            "provider_message_id": msg_id,
            "provider": "simulator_sms",
            "delivered_at": datetime.now(timezone.utc).isoformat()
        }


class SimulatorWhatsAppProvider(BaseProvider):
    async def send_message(self, to: str, content: str, subject: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        msg_id = f"sim_wa_{uuid.uuid4().hex[:12]}"
        logger.info(f"[Simulator WhatsApp] To: {to} | Body: '{content}'")
        return {
            "success": True,
            "provider_message_id": msg_id,
            "provider": "simulator_whatsapp",
            "delivered_at": datetime.now(timezone.utc).isoformat()
        }


# Provider Registry
email_provider = SimulatorEmailProvider()
sms_provider = SimulatorSMSProvider()
whatsapp_provider = SimulatorWhatsAppProvider()
