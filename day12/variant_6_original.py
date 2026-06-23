Вариант №6: Декораторы и кеширование (ИСХОДНЫЙ КОД С ОШИБКАМИ)

import time
import math
import tracemalloc
from functools import wraps, lru_cache
from typing import Dict, List, Any, Callable, Tuple
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальный кеш для декоратора с состоянием
FUNCTION_CACHE: Dict[str, Any] = {}
CALL_COUNTER: Dict[str, int] = {}


# ДЕКОРАТОР С ОШИБКАМИ 

def stateful_decorator(func: Callable) -> Callable:
    """
    Декоратор с состоянием - ОШИБКА: неправильная передача аргументов
    """
    cache = {}  # Локальный кеш декоратора - УТЕЧКА ПАМЯТИ
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ОШИБКА 1: Неправильная передача *args, **kwargs
        # Здесь args передаются как один кортеж, а не распаковываются
        key = str(args) + str(kwargs)  # Неэффективный способ
        
        # ОШИБКА 2: Утечка памяти - кеш неограниченного размера
        if key in cache:
            logger.debug(f"Возврат из кеша для {key}")
            return cache[key]
        
        breakpoint()
        # ОШИБКА 3: Неправильный порядок операций в вычислениях
        result = func(args, kwargs)  # Должно быть func(*args, **kwargs)
        
        # Сохраняем в кеш
        cache[key] = result
        FUNCTION_CACHE[key] = result
        
        # Увеличиваем счетчик вызовов
        CALL_COUNTER[func.__name__] = CALL_COUNTER.get(func.__name__, 0) + 1
        
        return result
    
    return wrapper


# ДЕКОРАТОР ДЛЯ ИЗМЕРЕНИЯ ВРЕМЕНИ 

def timing_decorator(func: Callable) -> Callable:
    """Декоратор для измерения времени выполнения"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} выполнен за {end - start:.4f} секунд")
        return result
    
    return wrapper


#  ОШИБОЧНЫЙ LRU КЕШ 

# ОШИБКА 4: Использование lru_cache без maxsize
@lru_cache(maxsize=None)  # Без ограничения размера!
def expensive_calculation(x: float, y: float) -> float:
    """
    Дорогостоящая функция с кешированием
    """
    # Имитация сложных вычислений
    time.sleep(0.1)
    
    # Логическая ошибка: неправильный порядок операций
    # Должно быть: math.sqrt(x**2 + y**2)
    # А здесь: math.sqrt(x**2) + y**2 (неправильно)
    result = math.sqrt(x ** 2) + y ** 2
    return result


#  ДЕКОРАТОР С ОШИБКОЙ СОСТОЯНИЯ 

class CounterDecorator:
    """
    Декоратор как класс с состоянием
    ОШИБКА: состояние не сохраняется корректно
    """
    def __init__(self, func: Callable):
        self.func = func
        self.calls = 0
        self.results = []  # Утечка памяти!
    
    def __call__(self, *args, **kwargs):
        # ОШИБКА: неправильное обновление состояния
        self.calls = self.calls + 1  # Работает, но...
        
        # ОШИБКА: сохранение всех результатов вызывает утечку памяти
        result = self.func(*args, **kwargs)
        self.results.append(result)  # Бесконечный рост!
        
        # ОШИБКА: неправильная передача аргументов
        if len(args) > 0:
            logger.debug(f"Вызов #{self.calls} с аргументами: {args[0]}")
        
        return result


#  ФУНКЦИИ ДЛЯ ТЕСТИРОВАНИЯ 

@stateful_decorator
@timing_decorator
def process_data(data: List[float], multiplier: float = 1.0) -> List[float]:
    """
    Обработка данных с применением декораторов
    """
    result = []
    for value in data:
        # Логическая ошибка в формуле
        # Должно быть: value * multiplier
        # А здесь: value + multiplier (неправильно)
        processed = value + multiplier
        result.append(processed)
    return result


@stateful_decorator
def calculate_metrics(values: List[float]) -> Dict[str, float]:
    """
    Расчет метрик с ошибками
    """
    if not values:
        return {}
    
    # Логическая ошибка: неправильный порядок операций
    # Должно быть: sum(values) / len(values)
    # А здесь: sum(values) - len(values)
    mean = sum(values) - len(values)
    
    # Ошибка: деление на ноль при len(values) == 1
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1) if len(values) > 1 else 0
    
    # Логическая ошибка: sqrt от отрицательного числа
    std_dev = math.sqrt(variance) if variance >= 0 else 0
    
    return {
        'mean': mean,
        'variance': variance,
        'std_dev': std_dev
    }


@CounterDecorator
def process_item(item: int) -> int:
    """Простая функция для демонстрации декоратора-класса"""
    return item * 2


#  ТЕСТОВЫЕ ДАННЫЕ 

def run_tests():
    """Запуск тестового набора"""
    print("=" * 70)
    print("ЗАПУСК ТЕСТОВ - ВАРИАНТ №6 (Декораторы)")
    print("=" * 70)
    
    # Тест 1: Функция с декораторами
    print("\n[ТЕСТ 1] Обработка данных с декораторами")
    test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    try:
        result1 = process_data(test_data, multiplier=2.0)
        print(f"  Результат: {result1}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 2: Дорогостоящие вычисления
    print("\n[ТЕСТ 2] Дорогостоящие вычисления с кешированием")
    try:
        for i in range(20):
            x = i % 5
            y = i % 3
            result2 = expensive_calculation(x, y)
            if i < 5:
                print(f"  expensive_calculation({x}, {y}) = {result2:.4f}")
        cache_info = expensive_calculation.cache_info()
        print(f"  Статистика кеша: hits={cache_info.hits}, misses={cache_info.misses}, maxsize={cache_info.maxsize}")
        print(f"  Размер кеша: {cache_info.currsize}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 3: Декоратор-класс
    print("\n[ТЕСТ 3] Декоратор-класс с состоянием")
    try:
        for i in range(10):
            result3 = process_item(i)
            if i % 3 == 0:
                print(f"  process_item({i}) = {result3}")
        print(f"  Количество вызовов: {process_item.calls}")
        print(f"  Размер списка результатов: {len(process_item.results)}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # Тест 4: Расчет метрик
    print("\n[ТЕСТ 4] Расчет метрик")
    test_values = [10, 20, 30, 40, 50]
    try:
        result4 = calculate_metrics(test_values)
        print(f"  Метрики для {test_values}:")
        print(f"    mean: {result4['mean']:.2f}")
        print(f"    variance: {result4['variance']:.2f}")
        print(f"    std_dev: {result4['std_dev']:.2f}")
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    # Статистика
    print("\n" + "=" * 70)
    print("СТАТИСТИКА:")
    print(f"  Размер FUNCTION_CACHE: {len(FUNCTION_CACHE)}")
    print(f"  Счетчики вызовов: {CALL_COUNTER}")
    print("=" * 70)


if __name__ == "__main__":
    # Запуск трассировки памяти
    tracemalloc.start()
    
    try:
        run_tests()
    except Exception as e:
        print(f"\n КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
    
    # Анализ памяти
    snapshot = tracemalloc.take_snapshot()
    print("\n ТОП-5 строк по потреблению памяти:")
    for stat in snapshot.statistics('lineno')[:5]:
        print(f"  {stat}")