# СПЕЦИФИКАЦИЯ ВАЛИДАЦИИ ЗАКАЗОВ

## ЧТО ПРИХОДИТ НА ВХОД (JSON)

{
  "order_id": "ORD-001",
  "user": {
    "user_id": "USR-001",
    "created_at": "2025-01-01T10:00:00",
    "age_verified": false,
    "email_last_changed": null,
    "country": "US"
  },
  "items": [
    {
      "product_id": "P-001",
      "name": "Laptop",
      "category": "Electronics",
      "price": 999.99,
      "quantity": 1
    }
  ],
  "delivery_country": "US",
  "order_time": "2025-01-15T14:30:00",
  "payment_method": {
    "type": "credit_card",
    "wallet_country": "US"
  }
}

## ЧТО ВОЗВРАЩАЕТ ФУНКЦИЯ

{
  "valid": true,
  "reasons": [],
  "risk_score": 0.0
}

## ПРАВИЛА ПРОВЕРКИ

1. Сумма заказа должна быть больше 0 и меньше 1,000,000
   Ошибка: "Order total must be between 0 and 1,000,000"

2. Если пользователь зарегистрирован меньше 7 дней назад, сумма не больше 15,000
   Ошибка: "New users cannot order more than 15,000"

3. В заказе не больше 50 товаров
   Ошибка: "Order cannot have more than 50 items"

4. Если есть алкоголь (категория "Alcohol"):
   - Должен быть age_verified = true
   - Время с 08:00 до 23:00
   Ошибки: 
   - "Age verification required for alcohol"
   - "Alcohol orders only allowed between 08:00 and 23:00"

5. Риск-скор (число от 0 до 1):
   - Если сумма > 100,000 → risk_score = 0.9
   - Если email меняли за последний час → risk_score + 0.2
   - Если страна доставки != страна кошелька → risk_score + 0.3
   - Итог не больше 1

## ПРИМЕРЫ

 ВАЛИДНЫЙ ЗАКАЗ:
Сумма 500, старый пользователь, 1 товар, без алкоголя
Результат: valid=True, risk_score=0.0

 НЕВАЛИДНЫЙ ЗАКАЗ:
Сумма -100 (отрицательная)
Результат: valid=False, причина "Order total must be between 0 and 1,000,000"

 НЕВАЛИДНЫЙ ЗАКАЗ:
Новый пользователь (5 дней), сумма 20,000
Результат: valid=False, причина "New users cannot order more than 15,000"