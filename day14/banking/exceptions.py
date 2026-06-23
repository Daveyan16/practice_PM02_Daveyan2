class DomainError(Exception):
    """Базовый класс для всех бизнес-ошибок."""
    pass

class ValidationError(DomainError):
    pass

class AccountNotFoundError(DomainError):
     def __init__(self, account_id=None, number=None):
         if number:
             super().__init__(f"Account with number '{number}' not found")
         else:
             super().__init__(f"Account with ID {account_id} not found")

class InsufficientFundsError(DomainError):
     pass

class TransferLimitExceededError(DomainError):
     pass

class FraudSuspicionError(DomainError):
     pass

class InactiveAccountError(DomainError):
     pass# banking/exceptions.py

class DomainError(Exception):
    """Базовый класс для всех бизнес-ошибок."""
    pass

class ValidationError(DomainError):
    pass

class AccountNotFoundError(DomainError):
     def __init__(self, account_id=None, number=None):
         if number:
             super().__init__(f"Account with number '{number}' not found")
         else:
             super().__init__(f"Account with ID {account_id} not found")

class InsufficientFundsError(DomainError):
     pass

class TransferLimitExceededError(DomainError):
     pass

class FraudSuspicionError(DomainError):
     pass

class InactiveAccountError(DomainError):
     pass