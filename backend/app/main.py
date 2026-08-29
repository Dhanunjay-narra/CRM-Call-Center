from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base
from app.core.websocket_manager import ws_manager
from app.modules.agents.router import router as agents_router
from app.modules.customers.router import router as customers_router
from app.modules.calls.router import router as calls_router
from app.modules.tickets.router import router as tickets_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(customers_router, prefix=settings.API_V1_STR)
app.include_router(calls_router, prefix=settings.API_V1_STR)
app.include_router(tickets_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "CRM-Call-Center",
        "version": settings.VERSION,
        "acd_engine": "online",
        "webrtc_gateway": "ready"
    }

@app.websocket("/ws/telephony/{agent_id}")
async def telephony_websocket(websocket: WebSocket, agent_id: str):
    await ws_manager.connect(agent_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(agent_id, websocket)
