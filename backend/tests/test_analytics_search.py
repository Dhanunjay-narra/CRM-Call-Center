import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_callcenter_and_sales_analytics(client: AsyncClient):
    """Test operational KPI calculation (AHT, ASA, Service Level, Occupancy) and Sales Funnel"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Metrics Global Analytics",
        "full_name": "Analytics Director",
        "email": "director@metricsanalytics.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch Operational Call Center KPIs
    op_res = await client.get("/api/v1/analytics/operational", headers=headers)
    assert op_res.status_code == 200
    op_data = op_res.json()
    assert "service_level_percent" in op_data
    assert "aht_seconds" in op_data
    assert "asa_seconds" in op_data
    assert "agents_online" in op_data

    # 2. Fetch Sales Analytics
    sales_res = await client.get("/api/v1/analytics/sales", headers=headers)
    assert sales_res.status_code == 200
    sales_data = sales_res.json()
    assert "open_pipeline_value" in sales_data
    assert "lead_conversion_rate" in sales_data

    # 3. Fetch Executive 360 Summary
    exec_res = await client.get("/api/v1/analytics/executive", headers=headers)
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert "average_health_score" in exec_data
    assert "sla_compliance_percent" in exec_data


@pytest.mark.asyncio
async def test_global_multi_entity_search(client: AsyncClient):
    """
    Test Global Multi-Entity Search:
    Searching 'Ravi' matches Customer, Lead, and Ticket simultaneously.
    """
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Search Engine Test Org",
        "full_name": "Search Tester",
        "email": "search@testorg.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Customer "Ravi Kumar"
    await client.post("/api/v1/customers", json={
        "name": "Ravi Kumar Enterprise",
        "email": "ravi@enterprise.com"
    }, headers=headers)

    # 2. Create Lead "Ravi Sharma"
    await client.post("/api/v1/leads", json={
        "first_name": "Ravi",
        "last_name": "Sharma",
        "company_name": "Sharma Telecom",
        "email": "sharma@telecom.com"
    }, headers=headers)

    # 3. Create Ticket referencing "Ravi"
    await client.post("/api/v1/tickets", json={
        "title": "Ravi account billing adjustment",
        "description": "Customer requested revision of invoices"
    }, headers=headers)

    # 4. Perform Global Search for "Ravi"
    search_res = await client.get("/api/v1/search?q=Ravi", headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["total_matches"] >= 3
    entity_types = [r["entity_type"] for r in search_data["results"]]
    assert "customer" in entity_types
    assert "lead" in entity_types
    assert "ticket" in entity_types
