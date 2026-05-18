from httpx import AsyncClient

from app.models.usuario import Usuario


async def test_login_correcto(client: AsyncClient, usuario_admin: Usuario) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"]
    assert data["refresh_token"]


async def test_login_incorrecto(client: AsyncClient, usuario_admin: Usuario) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "password-malo"},
    )
    assert response.status_code == 401


async def test_refresh_token(client: AsyncClient, usuario_admin: Usuario) -> None:
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    assert login.status_code == 200
    refresh_token = login.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_endpoint_sin_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/sucursales/")
    assert response.status_code == 401
