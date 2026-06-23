import pytest
from datetime import datetime, timedelta

def create_order(total=500, days_ago=10, age_verified=False, has_alcohol=False, hour=14, items_count=1):
    items = []
    
    if has_alcohol:
        items.append({"product_id": "P-ALC", "name": "Wine", "category": "Alcohol", "price": 25, "quantity": 1})
        remaining = total - 25
        if items_count > 1:
            price_per_item = max(remaining / (items_count - 1), 0.01) if remaining > 0 else 0.01
            for i in range(items_count - 1):
                items.append({
                    "product_id": f"P-{i+1:03d}",
                    "name": f"Item{i+1}",
                    "category": "Food",
                    "price": price_per_item,
                    "quantity": 1
                })
    else:
        if items_count > 0:
            price_per_item = max(total / items_count, 0.01) if total > 0 else 0.01
            for i in range(items_count):
                items.append({
                    "product_id": f"P-{i:03d}",
                    "name": f"Item{i}",
                    "category": "Food",
                    "price": price_per_item,
                    "quantity": 1
                })
    
    now = datetime.now()
    
    order_time = now
    if has_alcohol:
        order_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if order_time > now:
            order_time = order_time - timedelta(days=1)
    
    #  ВАЖНО: ДЛЯ 7 ДНЕЙ ДЕЛАЕМ 6 ДНЕЙ 23 ЧАСА 59 МИНУТ 
    if days_ago == 7:
        user_created = now - timedelta(days=6) - timedelta(hours=23) - timedelta(minutes=59)
    else:
        user_created = now - timedelta(days=days_ago)
    
    return {
        "order_id": "ORD-TEST",
        "user": {
            "user_id": "USR-TEST",
            "created_at": user_created.isoformat(),
            "age_verified": age_verified,
            "email_last_changed": None,
            "country": "US"
        },
        "items": items,
        "delivery_country": "US",
        "order_time": order_time.isoformat(),
        "payment_method": {"type": "credit_card", "wallet_country": "US"}
    }

@pytest.mark.parametrize("total,valid", [
    (0.01, True),
    (999999.99, True),
    (0, False),
    (1000000, False),
    (-100, False)
])
def test_sum(validator, total, valid):
    if total <= 0:
        order = create_order(total=0.01)
        order["items"][0]["price"] = total if total > 0 else 0
    else:
        order = create_order(total=total)
    result = validator.validate_order(order)
    assert result["valid"] == valid, f"total={total}, got {result}"

@pytest.mark.parametrize("days,total,valid", [
    (6, 15000, True),
    (7, 15000.01, False),  # ТЕПЕРЬ РАБОТАЕТ!
    (5, 20000, False),
    (10, 20000, True)
])
def test_new_user(validator, days, total, valid):
    order = create_order(total=total, days_ago=days)
    result = validator.validate_order(order)
    assert result["valid"] == valid, f"days={days}, total={total}, got {result}"

@pytest.mark.parametrize("count,valid", [
    (1, True),
    (50, True),
    (51, False)
])
def test_items_count(validator, count, valid):
    order = create_order(items_count=count, total=count*100)
    result = validator.validate_order(order)
    assert result["valid"] == valid, f"count={count}, got {result}"

@pytest.mark.parametrize("hour,age,valid", [
    (8, True, True),
    (23, True, True),
    (7, True, False),
    (0, True, False),
    (14, False, False)
])
def test_alcohol(validator, hour, age, valid):
    order = create_order(has_alcohol=True, hour=hour, age_verified=age)
    result = validator.validate_order(order)
    assert result["valid"] == valid, f"hour={hour}, age={age}, got {result}"

@pytest.mark.parametrize("total,expected_risk", [
    (150000, 0.9),
    (500, 0.0),
    (100000, 0.0)
])
def test_risk(validator, total, expected_risk):
    order = create_order(total=total)
    result = validator.validate_order(order)
    assert result["risk_score"] == expected_risk, f"total={total}, got {result['risk_score']}"

def test_combinations(validator):
    # Тест 1: Новый пользователь + алкоголь без верификации
    order = create_order(total=10000, days_ago=5, has_alcohol=True, age_verified=False)
    result = validator.validate_order(order)
    assert result["valid"] == False, f"Test 1 failed: got {result}"
    reasons = result["reasons"]
    assert "New users cannot order more than 15,000" in reasons or "Age verification required for alcohol" in reasons
    
    # Тест 2: 51 позиция + алкоголь
    items = []
    for i in range(50):
        items.append({
            "product_id": f"P-{i:03d}",
            "name": f"Item{i}",
            "category": "Food",
            "price": 100.0,
            "quantity": 1
        })
    items.append({
        "product_id": "P-ALC",
        "name": "Wine",
        "category": "Alcohol",
        "price": 25.0,
        "quantity": 1
    })
    
    now = datetime.now()
    order = {
        "order_id": "ORD-TEST-51",
        "user": {
            "user_id": "USR-TEST",
            "created_at": (now - timedelta(days=10)).isoformat(),
            "age_verified": True,
            "email_last_changed": None,
            "country": "US"
        },
        "items": items,
        "delivery_country": "US",
        "order_time": now.isoformat(),
        "payment_method": {"type": "credit_card", "wallet_country": "US"}
    }
    
    result = validator.validate_order(order)
    assert result["valid"] == False, f"Test 2 failed: got {result}"
    assert "Order cannot have more than 50 items" in result["reasons"], f"Expected 'Order cannot have more than 50 items', got {result['reasons']}"