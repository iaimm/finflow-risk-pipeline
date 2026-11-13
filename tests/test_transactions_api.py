import pytest
from fastapi.testclient import TestClient

from finflow.api.main import create_app


@pytest.fixture
def client():
    with TestClient(create_app()) as test_client:
        yield test_client


def transaction_payload() -> dict:
    return {
        "transaction_id": "T-API-TEST-001",
        "account_id": "A000001",
        "amount": "99.90",
        "currency": "CNY",
        "transaction_type": "DEBIT",
    }


def test_create_and_get_transaction(client: TestClient):
    response = client.post(
        "/api/v1/transactions",
        json=transaction_payload(),
    )

    assert response.status_code == 201
    assert response.json()["transaction_id"] == "T-API-TEST-001"

    response = client.get(
        "/api/v1/transactions/T-API-TEST-001"
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "99.90"


def test_list_transactions_with_pagination(client: TestClient):
    response = client.get(
        "/api/v1/transactions",
        params={"limit": 5, "offset": 0},
    )

    assert response.status_code == 200

    body = response.json()
    assert len(body["items"]) == 5
    assert body["total"] == 100
    assert body["limit"] == 5
    assert body["offset"] == 0


def test_invalid_amount_returns_422(client: TestClient):
    payload = transaction_payload()
    payload["amount"] = "0"

    response = client.post(
        "/api/v1/transactions",
        json=payload,
    )

    assert response.status_code == 422


def test_currency_mismatch_returns_400(client: TestClient):
    payload = transaction_payload()
    payload["currency"] = "USD"

    response = client.post(
        "/api/v1/transactions",
        json=payload,
    )

    assert response.status_code == 400


def test_unknown_transaction_returns_404(client: TestClient):
    response = client.get(
        "/api/v1/transactions/T-NOT-EXIST"
    )

    assert response.status_code == 404


def test_duplicate_transaction_returns_409(client: TestClient):
    response = client.post(
        "/api/v1/transactions",
        json=transaction_payload(),
    )
    assert response.status_code == 201

    response = client.post(
        "/api/v1/transactions",
        json=transaction_payload(),
    )
    assert response.status_code == 409