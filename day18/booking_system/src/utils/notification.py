import logging
import requests
import smtplib
from typing import Optional

from .utils.logger import logger

def send_email_notification(
    to_email: str, subject: str, body: str, from_email: str = "noreply@hotel.com"
) -> bool:
    """
    Отправляет email-уведомление.
    Возвращает True в случае успеха, иначе False.
    """
    if not to_email or not subject or not body:
        logger.error("Пустые параметры для отправки email.")
        return False

    message = f"Subject: {subject}\n\n{body}"
    try:
        with smtplib.SMTP("localhost") as server:
            server.sendmail(from_email, to_email, message)
        logger.info(f"Email успешно отправлен на {to_email}")
        return True
    except smtplib.SMTPException as e:
        logger.error(f"Ошибка отправки email: {e}")
        return False

def send_sms_notification(to_phone: str, message: str) -> bool:
    """
    Отправляет SMS через внешний HTTP-шлюз.
    Возвращает True в случае успеха, иначе False.
    """
    if not to_phone or not message:
        logger.error("Пустые параметры для отправки SMS.")
        return False

    url = "https://api.sms-gateway.com/send"
    payload = {"to": to_phone, "text": message}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"SMS успешно отправлен на {to_phone}")
            return True
        else:
            logger.error(f"Ошибка отправки SMS. Код ответа шлюза: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        logger.error(f"Таймаут при отправке SMS на {to_phone}")
        return False