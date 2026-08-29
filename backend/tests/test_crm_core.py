import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crm_lead_lifecycle_and_conversion(client: AsyncClient):
    """Test lead creation, scoring calculation, and atomic conversion to Customer 360 profile"""
    # 1. Register tenant
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Apex Global Sales",
        "full_name": "David Miller",
        "email": "david@apexsales.com",
        "password": "Password123!",
        "time_zone": "America/Chicago"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Lead
    lead_payload = {
        "first_name": "Ravi",
        "last_name": "Kumar",
        "email": "ravi.kumar@example.com",
        "phone_number": "+919876543210",
        "company_name": "Tech Corp India",
        "title": "Director of Technology",
        "source": "WEBSITE",
        "estimated_value": 25000.0,
        "notes": "Looking for 50-seat enterprise call center setup."
    }
    lead_res = await client.post("/api/v1/leads", json=lead_payload, headers=headers)
    assert lead_res.status_code == 201
    lead_data = lead_res.json()
    assert lead_data["score"] >= 80  # Score calculated from complete info & high deal value
    assert lead_data["status"] == "NEW"
    lead_id = lead_data["id"]

    # 3. Convert Lead
    conv_res = await client.post(f"/api/v1/leads/{lead_id}/convert", json={
        "create_customer": True,
        "customer_name": "Tech Corp India",
        "create_opportunity": True
    }, headers=headers)
    assert conv_res.status_code == 200
    conv_data = conv_res.json()
    assert conv_data["status"] == "CONVERTED"
    customer_id = conv_data["customer_id"]

    # 4. Fetch Customer 360 View
    c360_res = await client.get(f"/api/v1/customers/{customer_id}/360", headers=headers)
    assert c360_res.status_code == 200
    c360_data = c360_res.json()
    
    assert c360_data["customer"]["name"] == "Tech Corp India"
    assert len(c360_data["contacts"]) >= 1
    assert c360_data["contacts"][0]["first_name"] == "Ravi"
    assert len(c360_data["timeline"]) >= 1
    assert c360_data["timeline"][0]["event_type"] == "LeadConverted"


@pytest.mark.asyncio
async def test_crm_activities_and_timeline_events(client: AsyncClient):
    """Test task assignment and timeline event appending"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Global Support Group",
        "full_name": "Alice Johnson",
        "email": "alice@globalsupport.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Customer
    cust_res = await client.post("/api/v1/customers", json={
        "name": "Acme Logistics Inc.",
        "phone_number": "+18005550199",
        "email": "ops@acmelogistics.com"
    }, headers=headers)
    assert cust_res.status_code == 201
    cust_id = cust_res.json()["id"]

    # 2. Create Follow-up Activity
    act_res = await client.post("/api/v1/activities", json={
        "customer_id": cust_id,
        "activity_type": "FOLLOW_UP",
        "title": "Quarterly Business Review Call",
        "priority": "HIGH"
    }, headers=headers)
    assert act_res.status_code == 201
    assert act_res.json()["title"] == "Quarterly Business Review Call"

    # 3. Add Timeline Event (e.g. WhatsApp interaction)
    tl_res = await client.post("/api/v1/timeline", json={
        "customer_id": cust_id,
        "channel": "WHATSAPP",
        "event_type": "WhatsAppMessageReceived",
        "title": "Inbound WhatsApp Inquiry",
        "description": "Customer asked about contract renewal terms."
    }, headers=headers)
    assert tl_res.status_code == 201
    assert tl_res.json()["channel"] == "WHATSAPP"

    # 4. Fetch Timeline
    events_res = await client.get(f"/api/v1/timeline/{cust_id}", headers=headers)
    assert events_res.status_code == 200
    assert len(events_res.json()) >= 1
