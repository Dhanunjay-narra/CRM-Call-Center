import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_support_ticket_lifecycle_and_resolution(client: AsyncClient):
    """Test creating support ticket, calculating SLA targets, commenting, and resolving"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Apex Support Services",
        "full_name": "Support Lead",
        "email": "lead@apexsupport.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Customer
    cust_res = await client.post("/api/v1/customers", json={
        "name": "Acme Manufacturing",
        "email": "support@acmemfg.com"
    }, headers=headers)
    cust_id = cust_res.json()["id"]

    # 2. Create Critical Support Ticket
    ticket_res = await client.post("/api/v1/tickets", json={
        "customer_id": cust_id,
        "title": "Production Database Server Down",
        "description": "Critical outage affecting 500+ users.",
        "category": "Database Infrastructure",
        "priority": "CRITICAL"
    }, headers=headers)
    assert ticket_res.status_code == 201
    ticket = ticket_res.json()
    assert ticket["priority"] == "CRITICAL"
    assert ticket["status"] == "NEW"
    assert ticket["first_response_due_at"] is not None
    assert ticket["resolution_due_at"] is not None
    ticket_id = ticket["id"]

    # 3. Add Agent Reply
    comment_res = await client.post(f"/api/v1/tickets/{ticket_id}/comments", json={
        "body": "Engineering team is currently investigating server logs.",
        "is_internal_note": False
    }, headers=headers)
    assert comment_res.status_code == 201
    assert comment_res.json()["is_internal_note"] is False

    # Check that ticket first_responded_at is now set
    t_check = await client.get(f"/api/v1/tickets/{ticket_id}", headers=headers)
    assert t_check.json()["first_responded_at"] is not None

    # 4. Resolve Ticket
    resolve_res = await client.post(f"/api/v1/tickets/{ticket_id}/resolve", json={
        "resolution_code": "HOTFIX_DEPLOYED",
        "resolution_notes": "Restarted standby database replica and restored service.",
        "csat_score": 5
    }, headers=headers)
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "RESOLVED"
    assert resolve_res.json()["csat_score"] == 5

    # 5. Verify Timeline has TicketCreated and TicketResolved recorded
    timeline_res = await client.get(f"/api/v1/timeline/{cust_id}", headers=headers)
    assert timeline_res.status_code == 200
    events = timeline_res.json()
    assert any(e["channel"] == "TICKET" for e in events)


@pytest.mark.asyncio
async def test_knowledge_base_management_and_search(client: AsyncClient):
    """Test creating knowledge categories, agent call scripts, and keyword searching"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "KB Tech Solutions",
        "full_name": "Knowledge Manager",
        "email": "kb@techsolutions.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Category
    cat_res = await client.post("/api/v1/knowledge/categories", json={
        "name": "Network Troubleshooting",
        "description": "Standard operating procedures for network connectivity"
    }, headers=headers)
    assert cat_res.status_code == 201
    cat_id = cat_res.json()["id"]

    # 2. Create Article / Agent Script
    art_res = await client.post("/api/v1/knowledge/articles", json={
        "category_id": cat_id,
        "title": "SIP Softphone Audio Latency Guide",
        "content_markdown": "If caller reports audio delay, check UDP ports 10000-20000 and ensure QoS tagging.",
        "is_call_script": True
    }, headers=headers)
    assert art_res.status_code == 201
    assert art_res.json()["is_call_script"] is True

    # 3. Search Knowledge Base
    search_res = await client.get("/api/v1/knowledge/articles?query=latency", headers=headers)
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) >= 1
    assert "Latency" in results[0]["title"]
