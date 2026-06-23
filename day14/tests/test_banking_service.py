import datetime
from decimal import Decimal

from unittest.mock import MagicMock, call
import pytest

# Импортируем класс сервиса
from banking.services import BankingService 

from banking.entities import Account, Transaction
from banking.exceptions import (
    InsufficientFundsError,
    ValidationError,
    DomainError, 
)

def test_create_and_deposit():
    # Arrange - Подготовка моков и данных (AAA Pattern)
    acc_mock = MagicMock()

    # Создаем фейковый аккаунт
    fake_account = Account(id=123, number="ACC-001", owner_name="Ivanov", balance=Decimal('100.0'))
    acc_mock.get_by_number.return_value = fake_account

    tr_mock = MagicMock()

    service = BankingService(acc_mock, tr_mock)

    deposit_amount = Decimal('50.50')

    # Act - Выполнение действия под тестом
    service.deposit(fake_account.number, deposit_amount)

    # Assert - Проверка результатов и поведения моков
    
    # 1. Проверка изменения баланса объекта-сущности
    assert fake_account.balance == Decimal('150.50')

    # 2. Проверка вызова метода обновления репозитория
    acc_mock.update.assert_called_once_with(fake_account)
    
    # 3. Проверка создания транзакции через репозиторий
    expected_call = call(Transaction(
                        id=None,
                        account_id=fake_account.id,
                        amount=deposit_amount,
                        transaction_type='deposit',
                        created_at=pytest.approx(datetime.datetime.now(), abs=datetime.timedelta(seconds=1)),
                        description="Deposit"
                    ))
                    
    assert tr_mock.create.call_count == 1
    assert expected_call in tr_mock.create.call_args_list


def test_withdraw_insufficient_funds():
     mock_acc_repo = MagicMock()

     existing_acc = Account(id=456, number="ACC-002", owner_name="Pyotrov", balance=Decimal('50.00'))
     mock_acc_repo.get_by_number.return_value = existing_acc

     mock_tr_repo = MagicMock()

     service = BankingService(mock_acc_repo, mock_tr_repo)

     withdraw_amount = Decimal('100.00')
     
    
     with pytest.raises(DomainError):
         service.withdraw(existing_acc.number, withdraw_amount)
         

     mock_acc_repo.update.assert_not_called()
     mock_tr_repo.create.assert_not_called()
     
     
     assert existing_acc.balance == Decimal('50.00')


def test_transfer_success():
     src_acc = Account(id=1, number="SRC", balance=Decimal('200.0'), owner_name="Sender")
     dst_acc = Account(id=2, number="DST", balance=Decimal('50.0'), owner_name="Receiver")

     acc_repo = MagicMock()
     acc_repo.get_by_number.side_effect = lambda num: src_acc if num=='SRC' else dst_acc if num=='DST' else None

     tr_repo = MagicMock()
     
     service = BankingService(acc_repo, tr_repo)
     
     transfer_amount = Decimal('80.0')
     
     #Act
     service.transfer(src_acc.number, dst_acc.number, transfer_amount)
     
     # Assert
     #Проверка балансов
     assert src_acc.balance == Decimal('120.0') # 200 - 80
     assert dst_acc.balance == Decimal('130.0') # 50 + 80
     
     #Проверка вызовов update для обоих аккаунтов
     assert acc_repo.update.call_count == 2
     
     #Проверка создания двух транзакций
     assert tr_repo.create.call_count == 2