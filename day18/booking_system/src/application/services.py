

from .dto import NotificationRequestDTO
from ..notification import send_email_notification, send_sms_notification

class NotificationService:
    """
    Сервисный слой для управления уведомлениями.
    Использует низкоуровневые функции из src.notification.
    """
    def __init__(self):
        # Зависимости можно подменять для тестов
        self.send_email = send_email_notification
        self.send_sms = send_sms_notification

    def send_notification(self, dto: NotificationRequestDTO) -> bool:
        """
        Диспетчер уведомлений.
        Принимает DTO (объект данных) и решает, какую функцию вызвать.
        """
        if dto.notification_type == "email":
            return self.send_email(dto.recipient, dto.subject or "", dto.body or "")
        
        elif dto.notification_type == "sms":
            return self.send_sms(dto.recipient, dto.body or "")
        
        else:
            # Для push-уведомлений или неизвестных типов
            return False