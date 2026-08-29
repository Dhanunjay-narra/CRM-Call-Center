import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db
from app.core.redis import redis_manager
from app.core.websocket_manager import ws_manager
from app.core.exceptions import DomainException
from app.api.v1 import api_router

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespans"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.PROJECT_VERSION} in {settings.ENVIRONMENT} mode...")
    
    # Initialize database tables
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    # Connect to Redis
    await redis_manager.connect()

    yield

    # Shutdown
    logger.info("Shutting down CallSphere CRM...")
    await redis_manager.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Domain Exception Handler
@app.exception_handler(DomainException)
async def domain_exception_handler(request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": exc.error_code,
            "detail": exc.detail,
            "extra_data": exc.extra_data
        }
    )


# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


# Real-time WebSocket Gateway
@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str = Query(default="guest-agent"),
    org_id: str = Query(default="default-org"),
    supervisor: bool = Query(default=False)
):
    """
    Unified WebSocket gateway for:
    - Real-time softphone telephony events
    - Supervisor queue and agent telemetry
    - Omnichannel live chat messages
    - Instant notification broadcasts
    """
    await ws_manager.connect(websocket, user_id=user_id, org_id=org_id, is_supervisor=supervisor)
    try:
        while True:
            data = await websocket.receive_json()
            # Echo or process incoming WebSocket command (e.g. heartbeat or agent status change)
            msg_type = data.get("type", "ping")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "status_update":
                new_state = data.get("state", "AVAILABLE")
                await redis_manager.set_agent_presence(user_id, new_state, data.get("metadata"))
                await ws_manager.broadcast_to_supervisors(org_id, {
                    "type": "agent_state_changed",
                    "agent_id": user_id,
                    "state": new_state
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id=user_id, org_id=org_id)
    except Exception as e:
        logger.warning(f"WebSocket connection error: {e}")
        ws_manager.disconnect(websocket, user_id=user_id, org_id=org_id)
