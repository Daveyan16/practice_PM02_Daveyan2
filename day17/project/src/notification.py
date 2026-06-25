class NotificationError(Exception):
    """Исключение для ошибок отправки уведомлений"""
    pass


def send_email(client, to, subject, body):
    """
    Отправка Email
    """
    try:
        return client.send(to, subject, body)
    except Exception as e:
        raise NotificationError(
            f"Email sending failed: {e}"
        )


def send_sms(client, phone, text):
    """
    Отправка SMS
    """
    try:
        return client.send(
            phone,
            text,
            timeout=5
        )
    except TimeoutError:
        return False


def send_push(client, user_id, text):
    """
    Отправка Push-уведомления
    """
    result = client.push(user_id, text)

    return result.get(
        "success",
        False
    )