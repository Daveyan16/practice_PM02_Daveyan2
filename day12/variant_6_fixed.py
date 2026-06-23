"""
Вариант №6: Декораторы и кеширование (ИСПРАВЛЕННАЯ ВЕРСИЯ)

ВСЕ ОШИБКИ ИСПРАВЛЕНЫ:
1. Передача *args, **kwargs - исправлена распаковка
2. Логическая ошибка - исправлен порядок операций
3. Утечка памяти - добавлено ограничение размера кеша
4. Декоратор с состоянием - исправлено сохранение состояния
"""

import time
import math
import tracemalloc
from functools import wraps, lru_cache
from typing import Dict, List, Any, Callable, Tuple, Optional
from collections import OrderedDict
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# КЛАСС ДЛЯ ОГРАНИЧЕННОГО КЕША 

class LimitedCache:
    """Кеш с ограничением размера (LRU - Least Recently Used)"""
    
    def __init__(self, maxsize: int = 100):
        """Инициализация кеша с максимальным размером"""
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кеша"""
        if key in self.cache:
            # Перемещаем в конец (самый свежий)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Сохранение значения в кеш"""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Ограничение размера кеша
        if len(self.cache) > self.maxsize:
            # Удаляем самый старый элемент (первый в OrderedDict)
            self.cache.popitem(last=False)
    
    def __len__(self) -> int:
        """Возвращает текущий размер кеша"""
        return len(self.cache)
    
    def clear(self) -> None:
        """Очистка кеша"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кеша"""
        return {
            'size': len(self.cache),
            'maxsize': self.maxsize,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }


# ГЛОБАЛЬНЫЙ КЕШ С ОГРАНИЧЕНИЕМ 

FUNCTION_CACHE = LimitedCache(maxsize=100)
CALL_COUNTER: Dict[str, int] = {}


#ИСПРАВЛЕННЫЙ ДЕКОРАТОР 

def stateful_decorator(func: Callable) -> Callable:
    """
    Исправленный декоратор с состоянием
    """
    # Используем ограниченный кеш вместо неограниченного словаря
    cache = LimitedCache(maxsize=50)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ИСПРАВЛЕНО: эффективное создание ключа
        key = f"{func.__name__}_{args}_{tuple(kwargs.items())}"
        
        # Проверка кеша
        cached_result = cache.get(key)
        if cached_result is not None:
            logger.debug(f"Возврат из кеша для {key}")
            return cached_result
        
        # ИСПРАВЛЕНО: правильная передача аргументов с распаковкой
        result = func(*args, **kwargs)
        
        # Сохраняем в кеш
        cache.set(key, result)
        FUNCTION_CACHE.set(key, result)
        
        # Увеличиваем счетчик вызовов
        CALL_COUNTER[func.__name__] = CALL_COUNTER.get(func.__name__, 0) + 1
        
        return result
    
    # Добавляем метод для получения статистики кеша
    wrapper.get_cache_stats = cache.get_stats
    return wrapper


# ИСПРАВЛЕННЫЙ ДЕКОРАТОР ДЛЯ ИЗМЕРЕНИЯ ВРЕМЕНИ 

