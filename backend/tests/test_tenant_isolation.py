@pytest.mark.asyncio
async def test_cross_tenant_access(client):
    token = await login_as_doctor_a(client)

    response = await client.get(
        "/some-tenant-resource",
        headers={"Authorization": f"Bearer {token}"},
        params={"tenant_id": "other-tenant"}
    )

    assert response.status_code == 403
