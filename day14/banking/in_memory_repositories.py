from .entities import Account, Transaction
from .repositories import AccountRepository, TransactionRepository
import datetime as dt
from typing import Protocol, List  # Импортируем List для аннотаций типов

class InMemoryAccountRepository(AccountRepository):
    """Хранение счетов в памяти (словарь)"""
    def __init__(self):
        self._accounts = {}
        self._by_number = {}
        self._counter = 1

    def get_by_id(self, account_id: int) -> Account:
        if account_id not in self._accounts:
            raise AccountNotFoundError(account_id=account_id)
        return self._accounts[account_id]

    def get_by_number(self, number: str) -> Account:
        if number not in self._by_number:
            raise AccountNotFoundError(number=number)
        return self.get_by_id(self._by_number[number])

    def create(self, account: Account) -> Account:
        if account.number in self._by_number:
            raise ValueError("Account number already exists")
        new_account = Account(
            id=self._counter,
            number=account.number,
            owner_name=account.owner_name,
            balance=account.balance,
            is_active=account.is_active,
        )
        self._accounts[self._counter] = new_account
        self._by_number[new_account.number] = self._counter
        self._counter += 1
        return new_account

    def update(self, account: Account) -> None:
        if account.id not in self._accounts:
            raise AccountNotFoundError(account_id=account.id)
        self._accounts[account.id] = account


class InMemoryTransactionRepository(TransactionRepository):
    """Хранение транзакций в памяти (словарь)"""
    def __init__(self):
        self._transactions = {}
        self._counter = 1

    def create(self, transaction: Transaction) -> Transaction:
        new_tr = Transaction(
            id=self._counter,
            account_id=transaction.account_id,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            created_at=dt.datetime.now(),
            description=transaction.description,
        )
        self._transactions[self._counter] = new_tr
        self._counter += 1
        return new_tr

    def find_by_account_id(self, account_id: int) -> List[Transaction]:
        """
        Возвращает список транзакций для указанного счета.
        Аннотация '-> List[Transaction]' указывает, что метод возвращает список объектов типа Transaction
        """
        return [t for t in self._transactions.values() if t.account_id == account_id]