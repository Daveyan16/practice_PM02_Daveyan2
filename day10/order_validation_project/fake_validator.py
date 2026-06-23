from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import random
import time
from pydantic import BaseModel, Field, field_validator, ValidationError


class OrderItem(BaseModel):
    product_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., pattern="^(Food|Electronics|Alcohol|Clothing|Books)$")
    price: float = Field(..., gt=0, le=1_000_000)
    quantity: int = Field(..., gt=0, le=1000)


class PaymentMethod(BaseModel):
    type: str = Field(..., pattern="^(credit_card|debit_card|paypal|crypto|wallet)$")
    wallet_country: Optional[str] = Field(None, min_length=2, max_length=2)


class User(BaseModel):
    user_id: str = Field(..., min_length=1)
    created_at: datetime
    age_verified: bool = False
    email_last_changed: Optional[datetime] = None
    country: str = Field(..., min_length=2, max_length=2)


class Order(BaseModel):
    order_id: str = Field(..., min_length=1)
    user: User
    items: list[OrderItem] = Field(..., min_length=1, max_length=50)
    delivery_country: str = Field(..., min_length=2, max_length=2)
    order_time: datetime
    payment_method: PaymentMethod
    
    @field_validator('order_time')
    def validate_order_time(cls, v):
        if v > datetime.now() + timedelta(minutes=5):
            raise ValueError("Order time cannot be in future")
        return v
    
    def total_amount(self) -> float:
        return sum(item.price * item.quantity for item in self.items)


class FakeValidator:
    def __init__(self, chaos_mode: bool = False, delay_seconds: float = 0.0):
        self.chaos_mode = chaos_mode
        self.delay_seconds = delay_seconds
        
    def validate_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)
        
        if self.chaos_mode and random.random() < 0.05:
            return {
                "valid": random.choice([True, False]),
                "reasons": [],
                "risk_score": random.uniform(0, 1)
            }
        
        reasons = []
        now = datetime.now()
        
        # Сначала проверяем количество позиций (ДО Pydantic валидации)
        if "items" in order and len(order["items"]) > 50:
            reasons.append("Order cannot have more than 50 items")
            # Не возвращаем сразу, чтобы собрать все ошибки
        
        try:
            validated_order = Order(**order)
        except ValidationError as e:
            # Добавляем ошибки валидации
            for err in e.errors():
                # Пропускаем ошибку о количестве позиций, если мы уже добавили её
                if "items" in str(err) and "max_length" in str(err):
                    if "Order cannot have more than 50 items" not in reasons:
                        reasons.append("Order cannot have more than 50 items")
                elif "price" in str(err) or "total" in str(err):
                    if "Order total must be between 0 and 1,000,000" not in reasons:
                        reasons.append("Order total must be between 0 and 1,000,000")
                else:
                    reasons.append(str(err.get("msg", "Validation error")))
            
            # Если есть причины, возвращаем невалидный результат
            if reasons:
                return {"valid": False, "reasons": reasons, "risk_score": 0.0}
            return {"valid": False, "reasons": ["Validation error"], "risk_score": 0.0}
        
        total = validated_order.total_amount()
        
        # ПРАВИЛО 1: Сумма заказа
        if total <= 0 or total >= 1_000_000:
            reasons.append("Order total must be between 0 and 1,000,000")
        
        # ПРАВИЛО 2: Новые пользователи
        user_age = now - validated_order.user.created_at
        if user_age.days < 7:
            if total > 15_000:
                reasons.append("New users cannot order more than 15,000")
        
        # ПРАВИЛО 3: Количество позиций (дополнительная проверка)
        if len(validated_order.items) > 50:
            if "Order cannot have more than 50 items" not in reasons:
                reasons.append("Order cannot have more than 50 items")
        
        # ПРАВИЛО 4: Алкоголь
        has_alcohol = any(item.category == "Alcohol" for item in validated_order.items)
        if has_alcohol:
            if not validated_order.user.age_verified:
                reasons.append("Age verification required for alcohol")
            
            hour = validated_order.order_time.hour
            minute = validated_order.order_time.minute
            
            if hour < 8 or hour > 23:
                reasons.append("Alcohol orders only allowed between 08:00 and 23:00")
            elif hour == 23 and minute > 0:
                reasons.append("Alcohol orders only allowed between 08:00 and 23:00")
        
        # ПРАВИЛО 5: Риск-скоринг
        risk_score = 0.0
        
        if total > 100_000:
            risk_score = 0.9
        
        if validated_order.user.email_last_changed is not None:
            time_since_email_change = now - validated_order.user.email_last_changed
            if time_since_email_change.total_seconds() < 3600:
                risk_score = min(1.0, risk_score + 0.2)
        
        if (validated_order.payment_method.wallet_country is not None and 
            validated_order.delivery_country != validated_order.payment_method.wallet_country):
            risk_score = min(1.0, risk_score + 0.3)
        
        return {
            "valid": len(reasons) == 0,
            "reasons": reasons,
            "risk_score": risk_score
        }


def create_validator(chaos_mode: bool = False, delay_seconds: float = 0.0) -> FakeValidator:
    return FakeValidator(chaos_mode=chaos_mode, delay_seconds=delay_seconds)