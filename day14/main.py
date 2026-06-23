# main.py - Пример использования сервиса для демонстрации работы.
import logging.config

# Настройка логгера 
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
         'standard': {
             'format': '%(asctime)s [%(levelname)s] %(name)s %(context)s : %(message)s'
         },
     },
     'handlers': {
         'console': {
             'class': 'logging.StreamHandler',
             'formatter': 'standard',
         },
     },
     'loggers': {
         '': {  # root logger
             'handlers': ['console'],
             'level': 'INFO',
         },
     },
 })
 
if __name__ == "__main__":
     print("Запуск демонстрационного примера работы банковского сервиса...")
     
     from banking.in_memory_repositories import InMemoryAccountRepository, InMemoryTransactionRepository
     from banking.services import BankingService

     # Инициализация зависимостей 
     acc_repo = InMemoryAccountRepository()
     tr_repo = InMemoryTransactionRepository()
     
     service = BankingService(acc_repo, tr_repo)
     
     try:
         # Создаем два счета для теста перевода.
         sender = service.create_account(number="ACC-FROM", owner_name="Sender", initial_balance=200.0)
         receiver = service.create_account(number="ACC-TO", owner_name="Receiver", initial_balance=50.0)
         
         print(f"Счета созданы. Баланс отправителя: {sender.balance}, получателя: {receiver.balance}")
         
         # Выполняем перевод.
         service.transfer(sender.number, receiver.number, 80.0)
         
         print(f"Перевод выполнен. Баланс отправителя: {sender.balance}, получателя: {receiver.balance}")
         
         # Получаем выписку по счету получателя.
         statement = service.get_statement(receiver.number)
         print("\nВыписка по счету получателя:")
         for tr in statement[:2]: # Покажем только последние 2 операции для краткости вывода.
              print(f"ID:{tr.id} | Сумма:{tr.amount} | Тип:{tr.transaction_type} | Описание:{tr.description}")
              
     except Exception as e:
          print(f"Произошла ошибка при выполнении операции: {e}")