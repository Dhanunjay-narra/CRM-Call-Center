import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_omnichannel_messaging_and_templates(client: AsyncClient):
    """Test message template creation, variable rendering, and outbound WhatsApp dispatch"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "OmniChannel Telecom",
        "full_name": "Agent Sarah",
        "email": "sarah@omnicc.com",
        "password": "Password123!"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Customer
    cust_res = await client.post("/api/v1/customers", json={
        "name": "Ravi Omnichannel Test",
        "phone_number": "+919876500000",
        "email": "ravi.omni@example.com"
    }, headers=headers)
    cust_id = cust_res.json()["id"]

    # 2. Create Reusable Message Template
    tpl_res = await client.post("/api/v1/templates", json={
        "name": "Quotation Follow-up",
        "channel": "WHATSAPP",
        "category": "Sales",
        "body_template": "Hello {{customer_name}}, your formal quotation of ${{quote_amount}} has been generated. Let us know if you need any adjustments.",
        "variables": ["customer_name", "quote_amount"]
    }, headers=headers)
    assert tpl_res.status_code == 201
    tpl_id = tpl_res.json()["id"]

    # 3. Send Outbound WhatsApp message using template
    msg_res = await client.post("/api/v1/messages/send", json={
        "customer_id": cust_id,
        "channel": "WHATSAPP",
        "recipient_identifier": "+919876500000",
        "template_id": tpl_id,
        "template_variables": {"customer_name": "Ravi", "quote_amount": "15,000"},
        "body": ""  # populated by template
    }, headers=headers)
    assert msg_res.status_code == 201
    msg_data = msg_res.json()
    assert "Hello Ravi, your formal quotation of $15,000" in msg_data["body"]
    assert msg_data["channel"] == "WHATSAPP"
    conv_id = msg_data["conversation_id"]

    # 4. Verify Message History in Conversation Thread
    thread_res = await client.get(f"/api/v1/conversations/{conv_id}/messages", headers=headers)
    assert thread_res.status_code == 200
    assert len(thread_res.json()) >= 1


@pytest.mark.asyncio
async def test_inbound_webhook_and_unified_inbox(client: AsyncClient):
    """Test inbound webhook message auto-linking to customer and appearing in Unified Inbox"""
    reg_res = await client.post("/api/v1/auth/register", json={
        "organization_name": "Unified Inbox Hub",
        "full_name": "Support Lead",
        "email": "support@unifiedhub.com",
        "password": "Password123!"
    })
    org_id = reg_res.json()["user"]["organization_id"]
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Customer
    cust_res = await client.post("/api/v1/customers", json={
        "name": "Acme Webhook Customer",
        "phone_number": "+15559998888",
        "email": "acme.cust@example.com"
    }, headers=headers)
    cust_id = cust_res.json()["id"]

    # 2. Simulate Inbound WhatsApp Webhook
    wh_res = await client.post(f"/api/v1/webhooks/WHATSAPP?org_id={org_id}", json={
        "channel": "WHATSAPP",
        "from_identifier": "+15559998888",
        "to_identifier": "+18005550000",
        "body": "Hello, I need assistance with our billing statement."
    })
    assert wh_res.status_code == 200
    wh_data = wh_res.json()
    assert wh_data["customer_id"] == cust_id
    assert wh_data["direction"] == "INBOUND"

    # 3. Verify Customer 360 Timeline has Inbound WhatsApp recorded
    tl_res = await client.get(f"/api/v1/timeline/{cust_id}", headers=headers)
    assert tl_res.status_code == 200
    events = tl_res.json()
    assert any(e["channel"] == "WHATSAPP" and "MessageReceived" in e["event_type"] for e in events)
