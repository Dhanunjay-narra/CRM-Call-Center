import json
import logging
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages live WebSocket connections for:
    - User/Agent notifications
    - Telephony Softphone events (Incoming call, Ringing, Connected, Ended)
    - Supervisor Live Monitoring (Queue metrics, Agent states)
    - Omnichannel Chat messages
    """
    def __init__(self):
        # user_id -> Set of active WebSocket connections
        self._user_connections: Dict[str, Set[WebSocket]] = {}
        # org_id -> Set of active WebSocket connections
        self._org_connections: Dict[str, Set[WebSocket]] = {}
        # supervisor channel connections for an organization
        self._supervisor_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str, org_id: str, is_supervisor: bool = False) -> None:
        await websocket.accept()
        
        # User connection
        if user_id not in self._user_connections:
            self._user_connections[user_id] = set()
        self._user_connections[user_id].add(websocket)

        # Org connection
        if org_id not in self._org_connections:
            self._org_connections[org_id] = set()
        self._org_connections[org_id].add(websocket)

        # Supervisor connection
        if is_supervisor:
            if org_id not in self._supervisor_connections:
                self._supervisor_connections[org_id] = set()
            self._supervisor_connections[org_id].add(websocket)

        logger.info(f"WebSocket connected: user={user_id}, org={org_id}, supervisor={is_supervisor}")

    def disconnect(self, websocket: WebSocket, user_id: str, org_id: str) -> None:
        if user_id in self._user_connections:
            self._user_connections[user_id].discard(websocket)
            if not self._user_connections[user_id]:
                del self._user_connections[user_id]

        if org_id in self._org_connections:
            self._org_connections[org_id].discard(websocket)
            if not self._org_connections[org_id]:
                del self._org_connections[org_id]

        if org_id in self._supervisor_connections:
            self._supervisor_connections[org_id].discard(websocket)
            if not self._supervisor_connections[org_id]:
                del self._supervisor_connections[org_id]

        logger.info(f"WebSocket disconnected: user={user_id}, org={org_id}")

    async def send_to_user(self, user_id: str, message: Dict[str, Any]) -> None:
        """Send message directly to a specific user's active devices"""
        conns = self._user_connections.get(user_id, set()).copy()
        for ws in conns:
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed sending WS message to user {user_id}: {e}")
                self._user_connections.get(user_id, set()).discard(ws)

    async def broadcast_to_org(self, org_id: str, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients in an organization"""
        conns = self._org_connections.get(org_id, set()).copy()
        for ws in conns:
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed broadcasting WS to org {org_id}: {e}")
                self._org_connections.get(org_id, set()).discard(ws)

    async def broadcast_to_supervisors(self, org_id: str, message: Dict[str, Any]) -> None:
        """Broadcast live call/queue updates to supervisors in an organization"""
        conns = self._supervisor_connections.get(org_id, set()).copy()
        for ws in conns:
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed broadcasting WS to supervisors in org {org_id}: {e}")
                self._supervisor_connections.get(org_id, set()).discard(ws)


ws_manager = WebSocketManager()
