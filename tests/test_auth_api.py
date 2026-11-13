from datetime import timedelta

from fastapi.testclient import TestClient

from finflow.api.main import create_app
from finflow.config import AuthSettings
from finflow.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def get_token(
    client: TestClient,
    username: str,
    password: str,
) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_password_is_hashed():
    password = "example-password"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_admin_can_access_report():
    with TestClient(create_app()) as client:
        token = get_token(
            client,
            "admin",
            "admin-test-password",
        )

        response = client.get(
            "/api/v1/reports/daily",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 200


def test_wrong_password_returns_401():
    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "admin",
                "password": "wrong-password",
            },
        )

        assert response.status_code == 401


def test_invalid_token_returns_401():
    with TestClient(create_app()) as client:
        response = client.get(
            "/api/v1/reports/daily",
            headers={
                "Authorization": "Bearer invalid-token",
            },
        )

        assert response.status_code == 401


def test_expired_token_returns_401():
    settings = AuthSettings.from_env()

    expired_token = create_access_token(
        username="admin",
        settings=settings,
        expires_delta=timedelta(minutes=-1),
    )

    with TestClient(create_app()) as client:
        response = client.get(
            "/api/v1/reports/daily",
            headers={
                "Authorization": f"Bearer {expired_token}",
            },
        )

        assert response.status_code == 401


def test_viewer_cannot_access_admin_report():
    with TestClient(create_app()) as client:
        token = get_token(
            client,
            "viewer",
            "viewer-test-password",
        )

        response = client.get(
            "/api/v1/reports/daily",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 403