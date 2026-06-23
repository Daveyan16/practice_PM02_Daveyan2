"""
Тесты 
Проверяют все исправленные функции

"""

import unittest
import math
import sys
import os

# Добавляем путь к исходным файлам
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from variant_6_fixed import (
    process_data,
    expensive_calculation,
    process_item,
    calculate_metrics,
    clear_all_caches,
    FUNCTION_CACHE,
    CALL_COUNTER,
    get_all_cache_stats
)


class TestVariant6(unittest.TestCase):
    """Тестовый набор для Варианта №6"""
    
    def setUp(self):
        """Подготовка перед каждым тестом - очистка всех кешей"""
        clear_all_caches()
        # Дополнительно сбрасываем счетчик для process_item
        # Так как декоратор-класс сохраняет состояние
        process_item.calls = 0
        process_item.results = []
    
    def test_process_data_basic(self):
        """Тест базовой обработки данных"""
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = process_data(data, multiplier=2.0)
        
        expected = [2.0, 4.0, 6.0, 8.0, 10.0]
        self.assertEqual(result, expected)
        
    def test_process_data_different_multipliers(self):
        """Тест обработки данных с разными множителями"""
        data = [1.0, 2.0, 3.0]
        
        # Тест с множителем 0.5
        result1 = process_data(data, multiplier=0.5)
        expected1 = [0.5, 1.0, 1.5]
        self.assertEqual(result1, expected1)
        
        # Тест с множителем 3.0
        result2 = process_data(data, multiplier=3.0)
        expected2 = [3.0, 6.0, 9.0]
        self.assertEqual(result2, expected2)
        
    def test_process_data_default_multiplier(self):
        """Тест обработки данных с множителем по умолчанию"""
        data = [1.0, 2.0, 3.0]
        result = process_data(data)
        expected = [1.0, 2.0, 3.0]  # multiplier = 1.0
        self.assertEqual(result, expected)
    
    def test_expensive_calculation(self):
        """Тест дорогостоящих вычислений с кешированием"""
        # Первый вызов - кеш промах
        result1 = expensive_calculation(3.0, 4.0)
        expected1 = math.sqrt(9.0 + 16.0)  # = 5.0
        self.assertAlmostEqual(result1, expected1, places=5)
        
        # Второй вызов с теми же аргументами - кеш попадание
        result2 = expensive_calculation(3.0, 4.0)
        self.assertAlmostEqual(result2, expected1, places=5)
        
        # Проверка статистики кеша
        cache_info = expensive_calculation.cache_info()
        self.assertEqual(cache_info.hits, 1)
        self.assertEqual(cache_info.misses, 1)
    
    def test_expensive_calculation_known_values(self):
        """Тест известных значений для expensive_calculation"""
        # Пифагоровы тройки
        test_cases = [
            (3.0, 4.0, 5.0),
            (5.0, 12.0, 13.0),
            (8.0, 15.0, 17.0),
            (7.0, 24.0, 25.0),
        ]
        
        for x, y, expected in test_cases:
            result = expensive_calculation(x, y)
            self.assertAlmostEqual(result, expected, places=5)
    
    def test_process_item_with_decorator(self):
        """Тест декоратора-класса"""
        # Очищаем состояние перед тестом
        process_item.calls = 0
        process_item.results = []
        
        # Проверка функциональности
        for i in range(5):
            result = process_item(i)
            self.assertEqual(result, i * 2)
        
        # Проверка состояния
        stats = process_item.get_stats()
        self.assertEqual(stats['calls'], 5)
        self.assertEqual(stats['results_count'], 5)
        
    def test_process_item_max_results_limit(self):
        """Тест ограничения размера списка результатов"""
        # Очищаем состояние перед тестом
        process_item.calls = 0
        process_item.results = []
        
        # Заполняем больше, чем max_results (100)
        for i in range(200):
            process_item(i)
        
        stats = process_item.get_stats()
        self.assertEqual(stats['calls'], 200)
        self.assertLessEqual(stats['results_count'], stats['max_results'])
    
    def test_calculate_metrics(self):
        """Тест расчета метрик"""
        values = [10, 20, 30, 40, 50]
        result = calculate_metrics(values)
        
        # Проверка значений
        self.assertAlmostEqual(result['mean'], 30.0, places=5)
        self.assertAlmostEqual(result['variance'], 200.0, places=5)
        self.assertAlmostEqual(result['std_dev'], 14.14213562, places=5)
        
        # Тест с одним значением
        single_value = [42]
        result2 = calculate_metrics(single_value)
        self.assertAlmostEqual(result2['mean'], 42.0, places=5)
        self.assertAlmostEqual(result2['variance'], 0.0, places=5)
        self.assertAlmostEqual(result2['std_dev'], 0.0, places=5)
        
        # Тест с пустым списком
        empty_result = calculate_metrics([])
        self.assertEqual(empty_result, {})
    
    def test_cache_clearing(self):
        """Тест очистки кеша"""
        # Заполняем кеш
        for i in range(10):
            process_data([float(i)], multiplier=1.0)
        
        self.assertGreater(len(FUNCTION_CACHE), 0)
        
        # Очищаем кеш
        clear_all_caches()
        
        self.assertEqual(len(FUNCTION_CACHE), 0)
        cache_info = expensive_calculation.cache_info()
        self.assertEqual(cache_info.currsize, 0)
    
    def test_lru_cache_limit(self):
        """Тест ограничения размера LRU кеша"""
        # Очищаем кеш перед тестом
        expensive_calculation.cache_clear()
        
        # Заполняем кеш большим количеством уникальных значений
        for i in range(200):
            expensive_calculation(float(i), float(i % 10))
        
        cache_info = expensive_calculation.cache_info()
        # Кеш не должен превышать maxsize (128)
        self.assertLessEqual(cache_info.currsize, 128)


if __name__ == '__main__':
    unittest.main(verbosity=2)