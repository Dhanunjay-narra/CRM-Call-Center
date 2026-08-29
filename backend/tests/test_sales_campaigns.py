import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_sales_pipeline_opportunity_and_forecasting(client: AsyncClient):
    """Test pipelines, deal stage movements, forecasting calculations, and win rates"""
    # 1. Register Tenant
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Horizon Sales Group",
        "full_name": "Marcus Vance",
        "email": "marcus@horizonsales.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Default Pipeline
    pipe_res = await client.get("/api/v1/pipelines", headers=headers)
    assert pipe_res.status_code == 200
    pipelines = pipe_res.json()
    assert len(pipelines) >= 1
    pipeline = pipelines[0]
    stages = pipeline["stages"]
    assert len(stages) >= 6
    discovery_stage = stages[0]
    won_stage = [s for s in stages if s["is_won_stage"]][0]

    # 3. Create Opportunity
    opp_payload = {
        "pipeline_id": pipeline["id"],
        "stage_id": discovery_stage["id"],
        "title": "Enterprise Cloud Migration Deal",
        "amount": 50000.0,
        "currency": "USD"
    }
    opp_res = await client.post("/api/v1/opportunities", json=opp_payload, headers=headers)
    assert opp_res.status_code == 201
    opp_data = opp_res.json()
    assert opp_data["probability"] == discovery_stage["default_probability"]
    opp_id = opp_data["id"]

    # 4. Check Forecast (Open Deal)
    forecast_res = await client.get("/api/v1/sales/forecast", headers=headers)
    assert forecast_res.status_code == 200
    forecast_data = forecast_res.json()
    assert forecast_data["total_pipeline_value"] == 50000.0
    assert forecast_data["weighted_forecast_value"] == 50000.0 * (discovery_stage["default_probability"] / 100.0)

    # 5. Move Deal to Won Stage
    update_res = await client.patch(f"/api/v1/opportunities/{opp_id}", json={
        "stage_id": won_stage["id"]
    }, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "WON"
    assert update_res.json()["probability"] == 100

    # 6. Check Forecast (Won Deal)
    won_forecast = await client.get("/api/v1/sales/forecast", headers=headers)
    assert won_forecast.status_code == 200
    won_data = won_forecast.json()
    assert won_data["won_revenue"] == 50000.0
    assert won_data["win_rate_percent"] == 100.0


@pytest.mark.asyncio
async def test_campaign_creation_and_execution(client: AsyncClient):
    """Test creating and blasting an omnichannel marketing campaign"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Nexus Marketing",
        "full_name": "Elena Rostova",
        "email": "elena@nexusmktg.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Campaign
    camp_res = await client.post("/api/v1/campaigns", json={
        "name": "Q3 Telemarketing Outreach",
        "campaign_type": "SALES",
        "channel": "VOICE_CALL",
        "budget": 2500.0,
        "subject": "Exclusive Discount on Enterprise Plans",
        "message_body": "Hello {name}, we have a special promotion for you!"
    }, headers=headers)
    assert camp_res.status_code == 201
    camp_data = camp_res.json()
    assert camp_data["status"] == "DRAFT"
    camp_id = camp_data["id"]

    # 2. Execute Campaign
    exec_res = await client.post(f"/api/v1/campaigns/{camp_id}/execute", headers=headers)
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["status"] == "COMPLETED"
    assert exec_data["total_sent"] > 0
    assert exec_data["revenue_generated"] > 0
