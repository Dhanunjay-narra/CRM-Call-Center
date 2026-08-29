import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_agent_workforce_states(client: AsyncClient):
    """Test agent state changes, break durations, and presence tracking"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "CallCenter Direct",
        "full_name": "Agent Michael",
        "email": "michael@ccdirect.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch Agent Profile
    prof_res = await client.get("/api/v1/agents/profile", headers=headers)
    assert prof_res.status_code == 200
    assert prof_res.json()["current_state"] == "AVAILABLE"

    # 2. Put Agent on Lunch Break
    break_res = await client.post("/api/v1/agents/state", json={
        "state": "BREAK",
        "break_type": "LUNCH"
    }, headers=headers)
    assert break_res.status_code == 200
    assert break_res.json()["current_state"] == "BREAK"
    assert break_res.json()["current_break_type"] == "LUNCH"

    # 3. Return to Available
    avail_res = await client.post("/api/v1/agents/state", json={
        "state": "AVAILABLE"
    }, headers=headers)
    assert avail_res.status_code == 200
    assert avail_res.json()["current_state"] == "AVAILABLE"


@pytest.mark.asyncio
async def test_softphone_call_lifecycle_and_disposition(client: AsyncClient):
    """Test complete softphone call lifecycle: Initiate -> Ring -> Answer -> Hold -> End -> Disposition"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Vanguard Telecom",
        "full_name": "Agent Jessica",
        "email": "jessica@vanguardtel.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a customer to test automatic Caller ID resolution
    cust_res = await client.post("/api/v1/customers", json={
        "name": "Ravi Telephony Test",
        "phone_number": "+1555019876",
        "email": "ravi.test@example.com"
    }, headers=headers)
    cust_id = cust_res.json()["id"]

    # 2. Initiate Call to Customer Phone
    call_res = await client.post("/api/v1/calls/initiate", json={
        "direction": "OUTBOUND",
        "from_number": "+18005550000",
        "to_number": "+1555019876"
    }, headers=headers)
    assert call_res.status_code == 201
    call_data = call_res.json()
    assert call_data["status"] == "RINGING"
    assert call_data["customer_id"] == cust_id  # Automatically matched via Caller ID
    call_id = call_data["id"]

    # 3. Answer Call
    ans_res = await client.post(f"/api/v1/calls/{call_id}/answer", headers=headers)
    assert ans_res.status_code == 200
    assert ans_res.json()["status"] == "IN_PROGRESS"

    # 4. Toggle Hold
    hold_res = await client.post(f"/api/v1/calls/{call_id}/hold?hold=true", headers=headers)
    assert hold_res.status_code == 200
    assert hold_res.json()["status"] == "ON_HOLD"

    resume_res = await client.post(f"/api/v1/calls/{call_id}/hold?hold=false", headers=headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "IN_PROGRESS"

    # 5. End Call
    end_res = await client.post(f"/api/v1/calls/{call_id}/end", headers=headers)
    assert end_res.status_code == 200
    ended_data = end_res.json()
    assert ended_data["status"] == "COMPLETED"
    assert "recording_url" in ended_data

    # Agent should now be in ACW
    prof_res = await client.get("/api/v1/agents/profile", headers=headers)
    assert prof_res.json()["current_state"] == "AFTER_CALL_WORK"

    # 6. Submit Disposition
    disp_res = await client.post(f"/api/v1/calls/{call_id}/disposition", json={
        "disposition_code": "INTERESTED",
        "category": "Sales Pitch",
        "summary_notes": "Customer interested in upgraded 100 Mbps fiber line.",
        "follow_up_required": True
    }, headers=headers)
    assert disp_res.status_code == 201
    assert disp_res.json()["disposition_code"] == "INTERESTED"

    # Agent should now be back to AVAILABLE
    prof_res_after = await client.get("/api/v1/agents/profile", headers=headers)
    assert prof_res_after.json()["current_state"] == "AVAILABLE"

    # Verify Timeline has Call event recorded
    timeline_res = await client.get(f"/api/v1/timeline/{cust_id}", headers=headers)
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert any(e["channel"] == "CALL" for e in events)
