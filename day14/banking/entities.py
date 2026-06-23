from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Account:
    """Сущность банковского счета."""
    id: int
    number: str
    owner_name: str
    balance: float
    is_active: bool = True

@dataclass
class Transaction:
    """Сущность финансовой транзакции."""
    id: int
    account_id: int
    amount: float  # Положительное значение — приход, отрицательное — расход
    transaction_type: str  #'deposit', 'withdrawal', 'transfer'
    created_at: datetime
    description: Optional[str] = None