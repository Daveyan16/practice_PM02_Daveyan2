import pytest
import smtplib   # Для создания исключения SMTPException
import requests  # Для создания исключения Timeout

from src.application.dto import NotificationRequestDTO


@pytest.fixture
def notification_service():
    """Фикстура создает экземпляр NotificationService для тестов."""
    from src.application.services import NotificationService
    return NotificationService()


# --- Тесты для Email ---

def test_send_email_success(mocker):
    """
    Проверяет успешную отправку email.
    """
    mocker.patch('smtplib.SMTP') # Патчим класс, чтобы избежать реального подключения к серверу
    from src.notification import send_email_notification

    result = send_email_notification("user@example.com", "Subject", "Body")
    
    assert result is True


def test_send_email_smtp_error(mocker):
    """
    Проверяет обработку ошибки SMTP внутри функции.
    Покрывает блок try/except для почты.
    """
    from src.notification import send_email_notification

    # Настраиваем мок: объект SMTP выбрасывает исключение при вызове sendmail
    mock_smtp_instance = mocker.Mock()
    mock_smtp_instance.sendmail.side_effect = smtplib.SMTPException("Server Error")

    mock_smtp_class = mocker.patch('smtplib.SMTP')
    mock_smtp_class.return_value.__enter__.return_value = mock_smtp_instance

    result = send_email_notification(
        to_email="user@example.com",
        subject="Test",
        body="Body"
    )

    assert result is False


# --- Тесты для SMS ---

def test_send_sms_success(mocker):
    """
    Проверяет успешную отправку SMS.
    """
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.status_code = 200

    from src.notification import send_sms_notification

    result = send_sms_notification("+79001112233", "Hello!")
    assert result is True


def test_send_sms_timeout(mocker):
    """
    Проверяет обработку сетевой ошибки (Timeout) внутри функции.
    Покрывает блок try/except для SMS.
    """
    from src.notification import send_sms_notification

    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = requests.exceptions.Timeout()

    result = send_sms_notification("+79001112233", "Hello!")
    assert result is False


# --- Новые тесты для повышения Coverage (проверка граничных условий) ---

def test_send_email_empty_fields():
    """
    Проверяет ветку 'if not all([to_email, subject, body]): return False'
    в самом начале функции send_email_notification.
    """
    from src.notification import send_email_notification

    # Act & Assert: Передаем пустую строку в поле body
    result = send_email_notification(
        to_email="user@example.com",
        subject="Subject",
        body="" # Пустое тело письма
    )
    assert result is False


def test_send_sms_empty_message():
    """
    Проверяет ветку 'if not all([to_phone, message]): return False'
    в самом начале функции send_sms_notification.
    """
    from src.notification import send_sms_notification

    # Act & Assert: Передаем пустую строку в поле message
    result = send_sms_notification(
        to_phone="+79001112233",
        message="" # Пустое сообщение
    )
    assert result is False


# --- Тесты для Сервисного Слоя (Бизнес-логика) ---

def test_notification_service_dispatch_email(notification_service, mocker):
    """
    Тест проверяет, что сервис вызывает правильную функцию для EMAIL.
    """
    mock_send_email = mocker.patch.object(notification_service, 'send_email', return_value=True)
    mock_send_sms = mocker.patch.object(notification_service, 'send_sms')
    
    dto = NotificationRequestDTO(
        user_id=1,
        notification_type="email",
        recipient="user@example.com",
        subject="Hi",
        body="Body"
    )

    result = notification_service.send_notification(dto)

    assert result is True
    mock_send_email.assert_called_once() 
    mock_send_sms.assert_not_called()   


def test_notification_service_dispatch_sms(notification_service, mocker):
    """
    Тест проверяет, что сервис вызывает правильную функцию для SMS.
    """
    mock_send_email = mocker.patch.object(notification_service, 'send_email')
    mock_send_sms = mocker.patch.object(notification_service, 'send_sms', return_value=True)

    dto = NotificationRequestDTO(
        user_id=1,
        notification_type="sms",
        recipient="+79001112233",
        body="Message"
    )

    result = notification_service.send_notification(dto)

    assert result is True
    mock_send_sms.assert_called_once()
    mock_send_email.assert_not_called()