from dataclasses import dataclass
from typing import List, Dict

@dataclass
class SMSMessage:
    message_id: str
    from_phone: str
    to_phone: str
    content: str
    status: str = "DELIVERED"

class SMSGatewayDispatcher:
    def __init__(self):
        self.message_history: List[SMSMessage] = []

    def dispatch_sms(self, from_phone: str, to_phone: str, content: str) -> SMSMessage:
        msg = SMSMessage(
            message_id=f"SMS-{len(self.message_history) + 1}",
            from_phone=from_phone,
            to_phone=to_phone,
            content=content
        )
        self.message_history.append(msg)
        return msg
