# tests/test_orders.py
import pytest


@pytest.mark.asyncio
async def test_create_order(client):
    payload = {
        "customer": {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "123456",
            "notes": None,
        },
        "film_type": "35mm",
        "needs_print": True,
        "notes": "hello",
    }

    res = await client.post("/api/orders/", json=payload)

    assert res.status_code == 200
    data = res.json()

    assert "order_code" in data
    assert data["customer"]["email"] == "test@example.com"
