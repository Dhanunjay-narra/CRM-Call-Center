"""
CallSphere CRM Omnichannel Subsystem - Message Hub & Dispatch Pipeline 21
Supports WhatsApp Cloud REST payloads, SMS SMPP encoding, Email MIME synthesis,
and dynamic variable replacement engines.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class MessagePayloadBuilder_21:
    @staticmethod
    def build_whatsapp_template(to_number: str, template_name: str, parameters: List[str]) -> Dict[str, Any]:
        components = []
        if parameters:
            components.append({
                "type": "body",
                "parameters": [{"type": "text", "text": str(p)} for p in parameters]
            })
        return {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"},
                "components": components
            }
        }

    @staticmethod
    def render_macro_string(template_str: str, values: Dict[str, Any]) -> str:
        res = template_str
        for k, v in values.items():
            res = res.replace("{{ " + k + " }}", str(v)).replace("{{" + k + "}}", str(v))
        return res