def timing_decorator(func: Callable) -> Callable:
    """Исправленный декоратор для измерения времени выполнения"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} выполнен за {end - start:.4f} секунд")
        return result
    
    return wrapper


#  ИСПРАВЛЕННЫЙ LRU КЕШ 

# ИСПРАВЛЕНО: добавлен maxsize для ограничения размера
@lru_cache(maxsize=128)
def expensive_calculation(x: float, y: float) -> float:
    """
    Исправленная функция с ограниченным кешированием
    """
    # Имитация сложных вычислений
    time.sleep(0.1)
    
    # ИСПРАВЛЕНО: правильный порядок операций
    # Теперь: math.sqrt(x**2 + y**2)
    result = math.sqrt(x ** 2 + y ** 2)
    return result


#  ИСПРАВЛЕННЫЙ ДЕКОРАТОР-КЛАСС 

class CounterDecorator:
    """
    Исправленный декоратор как класс с состоянием
    Теперь с ограничением размера и корректным управлением состоянием
    """
    def __init__(self, func: Callable, max_results: int = 100):
        """
        Инициализация декоратора
        
        Args:
            func: Декорируемая функция
            max_results: Максимальное количество сохраняемых результатов
        """
        self.func = func
        self.calls = 0
        self.results = []
        self.max_results = max_results
        self.last_args = None
        self.last_kwargs = None
    
    def __call__(self, *args, **kwargs):
        """
        Вызов декорированной функции с сохранением состояния
        """
        # ИСПРАВЛЕНО: корректное обновление счетчика
        self.calls += 1
        
        # Сохраняем последние аргументы для отладки
        self.last_args = args
        self.last_kwargs = kwargs
        
        # ИСПРАВЛЕНО: правильная передача аргументов
        result = self.func(*args, **kwargs)
        
        # ИСПРАВЛЕНО: ограничение размера списка результатов
        self.results.append(result)
        if len(self.results) > self.max_results:
            # Оставляем только последние max_results элементов
            self.results = self.results[-self.max_results:]
        
        # ИСПРАВЛЕНО: корректное логирование
        if len(args) > 0:
            logger.debug(f"Вызов #{self.calls} с аргументами: {args[0]}")
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получение статистики декоратора
        
        Returns:
            Dict со статистикой: количество вызовов, размер результатов, и т.д.
        """
        return {
            'calls': self.calls,
            'results_count': len(self.results),
            'max_results': self.max_results,
            'last_args': self.last_args,
            'last_kwargs': self.last_kwargs
        }
    
    def clear_results(self) -> None:
        """Очистка сохраненных результатов"""
        self.results.clear()
        logger.info(f"Результаты декоратора {self.func.__name__} очищены")


# ИСПРАВЛЕННЫЕ ФУНКЦИИ 

@stateful_decorator
@timing_decorator
def process_data(data: List[float], multiplier: float = 1.0) -> List[float]:
    """
    Исправленная обработка данных с правильной формулой
    """
    result = []
    for value in data:
        # ИСПРАВЛЕНО: правильная формула умножения
        processed = value * multiplier
        result.append(processed)
    return result


@stateful_decorator
def calculate_metrics(values: List[float]) -> Dict[str, float]:
    """
    Исправленный расчет метрик с корректными формулами
    """
    if not values:
        return {}
    
    n = len(values)
    
    # ИСПРАВЛЕНО: правильный расчет среднего
    mean = sum(values) / n
    
    # ИСПРАВЛЕНО: правильный расчет дисперсии
    # Используем n вместо (n-1) для генеральной совокупности
    variance = sum((x - mean) ** 2 for x in values) / n if n > 0 else 0
    
    # ИСПРАВЛЕНО: sqrt только от неотрицательного числа
    std_dev = math.sqrt(max(0, variance))
    
    return {
        'mean': mean,
        'variance': variance,
        'std_dev': std_dev
    }


@CounterDecorator
def process_item(item: int) -> int:
    """Исправленная функция с декоратором-классом"""
    return item * 2


# ОЧИСТКА КЕША ПРИ НЕОБХОДИМОСТИ 

def clear_all_caches():
    """Очистка всех кешей"""
    FUNCTION_CACHE.clear()
    expensive_calculation.cache_clear()
    CALL_COUNTER.clear()
    logger.info("Все кеши очищены")


def get_all_cache_stats() -> Dict[str, Any]:
    """Получение статистики всех кешей"""
    return {
        'function_cache': FUNCTION_CACHE.get_stats(),
        'lru_cache': {
            'hits': expensive_calculation.cache_info().hits,
            'misses': expensive_calculation.cache_info().misses,
            'maxsize': expensive_calculation.cache_info().maxsize,
            'currsize': expensive_calculation.cache_info().currsize
        },
        'call_counter': CALL_COUNTER
    }


# ТЕСТОВЫЕ ДАННЫЕ

