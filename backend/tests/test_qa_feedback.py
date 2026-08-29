import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_customer_feedback_csat_nps_and_escalation(client: AsyncClient):
    """Test customer feedback collection, sentiment evaluation, and auto-escalation on low score"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Feedback Loop Systems",
        "full_name": "QA Lead",
        "email": "qa@feedbackloop.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Customer
    cust_res = await client.post("/api/v1/customers", json={
        "name": "Ravi Customer Feedback",
        "email": "ravi.feedback@example.com"
    }, headers=headers)
    cust_id = cust_res.json()["id"]

    # 2. Submit Positive Rating (5/5)
    fb_pos = await client.post("/api/v1/feedback/submit", json={
        "customer_id": cust_id,
        "score": 5,
        "comment": "Outstanding support experience!",
        "agent_rating": 5
    }, headers=headers)
    assert fb_pos.status_code == 201
    assert fb_pos.json()["sentiment"] == "POSITIVE"
    assert fb_pos.json()["is_escalated"] is False

    # 3. Submit Negative Rating (1/5) -> Should Auto-Escalate
    fb_neg = await client.post("/api/v1/feedback/submit", json={
        "customer_id": cust_id,
        "score": 1,
        "comment": "Issue unresolved after multiple calls.",
        "agent_rating": 1
    }, headers=headers)
    assert fb_neg.status_code == 201
    assert fb_neg.json()["sentiment"] == "NEGATIVE"
    assert fb_neg.json()["is_escalated"] is True

    # 4. Verify Metrics
    metrics_res = await client.get("/api/v1/feedback/metrics", headers=headers)
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert metrics["total_responses"] == 2
    assert metrics["average_csat"] == 3.0
    assert metrics["negative_escalations_count"] == 1


@pytest.mark.asyncio
async def test_qa_scorecard_evaluation_and_coaching(client: AsyncClient):
    """Test 100-point QA evaluation on call recording and coaching session creation"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Quality First Center",
        "full_name": "QA Supervisor",
        "email": "supervisor@qualityfirst.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get Scorecard
    sc_res = await client.get("/api/v1/qa/scorecards", headers=headers)
    assert sc_res.status_code == 200
    scorecard = sc_res.json()[0]
    sc_id = scorecard["id"]

    # 2. Create Call to evaluate
    call_res = await client.post("/api/v1/calls/initiate", json={
        "from_number": "+18001112222",
        "to_number": "+15554443333"
    }, headers=headers)
    call_id = call_res.json()["id"]

    # 3. Submit QA Evaluation (Score: 92/100 -> PASS)
    eval_res = await client.post("/api/v1/qa/evaluations", json={
        "scorecard_id": sc_id,
        "call_id": call_id,
        "agent_user_id": "test-agent-user",
        "section_scores": {
            "Greeting & Verification": 20.0,
            "Communication & Empathy": 14.0,
            "Product Knowledge": 15.0,
            "Problem Resolution": 18.0,
            "Compliance & Security": 13.0,
            "Closing & Next Steps": 12.0
        },
        "feedback_notes": "Great active listening and empathy demonstrated."
    }, headers=headers)
    assert eval_res.status_code == 201
    eval_data = eval_res.json()
    assert eval_data["total_score"] == 92.0
    assert eval_data["passed"] is True
    eval_id = eval_data["id"]

    # 4. Create Coaching Session
    coach_res = await client.post("/api/v1/qa/coaching", json={
        "agent_user_id": "test-agent-user",
        "evaluation_id": eval_id,
        "focus_area": "Product Knowledge & Compliance",
        "action_items": ["Review updated insurance policy guide", "Complete security refresh module"]
    }, headers=headers)
    assert coach_res.status_code == 201
    assert coach_res.json()["focus_area"] == "Product Knowledge & Compliance"
