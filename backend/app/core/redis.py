import json
import logging
from typing import Any, Dict, List, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


class InMemoryStore:
    """In-memory cache fallback when Redis is offline or disabled"""
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._presence: Dict[str, Dict[str, Any]] = {}
        self._queues: Dict[str, List[Dict[str, Any]]] = {}

    async def get(self, key: str) -> Optional[str]:
        val = self._data.get(key)
        if isinstance(val, (dict, list)):
            return json.dumps(val)
        return str(val) if val is not None else None

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        self._data[key] = value
        return True

    async def delete(self, key: str) -> bool:
        return self._data.pop(key, None) is not None

    async def set_agent_presence(self, agent_id: str, state: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self._presence[agent_id] = {
            "state": state,
            "updated_at": metadata.get("updated_at") if metadata else None,
            "metadata": metadata or {}
        }

    async def get_agent_presence(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._presence.get(agent_id)

    async def get_all_agent_presence(self) -> Dict[str, Dict[str, Any]]:
        return self._presence.copy()


class RedisManager:
    """Async Redis manager with automatic in-memory fallback"""
    def __init__(self):
        self._redis_client: Optional[aioredis.Redis] = None
        self._fallback = InMemoryStore()
        self._is_connected = False

    async def connect(self) -> None:
        if settings.REDIS_ENABLED:
            try:
                self._redis_client = aioredis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2.0
                )
                await self._redis_client.ping()
                self._is_connected = True
                logger.info("Connected to Redis successfully.")
            except Exception as e:
                logger.warning(f"Redis unavailable ({str(e)}). Using high-speed in-memory store fallback.")
                self._is_connected = False
        else:
            self._is_connected = False

    async def disconnect(self) -> None:
        if self._redis_client and self._is_connected:
            await self._redis_client.close()
            self._is_connected = False

    async def get(self, key: str) -> Optional[str]:
        if self._is_connected and self._redis_client:
            try:
                return await self._redis_client.get(key)
            except Exception:
                pass
        return await self._fallback.get(key)

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        if self._is_connected and self._redis_client:
            try:
                val_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                return await self._redis_client.set(key, val_str, ex=expire)
            except Exception:
                pass
        return await self._fallback.set(key, value, expire=expire)

    async def delete(self, key: str) -> bool:
        if self._is_connected and self._redis_client:
            try:
                return bool(await self._redis_client.delete(key))
            except Exception:
                pass
        return await self._fallback.delete(key)

    # Agent Presence
    async def set_agent_presence(self, agent_id: str, state: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        key = f"agent_presence:{agent_id}"
        data = {"state": state, "metadata": metadata or {}}
        if self._is_connected and self._redis_client:
            try:
                await self._redis_client.set(key, json.dumps(data), ex=86400)
            except Exception:
                pass
        await self._fallback.set_agent_presence(agent_id, state, metadata)

    async def get_agent_presence(self, agent_id: str) -> Optional[Dict[str, Any]]:
        if self._is_connected and self._redis_client:
            try:
                val = await self._redis_client.get(f"agent_presence:{agent_id}")
                if val:
                    return json.loads(val)
            except Exception:
                pass
        return await self._fallback.get_agent_presence(agent_id)

    async def get_all_agent_presence(self) -> Dict[str, Dict[str, Any]]:
        return await self._fallback.get_all_agent_presence()


redis_manager = RedisManager()
