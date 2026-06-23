import datetime as dt
import logging.config
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from .config import DAILY_TRANSFER_LIMIT, LOGGING_CONFIG
from .entities import Account, Transaction
from .repositories import AccountRepository, TransactionRepository
from .exceptions import *

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

class BankingService:
    """
    Сервисный слой для банковских операций
    Внедрение зависимостей через конструктор
    """
    #Используем значение из конфига, преобразуя его в Decimal для точности
    DAILY_TRANSFER_LIMIT = Decimal(str(DAILY_TRANSFER_LIMIT)) 
    
    def __init__(
        self,
        account_repo: AccountRepository,
        transaction_repo: TransactionRepository,
    ):
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo

    #Операции со счетами
    def create_account(self, number: str, owner_name: str, initial_balance: float = 0.0) -> Account:
        if initial_balance < 0:
            raise ValidationError("Initial balance cannot be negative")
        
        account = Account(id=None, number=number, owner_name=owner_name, balance=initial_balance)
        saved_account = self.account_repo.create(account)
        logger.info("Account created", extra={"account_id": saved_account.id})
        return saved_account

    #Финансовые операции 
    def deposit(self, account_number: str, amount: float) -> None:
        if amount <= 0:
            raise ValidationError("Deposit amount must be positive")
        
        account = self.account_repo.get_by_number(account_number)
        
        try:
            old_balance = account.balance  # Сохраняем состояние до операции
            account.balance += amount
            
            self.account_repo.update(account)
            
            tr = Transaction(
                id=None,
                account_id=account.id,
                amount=amount,
                transaction_type='deposit',
                created_at=dt.datetime.now(),
                description="Deposit"
            )
            self.transaction_repo.create(tr)
            
            logger.info("Deposit successful", extra={"account_id": account.id, "amount": amount})
            
        except Exception as e:
             # Откат состояния (Rollback)
             account.balance = old_balance
             logger.error("Deposit failed and rolled back", exc_info=True)
             raise DomainError("Deposit operation failed") from e

    def withdraw(self, account_number: str, amount: float) -> None:
        if amount <= 0:
            raise ValidationError("Withdrawal amount must be positive")
        
        account = self.account_repo.get_by_number(account_number)

        
        old_balance = account.balance 

        try:
            if account.balance < amount:
                raise InsufficientFundsError()
                
            account.balance -= amount
            
            daily_sum = sum(
                abs(t.amount) for t in self.transaction_repo.find_by_account_id(account.id)
                if t.created_at.date() == dt.date.today() and t.transaction_type == 'withdrawal'
            )
            if Decimal(daily_sum + amount).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) > BankingService.DAILY_TRANSFER_LIMIT:
                raise TransferLimitExceededError(f"Daily limit {BankingService.DAILY_TRANSFER_LIMIT} exceeded")

            self.account_repo.update(account)

            tr = Transaction(
                id=None,
                account_id=account.id,
                amount=-amount,
                transaction_type='withdrawal',
                created_at=dt.datetime.now(),
                description="Withdrawal"
            )
            self.transaction_repo.create(tr)

            logger.info("Withdrawal successful", extra={"account_id": account.id, "amount": amount})

        except Exception as e:
             #Откат состояния 
             account.balance = old_balance
             logger.error("Withdrawal failed and rolled back", exc_info=True)
             raise DomainError("Withdrawal operation failed") from e

    def transfer(
        self,
        from_account_number: str,
        to_account_number: str,
        amount: float,
    ) -> None:
        if amount <= 0:
            raise ValidationError("Transfer amount must be positive")
        
        from_account = self.account_repo.get_by_number(from_account_number)
        to_account = self.account_repo.get_by_number(to_account_number)
        
        
        old_from_balance = from_account.balance
        old_to_balance = to_account.balance

        try:
            if from_account.balance < amount:
                raise InsufficientFundsError()

            from_account.balance -= amount 
            self.account_repo.update(from_account)
             
            to_account.balance += amount 
            self.account_repo.update(to_account)
             
            now = dt.datetime.now()
             
            tr_out = Transaction(
                id=None,
                account_id=from_account.id,
                amount=-amount,
                transaction_type='transfer',
                created_at=now,
                description=f"Transfer to {to_account.number}"
            )
            self.transaction_repo.create(tr_out)
             
            tr_in = Transaction(
                id=None,
                account_id=to_account.id,
                amount=amount,
                transaction_type='transfer',
                created_at=now,
                description=f"Transfer from {from_account.number}"
            )
            self.transaction_repo.create(tr_in)
             
            logger.info(
                "Transfer successful",
                extra={
                    "from": from_account.number,
                    "to": to_account.number,
                    "amount": amount,
                }
            )
        except Exception as e:
            #Откат балансов
            from_account.balance = old_from_balance
            to_account.balance = old_to_balance
            logger.error("Transfer failed and rolled back", exc_info=True)
            raise DomainError("Transfer operation failed") from e

    def get_statement(self, account_number: str) -> List[Transaction]:
         """Получение выписки по счету"""
         account = self.account_repo.get_by_number(account_number)
         return sorted(
             self.transaction_repo.find_by_account_id(account.id),
             key=lambda x: x.created_at,
             reverse=True  
         )