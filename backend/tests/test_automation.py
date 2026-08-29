import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_workflow_automation_trigger_condition_and_action(client: AsyncClient):
    """Test Event Trigger -> Condition Evaluation -> Automated Task Execution"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Automation HQ",
        "full_name": "Automation Admin",
        "email": "admin@automationhq.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Workflow: Trigger on LeadCreated, Condition: score > 70, Action: CREATE_TASK
    wf_res = await client.post("/api/v1/workflows", json={
        "name": "High Value Lead Follow-up Automation",
        "trigger_type": "LeadCreated",
        "conditions": [
            {"field": "score", "operator": "greater_than", "value": 70}
        ],
        "actions": [
            {
                "action_type": "CREATE_TASK",
                "params": {
                    "title": "Immediate VIP Call Required for Hot Lead",
                    "priority": "HIGH"
                }
            },
            {
                "action_type": "NOTIFY_SUPERVISOR",
                "params": {
                    "message": "High score lead entered system"
                }
            }
        ]
    }, headers=headers)
    assert wf_res.status_code == 201
    wf_id = wf_res.json()["id"]

    # 2. Test Trigger with High Score Lead (Score = 85) -> Should Execute
    test_high = await client.post(f"/api/v1/workflows/{wf_id}/trigger-test", json={
        "score": 85,
        "email": "hotlead@example.com",
        "name": "Hot Lead"
    }, headers=headers)
    assert test_high.status_code == 200

    # 3. Check Workflow Logs
    logs_res = await client.get(f"/api/v1/workflows/{wf_id}/logs", headers=headers)
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) >= 1
    assert logs[0]["status"] == "SUCCESS"

    # 4. Test Trigger with Low Score Lead (Score = 40) -> Should Skip
    test_low = await client.post(f"/api/v1/workflows/{wf_id}/trigger-test", json={
        "score": 40,
        "email": "coldlead@example.com"
    }, headers=headers)
    assert test_low.status_code == 200

    logs_after = await client.get(f"/api/v1/workflows/{wf_id}/logs", headers=headers)
    assert logs_after.status_code == 200
    recent_log = logs_after.json()[0]
    assert recent_log["status"] == "SKIPPED"
