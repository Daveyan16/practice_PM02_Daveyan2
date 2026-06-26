from dataclasses import dataclass
from typing import Optional 

@dataclass
class NotificationRequestDTO:
    user_id: int
    notification_type: str  # 'email', 'sms'
    recipient: str         # Номер телефона или email
    subject: Optional[str] = None  # Для email/push
    body: Optional[str] = None     # Текст сообщения