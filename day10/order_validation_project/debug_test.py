from fake_validator import FakeValidator
from datetime import datetime, timedelta

validator = FakeValidator()

# Фиксируем текущее время
now = datetime.now()

# Функция для создания заказа с временем в прошлом
def create_test_order(hour, minute, days_ago=10):
    # Создаем время заказа на сегодня, но если оно в будущем - отнимаем день
    order_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if order_time > now:
        order_time = order_time - timedelta(days=1)  # Если в будущем - переносим на вчера
    
    return {
        "order_id": "ORD-TEST",
        "user": {
            "user_id": "USR-001",
            "created_at": (now - timedelta(days=days_ago)).isoformat(),
            "age_verified": True,
            "email_last_changed": None,
            "country": "US"
        },
        "items": [
            {"product_id": "P-001", "name": "Wine", "category": "Alcohol", "price": 100, "quantity": 1}
        ],
        "delivery_country": "US",
        "order_time": order_time.isoformat(),
        "payment_method": {"type": "credit_card", "wallet_country": "US"}
    }

# Тест 1: 22:59
order = create_test_order(22, 59)
result = validator.validate_order(order)
print(f"22:59 result: {result}")

# Тест 2: 23:00
order = create_test_order(23, 0)
result = validator.validate_order(order)
print(f"23:00 result: {result}")

# Тест 3: Новый пользователь 7 дней, сумма 15000.01
order = create_test_order(14, 0, days_ago=7)
order["items"][0]["price"] = 15000.01
result = validator.validate_order(order)
print(f"7 days, 15000.01 result: {result}")

# Тест 4: 07:59 (должно быть невалидно)
order = create_test_order(7, 59)
result = validator.validate_order(order)
print(f"07:59 result: {result}")