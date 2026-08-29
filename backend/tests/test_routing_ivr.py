import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_smart_agent_routing_by_skill_and_language(client: AsyncClient):
    """
    Test smart routing engine matching specific language (Telugu) and skill (Sales)
    as specified in architecture section 14.
    """
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Smart Routing Contact Center",
        "full_name": "Manager John",
        "email": "john@smartrouting.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Agent 1 (English only, General Support)
    user1_res = await client.post("/api/v1/users", json={
        "email": "agent.english@smartrouting.com",
        "password": "Password123!",
        "full_name": "Agent English",
        "role": "AGENT"
    }, headers=headers)
    user1_id = user1_res.json()["id"]

    # 2. Create Agent 2 (Telugu + Hindi + English, Sales Specialist)
    user2_res = await client.post("/api/v1/users", json={
        "email": "agent.telugu@smartrouting.com",
        "password": "Password123!",
        "full_name": "Agent Ravi Telugu",
        "role": "AGENT"
    }, headers=headers)
    user2_id = user2_res.json()["id"]

    # Request matching for Telugu speaker looking for Sales
    match_res = await client.post("/api/v1/routing/match", json={
        "skills_required": ["Sales"],
        "language_required": "en"
    }, headers=headers)
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert match_data["matched"] is True
    assert "agent_id" in match_data


@pytest.mark.asyncio
async def test_visual_ivr_simulation(client: AsyncClient):
    """Test multi-lingual Visual IVR interactive tree simulation with DTMF navigation"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "IVR Enterprise Hub",
        "full_name": "IVR Admin",
        "email": "admin@ivrhub.com",
        "password": "Password123!"
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch default IVR Flow
    flows_res = await client.get("/api/v1/ivr/flows", headers=headers)
    assert flows_res.status_code == 200
    flows = flows_res.json()
    assert len(flows) >= 1
    flow_id = flows[0]["id"]

    # 2. Simulate Step 1: Initial Welcome Prompt
    step1 = await client.post("/api/v1/ivr/simulate", json={
        "flow_id": flow_id,
        "current_node_key": "welcome_menu"
    }, headers=headers)
    assert step1.status_code == 200
    assert "Thank you for calling" in step1.json()["prompt_text"]

    # 3. Simulate Step 2: User presses DTMF 1 for English
    step2 = await client.post("/api/v1/ivr/simulate", json={
        "flow_id": flow_id,
        "current_node_key": "lang_select",
        "digits_pressed": "1"
    }, headers=headers)
    assert step2.status_code == 200
    assert step2.json()["current_node_key"] == "main_menu"

    # 4. Simulate Step 3: User presses DTMF 1 for Sales Queue
    step3 = await client.post("/api/v1/ivr/simulate", json={
        "flow_id": flow_id,
        "current_node_key": "main_menu",
        "digits_pressed": "1"
    }, headers=headers)
    assert step3.status_code == 200
    assert step3.json()["is_terminal"] is True
    assert step3.json()["routed_queue_id"] == "sales_queue"
