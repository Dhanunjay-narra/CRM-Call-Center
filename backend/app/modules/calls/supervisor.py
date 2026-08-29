from enum import Enum
from dataclasses import dataclass

class SupervisionMode(str, Enum):
    MONITOR = "MONITOR"    # Silent listen
    WHISPER = "WHISPER"    # Talk to agent only
    BARGE_IN = "BARGE_IN"  # Talk to all parties

@dataclass
class SupervisorSession:
    supervisor_id: str
    call_id: str
    mode: SupervisionMode

class SupervisorManager:
    def __init__(self):
        self.active_sessions = {}

    def attach_supervisor(self, supervisor_id: str, call_id: str, mode: SupervisionMode) -> SupervisorSession:
        sess = SupervisorSession(supervisor_id=supervisor_id, call_id=call_id, mode=mode)
        self.active_sessions[supervisor_id] = sess
        return sess
