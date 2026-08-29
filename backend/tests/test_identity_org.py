import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tenant_registration_and_login(client: AsyncClient):
    """Test full tenant registration, JWT token generation, and login flow"""
    reg_data = {
        "organization_name": "Acme Telecom Solutions",
        "full_name": "John Doe",
        "email": "admin@acmetelecom.com",
        "password": "SecurePassword123!",
        "phone_number": "+1234567890",
        "time_zone": "America/New_York"
    }
    
    # 1. Register Tenant
    res = await client.post("/api/v1/auth/register", json=reg_data)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "admin@acmetelecom.com"
    assert data["user"]["role"] == "ORGANIZATION_ADMIN"
    org_id = data["user"]["organization_id"]
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]

    # 2. Login with credentials
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "admin@acmetelecom.com",
        "password": "SecurePassword123!"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

    # 3. Refresh token
    refresh_res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()

    # 4. Request and verify OTP
    otp_req = await client.post("/api/v1/auth/otp/request", json={"email": "admin@acmetelecom.com"})
    assert otp_req.status_code == 200
    otp_code = otp_req.json()["debug_code"]
    
    otp_verify = await client.post("/api/v1/auth/otp/verify", json={
        "email": "admin@acmetelecom.com",
        "code": otp_code
    })
    assert otp_verify.status_code == 200


@pytest.mark.asyncio
async def test_departments_teams_and_users(client: AsyncClient):
    """Test creating departments, teams, and managing user roles"""
    reg_data = {
        "organization_name": "CloudSphere Tech",
        "full_name": "Sarah Connor",
        "email": "sarah@cloudsphere.io",
        "password": "Password789!",
        "time_zone": "UTC"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_data)
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List default departments (Sales & Support created automatically)
    dept_res = await client.get("/api/v1/departments", headers=headers)
    assert dept_res.status_code == 200
    depts = dept_res.json()
    assert len(depts) >= 2

    # 2. Create custom Department
    new_dept_res = await client.post("/api/v1/departments", json={
        "name": "Quality Assurance & Compliance",
        "code": "QA"
    }, headers=headers)
    assert new_dept_res.status_code == 201
    qa_dept = new_dept_res.json()
    assert qa_dept["code"] == "QA"

    # 3. Create Team under QA
    team_res = await client.post("/api/v1/teams", json={
        "name": "Call Auditing Team",
        "department_id": qa_dept["id"]
    }, headers=headers)
    assert team_res.status_code == 201
    assert team_res.json()["name"] == "Call Auditing Team"

    # 4. Create Agent User
    user_res = await client.post("/api/v1/users", json={
        "email": "agent.smith@cloudsphere.io",
        "password": "AgentPassword456!",
        "full_name": "Agent Smith",
        "role": "AGENT",
        "department_id": depts[0]["id"]
    }, headers=headers)
    assert user_res.status_code == 201
    agent_id = user_res.json()["id"]

    # 5. List users
    users_list = await client.get("/api/v1/users", headers=headers)
    assert users_list.status_code == 200
    assert len(users_list.json()) >= 2
