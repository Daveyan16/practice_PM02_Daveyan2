"""
Тесты нестабильности и времени
"""

import pytest
import time
from datetime import datetime, timedelta
import random
from fake_validator import FakeValidator  # <-- ЭТО ВАЖНО!


def test_time_boundary_alcohol():
    """Тест: границы времени для алкоголя"""
    validator = FakeValidator()
    now = datetime.now()
    
    def create_order(hour, minute):
        order_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if order_time > now:
            order_time = order_time - timedelta(days=1)
        return {
            "order_id": "ORD-TIME-001",
            "user": {
                "user_id": "USR-001",
                "created_at": (now - timedelta(days=10)).isoformat(),
                "age_verified": True,
                "email_last_changed": None,
                "country": "US"
            },
            "items": [
                {"product_id": "P-001", "name": "Test Alcohol", "category": "Alcohol", "price": 100.0, "quantity": 1}
            ],
            "delivery_country": "US",
            "order_time": order_time.isoformat(),
            "payment_method": {"type": "credit_card", "wallet_country": "US"}
        }
    
    test_cases = [
        (7, 59, False),
        (8, 0, True),
        (22, 59, True),
        (23, 0, True),
        (23, 1, False),
    ]
    
    for hour, minute, expected_valid in test_cases:
        order = create_order(hour, minute)
        result = validator.validate_order(order)
        assert result["valid"] == expected_valid, f"Hour {hour}:{minute} failed"


def test_email_time_boundary():
    """Тест: границы времени для смены email"""
    validator = FakeValidator()
    now = datetime.now()
    
    order = {
        "order_id": "ORD-EMAIL-001",
        "user": {
            "user_id": "USR-001",
            "created_at": (now - timedelta(days=10)).isoformat(),
            "age_verified": False,
            "email_last_changed": None,
            "country": "US"
        },
        "items": [
            {"product_id": "P-001", "name": "Test Item", "category": "Food", "price": 500.0, "quantity": 1}
        ],
        "delivery_country": "US",
        "order_time": now.isoformat(),
        "payment_method": {"type": "credit_card", "wallet_country": "US"}
    }
    
    order["user"]["email_last_changed"] = (now - timedelta(minutes=59)).isoformat()
    result = validator.validate_order(order)
    assert result["risk_score"] == 0.2
    
    order["user"]["email_last_changed"] = (now - timedelta(minutes=61)).isoformat()
    result = validator.validate_order(order)
    assert result["risk_score"] == 0.0


def test_duplicate_orders():
    """Тест: устойчивость к дубликатам заказов"""
    validator = FakeValidator()
    order = {
        "order_id": "ORD-DUP-001",
        "user": {
            "user_id": "USR-001",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "age_verified": False,
            "email_last_changed": None,
            "country": "US"
        },
        "items": [
            {"product_id": "P-001", "name": "Test Item", "category": "Food", "price": 500.0, "quantity": 1}
        ],
        "delivery_country": "US",
        "order_time": datetime.now().isoformat(),
        "payment_method": {"type": "credit_card", "wallet_country": "US"}
    }
    
    result1 = validator.validate_order(order)
    result2 = validator.validate_order(order)
    assert result1["valid"] == result2["valid"]


def test_random_orders_stability():
    """Тест: 50 случайных заказов проверяют диапазоны значений"""
    validator = FakeValidator()
    
    for i in range(50):
        now = datetime.now()
        order = {
            "order_id": f"ORD-RND-{i:03d}",
            "user": {
                "user_id": f"USR-RND-{i:03d}",
                "created_at": (now - timedelta(days=random.randint(1, 365))).isoformat(),
                "age_verified": random.choice([True, False]),
                "email_last_changed": random.choice([
                    None,
                    (now - timedelta(minutes=random.randint(1, 120))).isoformat()
                ]),
                "country": random.choice(["US", "GB", "DE", "FR", "JP"])
            },
            "items": [
                {
                    "product_id": f"P-RND-{i:03d}-001",
                    "name": f"Random Item",
                    "category": random.choice(["Food", "Electronics", "Alcohol", "Clothing", "Books"]),
                    "price": random.uniform(1, 50000),
                    "quantity": random.randint(1, 10)
                }
            ],
            "delivery_country": random.choice(["US", "GB", "DE", "FR", "JP"]),
            "order_time": now.isoformat(),
            "payment_method": {
                "type": random.choice(["credit_card", "debit_card", "paypal", "crypto", "wallet"]),
                "wallet_country": random.choice([None, "US", "GB", "DE", "FR", "JP"])
            }
        }
        
        result = validator.validate_order(order)
        assert isinstance(result["valid"], bool)
        assert 0.0 <= result["risk_score"] <= 1.0


def test_validator_performance():
    """Тест: проверка производительности"""
    validator = FakeValidator()
    order = {
        "order_id": "ORD-PERF-001",
        "user": {
            "user_id": "USR-001",
            "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
            "age_verified": False,
            "email_last_changed": None,
            "country": "US"
        },
        "items": [
            {"product_id": "P-001", "name": "Test Item", "category": "Food", "price": 500.0, "quantity": 1}
        ],
        "delivery_country": "US",
        "order_time": datetime.now().isoformat(),
        "payment_method": {"type": "credit_card", "wallet_country": "US"}
    }
    
    start_time = time.time()
    for _ in range(100):
        validator.validate_order(order)
    end_time = time.time()
    
    assert end_time - start_time < 2.0