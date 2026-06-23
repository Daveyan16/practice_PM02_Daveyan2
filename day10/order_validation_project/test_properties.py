"""
Property-based тесты для validate_order
"""

import pytest
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from fake_validator import create_validator


@pytest.fixture
def prop_validator():
    return create_validator()


def test_risk_score_always_in_range(prop_validator):
    """Свойство: risk_score всегда в диапазоне [0, 1]"""
    @given(st.floats(min_value=0.01, max_value=999999.99))
    def test(amount):
        order = {
            "order_id": "ORD-001",
            "user": {
                "user_id": "USR-001",
                "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
                "age_verified": False,
                "email_last_changed": None,
                "country": "US"
            },
            "items": [
                {"product_id": "P-001", "name": "Test", "category": "Food", "price": amount, "quantity": 1}
            ],
            "delivery_country": "US",
            "order_time": datetime.now().isoformat(),
            "payment_method": {"type": "credit_card", "wallet_country": "US"}
        }
        result = prop_validator.validate_order(order)
        assert 0.0 <= result["risk_score"] <= 1.0
    
    test()


def test_valid_orders_have_no_reasons(prop_validator):
    """Свойство: валидные заказы не имеют причин ошибок"""
    @given(st.floats(min_value=0.01, max_value=999999.99))
    def test(amount):
        order = {
            "order_id": "ORD-001",
            "user": {
                "user_id": "USR-001",
                "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
                "age_verified": False,
                "email_last_changed": None,
                "country": "US"
            },
            "items": [
                {"product_id": "P-001", "name": "Test", "category": "Food", "price": amount, "quantity": 1}
            ],
            "delivery_country": "US",
            "order_time": datetime.now().isoformat(),
            "payment_method": {"type": "credit_card", "wallet_country": "US"}
        }
        result = prop_validator.validate_order(order)
        if result["valid"]:
            assert len(result["reasons"]) == 0
    
    test()


def test_invalid_order_has_reasons(prop_validator):
    """Свойство: невалидный заказ всегда имеет причины"""
    @given(st.integers(min_value=-1000, max_value=1000))
    def test(amount):
        if amount <= 0 or amount >= 1000000:
            order = {
                "order_id": "ORD-001",
                "user": {
                    "user_id": "USR-001",
                    "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
                    "age_verified": False,
                    "email_last_changed": None,
                    "country": "US"
                },
                "items": [
                    {"product_id": "P-001", "name": "Test", "category": "Food", "price": float(amount) if amount > 0 else 0.01, "quantity": 1}
                ],
                "delivery_country": "US",
                "order_time": datetime.now().isoformat(),
                "payment_method": {"type": "credit_card", "wallet_country": "US"}
            }
            result = prop_validator.validate_order(order)
            if not result["valid"]:
                assert len(result["reasons"]) > 0
    
    test()