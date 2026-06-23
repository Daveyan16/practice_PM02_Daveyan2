"""
Фикстуры для тестирования валидатора заказов
"""

import pytest
from datetime import datetime, timedelta
from fake_validator import create_validator


@pytest.fixture
def validator():
    """Создает обычный валидатор"""
    return create_validator()


@pytest.fixture
def chaos_validator():
    """Создает валидатор с режимом хаоса"""
    return create_validator(chaos_mode=True)


@pytest.fixture
def slow_validator():
    """Создает медленный валидатор"""
    return create_validator(delay_seconds=0.1)


@pytest.fixture
def base_order():
    """Базовый шаблон заказа"""
    return {
        "order_id": "ORD-TEST-001",
        "user": {
            "user_id": "USR-TEST-001",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "age_verified": False,
            "email_last_changed": None,
            "country": "US"
        },
        "items": [
            {
                "product_id": "P-001",
                "name": "Test Item",
                "category": "Food",
                "price": 500.0,
                "quantity": 1
            }
        ],
        "delivery_country": "US",
        "order_time": datetime.now().isoformat(),
        "payment_method": {
            "type": "credit_card",
            "wallet_country": "US"
        }
    }