def run_tests():
    """Запуск тестового набора"""
    print("=" * 70)
    print("ЗАПУСК ТЕСТОВ - ВАРИАНТ №6 (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("=" * 70)
    
    all_tests_passed = True
    
    # Тест 1: Функция с декораторами
    print("\n[ТЕСТ 1] Обработка данных с декораторами")
    test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    try:
        result1 = process_data(test_data, multiplier=2.0)
        print(f"  Результат: {result1}")
        
        # Проверка правильности
        expected = [2.0, 4.0, 6.0, 8.0, 10.0]
        if result1 == expected:
            print("  РЕЗУЛЬТАТ ВЕРНЫЙ!")
        else:
            print(f"   Ожидалось: {expected}")
            all_tests_passed = False
            
        # Проверка кеша
        cache_stats = process_data.get_cache_stats()
        print(f"  Статистика кеша: размер={cache_stats['size']}, hits={cache_stats['hits']}, misses={cache_stats['misses']}")
        
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Тест 2: Дорогостоящие вычисления
    print("\n[ТЕСТ 2] Дорогостоящие вычисления с кешированием")
    try:
        # Заполняем кеш
        test_results = []
        for i in range(25):
            x = i % 5
            y = i % 3
            result2 = expensive_calculation(x, y)
            test_results.append(result2)
            if i < 5:
                print(f"  expensive_calculation({x}, {y}) = {result2:.4f}")
        
        # Проверка правильности
        expected_result = math.sqrt(3**2 + 4**2)  # = 5.0
        # Проверяем последний вызов с x=3, y=4
        last_result = expensive_calculation(3, 4)
        print(f"  Проверка: expensive_calculation(3, 4) = {last_result:.4f}")
        if abs(last_result - 5.0) < 0.0001:
            print("   РЕЗУЛЬТАТ ВЕРНЫЙ!")
        else:
            print(f"   Ожидалось: 5.0000")
            all_tests_passed = False
        
        cache_info = expensive_calculation.cache_info()
        print(f"\n  Статистика кеша:")
        print(f"    hits={cache_info.hits}, misses={cache_info.misses}")
        print(f"    maxsize={cache_info.maxsize}, текущий размер={cache_info.currsize}")
        
        if cache_info.currsize <= 128:
            print("   КЕШ ОГРАНИЧЕН КОРРЕКТНО!")
        else:
            print(f"   Размер кеша превышает 128: {cache_info.currsize}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Тест 3: Декоратор-класс
    print("\n[ТЕСТ 3] Декоратор-класс с состоянием")
    try:
        # Тестируем с большим количеством вызовов
        for i in range(150):
            result3 = process_item(i)
            if i % 20 == 0 and i > 0:
                stats = process_item.get_stats()
                print(f"  process_item({i}) = {result3}, вызовов: {stats['calls']}, результатов: {stats['results_count']}")
        
        stats = process_item.get_stats()
        print(f"\n  Финальная статистика:")
        print(f"    Всего вызовов: {stats['calls']}")
        print(f"    Хранится результатов: {stats['results_count']}")
        print(f"    Максимум результатов: {stats['max_results']}")
        
        if stats['results_count'] <= stats['max_results']:
            print("   СПИСОК РЕЗУЛЬТАТОВ ОГРАНИЧЕН КОРРЕКТНО!")
        else:
            print(f"   Размер списка {stats['results_count']} превышает максимум {stats['max_results']}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Тест 4: Расчет метрик
    print("\n[ТЕСТ 4] Расчет метрик")
    test_values = [10, 20, 30, 40, 50]
    try:
        result4 = calculate_metrics(test_values)
        print(f"  Метрики для {test_values}:")
        print(f"    mean: {result4['mean']:.2f}")
        print(f"    variance: {result4['variance']:.2f}")
        print(f"    std_dev: {result4['std_dev']:.2f}")
        
        # Проверка правильности
        expected_mean = 30.0
        expected_variance = 200.0
        expected_std = 14.14213562
        
        if abs(result4['mean'] - expected_mean) < 0.01:
            print("   СРЕДНЕЕ РАССЧИТАНО ВЕРНО!")
        else:
            print(f"   Ожидалось среднее: {expected_mean}")
            all_tests_passed = False
            
        if abs(result4['variance'] - expected_variance) < 0.01:
            print("   ДИСПЕРСИЯ РАССЧИТАНА ВЕРНО!")
        else:
            print(f"   Ожидалась дисперсия: {expected_variance}")
            all_tests_passed = False
            
        if abs(result4['std_dev'] - expected_std) < 0.01:
            print("   СТАНДАРТНОЕ ОТКЛОНЕНИЕ РАССЧИТАНО ВЕРНО!")
        else:
            print(f"   Ожидалось стандартное отклонение: {expected_std}")
            all_tests_passed = False
            
        # Тест с одним значением
        single_result = calculate_metrics([42])
        if abs(single_result['mean'] - 42.0) < 0.01 and single_result['variance'] == 0:
            print("   РАБОТА С ОДНИМ ЗНАЧЕНИЕМ КОРРЕКТНА!")
        else:
            print("   Ошибка в работе с одним значением")
            all_tests_passed = False
            
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Статистика всех кешей
    print("\n" + "=" * 70)
    print("СТАТИСТИКА ВСЕХ КЕШЕЙ:")
    stats = get_all_cache_stats()
    print(f"  FUNCTION_CACHE: размер={stats['function_cache']['size']}, hits={stats['function_cache']['hits']}")
    print(f"  LRU_CACHE: размер={stats['lru_cache']['currsize']}, maxsize={stats['lru_cache']['maxsize']}")
    print(f"  Счетчики вызовов: {CALL_COUNTER}")
    print("=" * 70)
    
    # Итоговый результат
    print("\n" + "=" * 70)
    if all_tests_passed:
        print(" ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(" НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
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
    
    # Очистка кешей в конце
    clear_all_caches()
    print("\n Программа завершена, все кеши очищены")

"""
Вариант №6: Декораторы и кеширование (ИСПРАВЛЕННАЯ ВЕРСИЯ)
Студент: [Ваше ФИО]
Группа: [Ваша группа]
Дата: [Дата выполнения]

ВСЕ ОШИБКИ ИСПРАВЛЕНЫ:
1. Передача *args, **kwargs - исправлена распаковка
2. Логическая ошибка - исправлен порядок операций
3. Утечка памяти - добавлено ограничение размера кеша
4. Декоратор с состоянием - исправлено сохранение состояния
"""

import time
import math
import tracemalloc
from functools import wraps, lru_cache
from typing import Dict, List, Any, Callable, Tuple, Optional
from collections import OrderedDict
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


#  КЛАСС ДЛЯ ОГРАНИЧЕННОГО КЕША 

class LimitedCache:
    """Кеш с ограничением размера (LRU - Least Recently Used)"""
    
    def __init__(self, maxsize: int = 100):
        """Инициализация кеша с максимальным размером"""
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Получение значения из кеша"""
        if key in self.cache:
            # Перемещаем в конец (самый свежий)
            self.cache.move_to_end(key)
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Сохранение значения в кеш"""
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Ограничение размера кеша
        if len(self.cache) > self.maxsize:
            # Удаляем самый старый элемент (первый в OrderedDict)
            self.cache.popitem(last=False)
    
    def __len__(self) -> int:
        """Возвращает текущий размер кеша"""
        return len(self.cache)
    
    def clear(self) -> None:
        """Очистка кеша"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики кеша"""
        return {
            'size': len(self.cache),
            'maxsize': self.maxsize,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }


#  ГЛОБАЛЬНЫЙ КЕШ С ОГРАНИЧЕНИЕМ 

FUNCTION_CACHE = LimitedCache(maxsize=100)
CALL_COUNTER: Dict[str, int] = {}


# ИСПРАВЛЕННЫЙ ДЕКОРАТОР 

def stateful_decorator(func: Callable) -> Callable:
    """
    Исправленный декоратор с состоянием
    """
    # Используем ограниченный кеш вместо неограниченного словаря
    cache = LimitedCache(maxsize=50)
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # ИСПРАВЛЕНО: эффективное создание ключа
        key = f"{func.__name__}_{args}_{tuple(kwargs.items())}"
        
        # Проверка кеша
        cached_result = cache.get(key)
        if cached_result is not None:
            logger.debug(f"Возврат из кеша для {key}")
            return cached_result
        
        # ИСПРАВЛЕНО: правильная передача аргументов с распаковкой
        result = func(*args, **kwargs)
        
        # Сохраняем в кеш
        cache.set(key, result)
        FUNCTION_CACHE.set(key, result)
        
        # Увеличиваем счетчик вызовов
        CALL_COUNTER[func.__name__] = CALL_COUNTER.get(func.__name__, 0) + 1
        
        return result
    
    # Добавляем метод для получения статистики кеша
    wrapper.get_cache_stats = cache.get_stats
    return wrapper


#  ИСПРАВЛЕННЫЙ ДЕКОРАТОР ДЛЯ ИЗМЕРЕНИЯ ВРЕМЕНИ 

def timing_decorator(func: Callable) -> Callable:
    """Исправленный декоратор для измерения времени выполнения"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info(f"{func.__name__} выполнен за {end - start:.4f} секунд")
        return result
    
    return wrapper


#  ИСПРАВЛЕННЫЙ LRU КЕШ 

# ИСПРАВЛЕНО: добавлен maxsize для ограничения размера
@lru_cache(maxsize=128)
def expensive_calculation(x: float, y: float) -> float:
    """
    Исправленная функция с ограниченным кешированием
    """
    # Имитация сложных вычислений
    time.sleep(0.1)
    
    # ИСПРАВЛЕНО: правильный порядок операций
    # Теперь: math.sqrt(x**2 + y**2)
    result = math.sqrt(x ** 2 + y ** 2)
    return result


#  ИСПРАВЛЕННЫЙ ДЕКОРАТОР-КЛАСС 

class CounterDecorator:
    """
    Исправленный декоратор как класс с состоянием
    Теперь с ограничением размера и корректным управлением состоянием
    """
    def __init__(self, func: Callable, max_results: int = 100):
        """
        Инициализация декоратора
        
        Args:
            func: Декорируемая функция
            max_results: Максимальное количество сохраняемых результатов
        """
        self.func = func
        self.calls = 0
        self.results = []
        self.max_results = max_results
        self.last_args = None
        self.last_kwargs = None
    
    def __call__(self, *args, **kwargs):
        """
        Вызов декорированной функции с сохранением состояния
        """
        # ИСПРАВЛЕНО: корректное обновление счетчика
        self.calls += 1
        
        # Сохраняем последние аргументы для отладки
        self.last_args = args
        self.last_kwargs = kwargs
        
        # ИСПРАВЛЕНО: правильная передача аргументов
        result = self.func(*args, **kwargs)
        
        # ИСПРАВЛЕНО: ограничение размера списка результатов
        self.results.append(result)
        if len(self.results) > self.max_results:
            # Оставляем только последние max_results элементов
            self.results = self.results[-self.max_results:]
        
        # ИСПРАВЛЕНО: корректное логирование
        if len(args) > 0:
            logger.debug(f"Вызов #{self.calls} с аргументами: {args[0]}")
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получение статистики декоратора
        
        Returns:
            Dict со статистикой: количество вызовов, размер результатов, и т.д.
        """
        return {
            'calls': self.calls,
            'results_count': len(self.results),
            'max_results': self.max_results,
            'last_args': self.last_args,
            'last_kwargs': self.last_kwargs
        }
    
    def clear_results(self) -> None:
        """Очистка сохраненных результатов"""
        self.results.clear()
        logger.info(f"Результаты декоратора {self.func.__name__} очищены")


#  ИСПРАВЛЕННЫЕ ФУНКЦИИ 

@stateful_decorator
@timing_decorator
def process_data(data: List[float], multiplier: float = 1.0) -> List[float]:
    """
    Исправленная обработка данных с правильной формулой
    """
    result = []
    for value in data:
        # ИСПРАВЛЕНО: правильная формула умножения
        processed = value * multiplier
        result.append(processed)
    return result


@stateful_decorator
def calculate_metrics(values: List[float]) -> Dict[str, float]:
    """
    Исправленный расчет метрик с корректными формулами
    """
    if not values:
        return {}
    
    n = len(values)
    
    # ИСПРАВЛЕНО: правильный расчет среднего
    mean = sum(values) / n
    
    # ИСПРАВЛЕНО: правильный расчет дисперсии
    # Используем n вместо (n-1) для генеральной совокупности
    variance = sum((x - mean) ** 2 for x in values) / n if n > 0 else 0
    
    # ИСПРАВЛЕНО: sqrt только от неотрицательного числа
    std_dev = math.sqrt(max(0, variance))
    
    return {
        'mean': mean,
        'variance': variance,
        'std_dev': std_dev
    }


@CounterDecorator
def process_item(item: int) -> int:
    """Исправленная функция с декоратором-классом"""
    return item * 2


# ОЧИСТКА КЕША ПРИ НЕОБХОДИМОСТИ 

def clear_all_caches():
    """Очистка всех кешей"""
    FUNCTION_CACHE.clear()
    expensive_calculation.cache_clear()
    CALL_COUNTER.clear()
    logger.info("Все кеши очищены")


def get_all_cache_stats() -> Dict[str, Any]:
    """Получение статистики всех кешей"""
    return {
        'function_cache': FUNCTION_CACHE.get_stats(),
        'lru_cache': {
            'hits': expensive_calculation.cache_info().hits,
            'misses': expensive_calculation.cache_info().misses,
            'maxsize': expensive_calculation.cache_info().maxsize,
            'currsize': expensive_calculation.cache_info().currsize
        },
        'call_counter': CALL_COUNTER
    }


# ТЕСТОВЫЕ ДАННЫЕ 

def run_tests():
    """Запуск тестового набора"""
    print("=" * 70)
    print("ЗАПУСК ТЕСТОВ - ВАРИАНТ №6 (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("=" * 70)
    
    all_tests_passed = True
    
    # Тест 1: Функция с декораторами
    print("\n[ТЕСТ 1] Обработка данных с декораторами")
    test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    
    try:
        result1 = process_data(test_data, multiplier=2.0)
        print(f"  Результат: {result1}")
        
        # Проверка правильности
        expected = [2.0, 4.0, 6.0, 8.0, 10.0]
        if result1 == expected:
            print("   РЕЗУЛЬТАТ ВЕРНЫЙ!")
        else:
            print(f"   Ожидалось: {expected}")
            all_tests_passed = False
            
        # Проверка кеша
        cache_stats = process_data.get_cache_stats()
        print(f"  Статистика кеша: размер={cache_stats['size']}, hits={cache_stats['hits']}, misses={cache_stats['misses']}")
        
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Тест 2: Дорогостоящие вычисления
    print("\n[ТЕСТ 2] Дорогостоящие вычисления с кешированием")
    try:
        # Заполняем кеш
        test_results = []
        for i in range(25):
            x = i % 5
            y = i % 3
            result2 = expensive_calculation(x, y)
            test_results.append(result2)
            if i < 5:
                print(f"  expensive_calculation({x}, {y}) = {result2:.4f}")
        
        # Проверка правильности
        expected_result = math.sqrt(3**2 + 4**2)  # = 5.0
        # Проверяем последний вызов с x=3, y=4
        last_result = expensive_calculation(3, 4)
        print(f"  Проверка: expensive_calculation(3, 4) = {last_result:.4f}")
        if abs(last_result - 5.0) < 0.0001:
            print("   РЕЗУЛЬТАТ ВЕРНЫЙ!")
        else:
            print(f"   Ожидалось: 5.0000")
            all_tests_passed = False
        
        cache_info = expensive_calculation.cache_info()
        print(f"\n  Статистика кеша:")
        print(f"    hits={cache_info.hits}, misses={cache_info.misses}")
        print(f"    maxsize={cache_info.maxsize}, текущий размер={cache_info.currsize}")
        
        if cache_info.currsize <= 128:
            print("   КЕШ ОГРАНИЧЕН КОРРЕКТНО!")
        else:
            print(f"   Размер кеша превышает 128: {cache_info.currsize}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"  Ошибка: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Тест 3: Декоратор-класс
    print("\n[ТЕСТ 3] Декоратор-класс с состоянием")
    try:
        # Тестируем с большим количеством вызовов
        for i in range(150):
            result3 = process_item(i)
            if i % 20 == 0 and i > 0:
                stats = process_item.get_stats()
                print(f"  process_item({i}) = {result3}, вызовов: {stats['calls']}, результатов: {stats['results_count']}")
        
        stats = process_item.get_stats()
        print(f"\n  Финальная статистика:")
        print(f"    Всего вызовов: {stats['calls']}")
        print(f"    Хранится результатов: {stats['results_count']}")
        print(f"    Максимум результатов: {stats['max_results']}")
        
        if stats['results_count'] <= stats['max_results']:
            print("   СПИСОК РЕЗУЛЬТАТОВ ОГРАНИЧЕН КОРРЕКТНО!")
        else:
            print(f"   Размер списка {stats['results_count']} превышает максимум {stats['max_results']}")
            all_tests_passed = False
            
    except Exception as e:
        print(f"   Ошибка: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Тест 4: Расчет метрик
    print("\n[ТЕСТ 4] Расчет метрик")
    test_values = [10, 20, 30, 40, 50]
    try:
        result4 = calculate_metrics(test_values)
        print(f"  Метрики для {test_values}:")
        print(f"    mean: {result4['mean']:.2f}")
        print(f"    variance: {result4['variance']:.2f}")
        print(f"    std_dev: {result4['std_dev']:.2f}")
        
        # Проверка правильности
        expected_mean = 30.0
        expected_variance = 200.0
        expected_std = 14.14213562
        
        if abs(result4['mean'] - expected_mean) < 0.01:
            print("   СРЕДНЕЕ РАССЧИТАНО ВЕРНО!")
        else:
            print(f"   Ожидалось среднее: {expected_mean}")
            all_tests_passed = False
            
        if abs(result4['variance'] - expected_variance) < 0.01:
            print("   ДИСПЕРСИЯ РАССЧИТАНА ВЕРНО!")
        else:
            print(f"   Ожидалась дисперсия: {expected_variance}")
            all_tests_passed = False
            
        if abs(result4['std_dev'] - expected_std) < 0.01:
            print("   СТАНДАРТНОЕ ОТКЛОНЕНИЕ РАССЧИТАНО ВЕРНО!")
        else:
            print(f"   Ожидалось стандартное отклонение: {expected_std}")
            all_tests_passed = False
            
        # Тест с одним значением
        single_result = calculate_metrics([42])
        if abs(single_result['mean'] - 42.0) < 0.01 and single_result['variance'] == 0:
            print(" РАБОТА С ОДНИМ ЗНАЧЕНИЕМ КОРРЕКТНА!")
        else:
            print(" Ошибка в работе с одним значением")
            all_tests_passed = False
            
    except Exception as e:
        print(f"  Ошибка: {e}")
        import traceback
        traceback.print_exc()
        all_tests_passed = False
    
    # Статистика всех кешей
    print("\n" + "=" * 70)
    print("СТАТИСТИКА ВСЕХ КЕШЕЙ:")
    stats = get_all_cache_stats()
    print(f"  FUNCTION_CACHE: размер={stats['function_cache']['size']}, hits={stats['function_cache']['hits']}")
    print(f"  LRU_CACHE: размер={stats['lru_cache']['currsize']}, maxsize={stats['lru_cache']['maxsize']}")
    print(f"  Счетчики вызовов: {CALL_COUNTER}")
    print("=" * 70)
    
    # Итоговый результат
    print("\n" + "=" * 70)
    if all_tests_passed:
        print(" ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print(" НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ!")
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
    print("\n🔍 ТОП-5 строк по потреблению памяти:")
    for stat in snapshot.statistics('lineno')[:5]:
        print(f"  {stat}")
    
    # Очистка кешей в конце
    clear_all_caches()
    print("\n Программа завершена, все кеши очищены")