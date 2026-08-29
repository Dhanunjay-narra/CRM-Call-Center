import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["acd_engine"] == "online"

@pytest.mark.asyncio
async def test_agent_registration_and_login_flow(client: AsyncClient):
    # 1. Register agent
    reg_res = await client.post("/api/v1/agents/register", json={
        "name": "Sarah Connor",
        "email": "sarah.connor@callcenter.io",
        "password": "SecurePassword123!",
        "skills": "TECHNICAL,BILLING"
    })
    assert reg_res.status_code == 201
    agent_data = reg_res.json()
    assert agent_data["name"] == "Sarah Connor"
    assert agent_data["status"] == "AVAILABLE"
    agent_id = agent_data["id"]

    # 2. Login agent
    login_res = await client.post("/api/v1/agents/login", json={
        "email": "sarah.connor@callcenter.io",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 3. Update status
    status_res = await client.patch(f"/api/v1/agents/{agent_id}/status", json={
        "status": "BUSY"
    })
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "BUSY"

@pytest.mark.asyncio
async def test_customer_management_flow(client: AsyncClient):
    # 1. Create customer
    res = await client.post("/api/v1/customers", json={
        "first_name": "Elon",
        "last_name": "Musk",
        "email": "elon@spacex.com",
        "phone": "+14155552671",
        "company": "SpaceX",
        "tier": "ENTERPRISE"
    })
    assert res.status_code == 201
    cust = res.json()
    assert cust["first_name"] == "Elon"

    # 2. Query by phone
    phone_res = await client.get(f"/api/v1/customers/by-phone/{cust['phone']}")
    assert phone_res.status_code == 200
    assert phone_res.json()["email"] == "elon@spacex.com"

@pytest.mark.asyncio
async def test_acd_call_queue_and_actions(client: AsyncClient):
    # 1. Register available agent
    ag_res = await client.post("/api/v1/agents/register", json={
        "name": "Alex Murphy",
        "email": "alex.murphy@callcenter.io",
        "password": "PassWord!123"
    })
    agent_id = ag_res.json()["id"]

    # 2. Register customer
    cust_res = await client.post("/api/v1/customers", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+18005551234"
    })
    cust_id = cust_res.json()["id"]

    # 3. Initiate Call
    call_res = await client.post("/api/v1/calls/initiate", json={
        "customer_id": cust_id,
        "direction": "INBOUND",
        "queue_name": "Priority VIP Support",
        "priority": 5
    })
    assert call_res.status_code == 201
    call_data = call_res.json()
    call_id = call_data["call_id"]
    assert call_data["agent_id"] == agent_id

    # 4. Answer Call
    ans_res = await client.post(f"/api/v1/calls/{call_id}/action", json={
        "action": "ANSWER",
        "agent_id": agent_id
    })
    assert ans_res.status_code == 200
    assert ans_res.json()["status"] == "ACTIVE"

    # 5. Hold & Resume
    hold_res = await client.post(f"/api/v1/calls/{call_id}/action", json={"action": "HOLD"})
    assert hold_res.json()["status"] == "ON_HOLD"
    resume_res = await client.post(f"/api/v1/calls/{call_id}/action", json={"action": "RESUME"})
    assert resume_res.json()["status"] == "ACTIVE"

    # 6. End Call
    end_res = await client.post(f"/api/v1/calls/{call_id}/action", json={"action": "END"})
    assert end_res.json()["status"] == "COMPLETED"

@pytest.mark.asyncio
async def test_support_tickets_lifecycle(client: AsyncClient):
    cust_res = await client.post("/api/v1/customers", json={
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice.smith@example.com",
        "phone": "+19998887777"
    })
    cust_id = cust_res.json()["id"]

    # 1. Create Ticket
    t_res = await client.post("/api/v1/tickets", json={
        "customer_id": cust_id,
        "subject": "Billing issue with recurring subscription",
        "description": "Invoice #4892 was charged twice.",
        "priority": "HIGH",
        "channel": "VOICE_CALL"
    })
    assert t_res.status_code == 201
    t_data = t_res.json()
    ticket_id = t_data["id"]

    # 2. Update Ticket
    patch_res = await client.patch(f"/api/v1/tickets/{ticket_id}", json={
        "status": "RESOLVED"
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "RESOLVED"

@pytest.mark.asyncio
async def test_webrtc_signaling(client: AsyncClient):
    sig_res = await client.post("/api/v1/calls/signal", json={
        "call_id": "CALL-12345",
        "type": "offer",
        "payload": {"sdp": "v=0\r\no=- 123 456 IN IP4 127.0.0.1"}
    })
    assert sig_res.status_code == 200
    assert sig_res.json()["status"] == "signaling_dispatched"
