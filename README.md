# CallSphere CRM: Intelligent Call Center + Customer Relationship Management Platform

[![CI Pipeline](https://github.com/Dhanunjay-narra/CRM-Call-Center/actions/workflows/ci.yml/badge.svg)](https://github.com/Dhanunjay-narra/CRM-Call-Center/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-000000.svg)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Cache-Redis-DC382D.svg)](https://redis.io)

**CallSphere CRM** is an enterprise-grade platform unifying CRM, Contact Center, Sales Pipelines, Omnichannel Messaging (Voice, Email, SMS, WhatsApp), Customer Support with SLA Engine, Visual IVR & Skill-based Call Routing, Workflow Automation, Quality Assurance & Scorecards, and Real-Time Operational Analytics into a cohesive system.

---

## 🌟 Key Architecture & Highlights

Every customer interaction—calls, WhatsApp messages, support tickets, quotations, and feedback—is synthesized into an immutable **Customer 360 Unified Timeline & Interaction Graph**.

```
Lead ➔ Prospect ➔ Contact ➔ Opportunity ➔ Sales Activity ➔ Customer ➔ Support ➔ Feedback ➔ Retention
```

### 22 Major Modules:
1. **Identity & Access Management**: Multi-factor auth, session security, 11-tier RBAC (`Super Admin` to `QA Analyst`), fine-grained permissions.
2. **Organization Management**: Multi-tenancy, departments, teams, branches, business hours, holiday calendars.
3. **Agent & Workforce Management**: Agent profiles, skills, languages, state transitions (`Available`, `On Call`, `ACW`, `Break`), adherence, occupancy.
4. **Lead Management**: Lifecycle, automated scoring, lead distribution, duplicate detection, conversion to Contact & Opportunity.
5. **Contact Management**: Profiles, multiple phones/emails, relationships, merge engine, consent tracking.
6. **Customer Management**: Central Customer 360, Health Scores, sentiment analysis, lifetime value calculations.
7. **Sales & Opportunity Management**: Multi-pipeline Kanban, custom stages, deal probability, forecasting, win/loss analysis.
8. **Activity & Task Management**: Unified calls, emails, SMS, WhatsApp, meetings, tasks, reminders, follow-ups.
9. **Campaign Management**: Multi-channel audience segmentation, automated execution, delivery tracking, ROI analytics.
10. **Call Center Management**: Inbound/outbound call lifecycle, softphone dialer, warm/cold transfer, hold, recordings, dispositions.
11. **Call Routing & Queue Engine**: Queue SLA, wait time estimations, overflow queues, callback queues, VIP prioritization.
12. **Smart Routing Engine**: Round robin, least busy, longest idle, skill-based, language-based, and customer priority routing.
13. **Visual IVR System**: Visual DTMF flow execution, text-to-speech, multi-lingual audio menus, emergency bypass.
14. **Omnichannel Communication**: Unified inbox for Voice, Email, SMS, and WhatsApp with provider abstraction.
15. **Customer Support & Ticketing**: Ticket lifecycle, SLA monitoring engine (80% warning alerts, automatic breach escalation).
16. **Knowledge Management**: Articles, FAQs, troubleshooting scripts, versioning, agent-facing vs. customer-facing separation.
17. **Workflow & Automation Engine**: Event-driven Trigger ➔ Condition ➔ Action engine with timers and cron triggers.
18. **Quality Assurance (QA)**: Call sampling, 100-point customizable QA scorecards, coaching workflows, dispute tracking.
19. **Customer Feedback Management**: CSAT, NPS, CES surveys, auto-escalation triggers on negative sentiment.
20. **Analytics & Reporting**: Operational KPIs (AHT, ASA, FCR, FRT, ACW, Occupancy, Service Level), sales velocity, customer health.
21. **Search & Customer Timeline**: Global search across all entities, interactive Customer 360 chronological timeline.
22. **Audit, Security & Compliance**: Immutable audit logging, field-level before/after diffs, login tracking, session enforcement.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Celery, WebSockets |
| **Database & Cache** | PostgreSQL 16, Redis 7, SQLite (Zero-config dev mode) |
| **Frontend** | Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide Icons, TanStack Query, Zustand |
| **DevOps & Testing** | Docker, Docker Compose, Pytest, Pytest-Asyncio, GitHub Actions CI |

---

## 🚀 Quick Start Guide

### Option 1: Run with Docker Compose (Recommended)
```bash
# Clone the repository
git clone https://github.com/Dhanunjay-narra/CRM-Call-Center.git
cd CRM-Call-Center

# Start all services (PostgreSQL, Redis, Backend API, Celery Worker, Next.js Frontend)
docker-compose up -d --build
```
Access the application:
- **Frontend App**: `http://localhost:3000`
- **Backend API Docs**: `http://localhost:8000/docs`
- **API Health Check**: `http://localhost:8000/api/v1/health`

### Option 2: Local Development Mode

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Run FastAPI server (uses SQLite auto-fallback if Postgres is not running)
uvicorn app.main:app --reload --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Running Automated Tests

```bash
# Run backend test suite
cd backend
pytest tests/ -v
```

---

## 📄 License
MIT License. Created for CallSphere CRM.
