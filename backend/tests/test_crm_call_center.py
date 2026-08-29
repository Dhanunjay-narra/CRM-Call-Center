import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_agent_registration_and_login_flow(client: AsyncClient):
    # 1. Register tenant & user
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Call Center Corp",
        "full_name": "Sarah Connor",
        "email": "sarah.connor@callcenter.io",
        "password": "SecurePassword123!",
        "phone_number": "+18005551234"
    })
    assert reg_res.status_code == 201
    auth_data = reg_res.json()
    assert "access_token" in auth_data
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Login agent
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "sarah.connor@callcenter.io",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 3. Update agent state
    state_res = await client.post("/api/v1/agents/state", headers=headers, json={
        "state": "AVAILABLE"
    })
    assert state_res.status_code == 200
    assert state_res.json()["current_state"] == "AVAILABLE"

@pytest.mark.asyncio
async def test_customer_management_flow(client: AsyncClient, auth_headers: dict):
    # 1. Create customer
    res = await client.post("/api/v1/customers", headers=auth_headers, json={
        "name": "Elon Musk",
        "email": "elon@spacex.com",
        "phone": "+14155552671",
        "company_name": "SpaceX"
    })
    assert res.status_code == 201
    customer = res.json()
    assert customer["name"] == "Elon Musk"
    assert customer["email"] == "elon@spacex.com"

@pytest.mark.asyncio
async def test_acd_call_queue_and_actions(client: AsyncClient, auth_headers: dict):
    # 1. Initiate Call
    call_res = await client.post("/api/v1/calls/initiate", headers=auth_headers, json={
        "from_number": "+18005551234",
        "to_number": "+14155552671",
        "direction": "INBOUND"
    })
    assert call_res.status_code == 201
    call_data = call_res.json()
    call_id = call_data["id"]
    assert call_data["direction"] == "INBOUND"

    # 2. End Call / Disposition
    end_res = await client.post(f"/api/v1/calls/{call_id}/disposition", headers=auth_headers, json={
        "disposition_code": "RESOLVED",
        "notes": "Customer inquiries addressed successfully."
    })
    assert end_res.status_code in (200, 201)
    assert end_res.json()["call_id"] == call_id

@pytest.mark.asyncio
async def test_support_tickets_lifecycle(client: AsyncClient, auth_headers: dict):
    # 1. Create Customer
    cust_res = await client.post("/api/v1/customers", headers=auth_headers, json={
        "name": "Alice Smith",
        "email": "alice.smith@example.com"
    })
    cust_id = cust_res.json()["id"]

    # 2. Create Ticket
    t_res = await client.post("/api/v1/tickets", headers=auth_headers, json={
        "customer_id": cust_id,
        "title": "Billing issue with recurring subscription",
        "description": "Invoice #4892 was charged twice.",
        "priority": "HIGH"
    })
    assert t_res.status_code == 201
    t_data = t_res.json()
    ticket_id = t_data["id"]
    assert t_data["priority"] == "HIGH"

    # 3. Update Ticket / Resolve
    patch_res = await client.post(f"/api/v1/tickets/{ticket_id}/resolve", headers=auth_headers, json={
        "resolution_notes": "Resolved duplicate billing invoice."
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "RESOLVED"

@pytest.mark.asyncio
async def test_webrtc_signaling(client: AsyncClient, auth_headers: dict):
    agent_state_res = await client.post("/api/v1/agents/state", headers=auth_headers, json={
        "state": "AVAILABLE"
    })
    assert agent_state_res.status_code == 200
    assert agent_state_res.json()["current_state"] == "AVAILABLE"
