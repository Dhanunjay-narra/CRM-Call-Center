# OmniChannel Cloud CRM & Call Center Core Platform

Enterprise-grade Cloud Contact Center & Customer Relationship Management (CRM) system powered by FastAPI, WebRTC telephony signaling, Automatic Call Distribution (ACD), Next.js 14, and real-time WebSocket state synchronization.

---

## 🌟 Key Architecture & Capabilities

- **Automatic Call Distribution (ACD) Engine**: Intelligent skill-based agent routing, priority wait-queues, and real-time telephony dispatcher.
- **WebRTC Softphone & Telephony**: Audio/video session signaling, active call controls (Mute, Hold, Resume, Warm Transfer, End Call).
- **Customer 360 & Contact Hub**: Unified customer dossier, LTV tracking, lifetime sentiment scoring, and interaction logs.
- **Support Tickets & SLA Lifecycle**: Omnichannel incident tracking, SLA timers, priority escalations, and resolution status.
- **Modern Next.js 14 Dashboard**: Softphone dialer widget, live queue radar, customer profile drawer, and agent status controls.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to view the agent workstation.

### 3. Run Test Suite
```bash
cd backend
pytest tests/ -v
```

---

## 🐳 Docker Deployment
```bash
docker-compose up --build
```
