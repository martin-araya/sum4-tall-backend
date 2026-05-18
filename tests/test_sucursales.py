from httpx import AsyncClient


async def test_get_sucursales(client: AsyncClient, token_admin: str) -> None:
    response = await client.get(
        "/api/v1/sucursales/",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data
    assert isinstance(data["items"], list)


async def test_create_sucursal_admin(client: AsyncClient, token_admin: str) -> None:
    payload = {
        "nombre": "Sucursal Centro",
        "region": "Metropolitana",
        "direccion": "Av. Principal 123",
    }
    response = await client.post(
        "/api/v1/sucursales/",
        json=payload,
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["nombre"] == "Sucursal Centro"
    assert data["region"] == "Metropolitana"
    assert data["direccion"] == "Av. Principal 123"
    assert data["activo"] is True
    assert "id" in data


async def test_create_sucursal_auditor(client: AsyncClient, token_auditor: str) -> None:
    payload = {
        "nombre": "Sucursal Norte",
        "region": "Norte",
    }
    response = await client.post(
        "/api/v1/sucursales/",
        json=payload,
        headers={"Authorization": f"Bearer {token_auditor}"},
    )
    assert response.status_code == 403
