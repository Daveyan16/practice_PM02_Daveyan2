import pytest


@pytest.mark.skip(reason="Этот тест требует подключения к реальному внешнему API")
def test_real_sms_gateway():
    from src.notification import send_sms_notification

    # Этот тест будет пропущен при запуске pytest
    result = send_sms_notification("+79998887766", "Интеграционный тест")
    
    assert result is True 