import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.append(
    str(Path(__file__).resolve().parent.parent / "src")
)

from notification import (
    NotificationError,
    send_email,
    send_sms,
    send_push
)


def test_send_email_success():
    client = Mock()
    client.send.return_value = True

    assert send_email(
        client,
        "user@mail.com",
        "Test",
        "Message"
    ) is True


def test_send_email_error():
    client = Mock()
    client.send.side_effect = Exception("SMTP Error")

    with pytest.raises(NotificationError):
        send_email(
            client,
            "user@mail.com",
            "Test",
            "Message"
        )


def test_send_sms_success():
    client = Mock()
    client.send.return_value = True

    assert send_sms(
        client,
        "+79999999999",
        "SMS"
    ) is True


def test_send_sms_timeout():
    client = Mock()
    client.send.side_effect = TimeoutError()

    assert send_sms(
        client,
        "+79999999999",
        "SMS"
    ) is False


def test_send_push_success():
    client = Mock()
    client.push.return_value = {
        "success": True
    }

    assert send_push(
        client,
        1,
        "Push"
    ) is True


def test_send_push_fail():
    client = Mock()
    client.push.return_value = {
        "success": False
    }

    assert send_push(
        client,
        1,
        "Push"
    ) is False