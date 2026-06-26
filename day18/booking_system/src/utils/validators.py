import re

def is_valid_email(email: str) -> bool:
    """Проверяет валидность email-адреса."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def is_valid_phone(phone: str) -> bool:
    """Проверяет валидность номера телефона"""
    phone = re.sub(r"\D", "", phone)  # Убираем все не-цифры
    return len(phone) == 11 and phone.startswith("7")