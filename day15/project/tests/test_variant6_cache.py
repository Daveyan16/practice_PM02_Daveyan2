import pytest
import time

from app.services import ProductService, ProductRepository
from app.exceptions import ProductNotFoundError


class TestProductServiceCache:
    
    def test_cache_works_with_mock_repo(self, mocker):
        mock_repo = mocker.Mock()
        mock_repo.get_by_id.return_value = {"id": 1, "name": "Book", "price": 29.99}
        
        service = ProductService(mock_repo)
        
        result1 = service.get_product_by_id(1)
        result2 = service.get_product_by_id(1)
        
        assert mock_repo.get_by_id.call_count == 1
        assert result1 == result2
        mock_repo.get_by_id.assert_called_once_with(1)
    
    def test_cache_returns_same_object_reference(self, mocker):
        mock_repo = mocker.Mock()
        test_data = {"id": 1, "name": "Book", "price": 29.99}
        mock_repo.get_by_id.return_value = test_data
        
        service = ProductService(mock_repo)
        
        result1 = service.get_product_by_id(1)
        result2 = service.get_product_by_id(1)
        
        assert result1 is result2
    
    def test_cache_spy_repository_call(self, mocker):
        real_repo = ProductRepository()
        spy = mocker.spy(real_repo, "get_by_id")
        
        service = ProductService(real_repo)
        
        service.get_product_by_id(1)
        service.get_product_by_id(1)
        
        assert spy.call_count == 1
        spy.assert_called_once_with(1)
    
    def test_clear_cache_refreshes_data(self, mocker):
        mock_repo = mocker.Mock()
        mock_repo.get_by_id.side_effect = [
            {"id": 1, "name": "Book", "price": 29.99},
            {"id": 1, "name": "Book", "price": 39.99},
        ]
        
        service = ProductService(mock_repo)
        
        result1 = service.get_product_by_id(1)
        assert result1["price"] == 29.99
        
        service.clear_cache(1)
        
        result2 = service.get_product_by_id(1)
        
        assert mock_repo.get_by_id.call_count == 2
        assert result2["price"] == 39.99
        assert result1 is not result2
    
    def test_clear_all_cache(self, mocker):
        mock_repo = mocker.Mock()
        mock_repo.get_by_id.side_effect = [
            {"id": 1, "name": "Book", "price": 29.99},
            {"id": 2, "name": "Pen", "price": 1.99},
            {"id": 1, "name": "Book", "price": 39.99},
        ]
        
        service = ProductService(mock_repo)
        
        service.get_product_by_id(1)
        service.get_product_by_id(2)
        
        stats = service.get_cache_stats()
        assert stats["cache_size"] == 2
        
        service.clear_cache()
        
        result = service.get_product_by_id(1)
        
        assert mock_repo.get_by_id.call_count == 3
        assert result["price"] == 39.99
    
    def test_cache_ttl_expiration(self, mocker):
        mock_repo = mocker.Mock()
        mock_repo.get_by_id.side_effect = [
            {"id": 1, "name": "Book", "price": 29.99},
            {"id": 1, "name": "Book", "price": 49.99},
        ]
        
        service = ProductService(mock_repo, cache_duration=0.1)
        
        result1 = service.get_product_by_id(1)
        assert result1["price"] == 29.99
        
        time.sleep(0.2)
        
        result2 = service.get_product_by_id(1)
        
        assert mock_repo.get_by_id.call_count == 2
        assert result2["price"] == 49.99
    
    def test_update_product_invalidates_cache(self, mocker):
        """Тест: обновление инвалидирует кэш и обновляет его новыми данными"""
        mock_repo = mocker.Mock()
        mock_repo.get_by_id.return_value = {"id": 1, "name": "Book", "price": 29.99}
        mock_repo.update.return_value = {"id": 1, "name": "Book", "price": 39.99}
        
        service = ProductService(mock_repo)
        
        # Кэшируем продукт (вызов get_by_id)
        cached = service.get_product_by_id(1)
        assert cached["price"] == 29.99
        
        # Обновляем продукт (вызов update, но не get_by_id)
        updated = service.update_product(1, {"price": 39.99})
        
        # Получаем из кэша (не должен вызывать get_by_id, так как кэш обновлен)
        result = service.get_product_by_id(1)
        
        # Проверяем: get_by_id вызван ТОЛЬКО 1 раз (при первом кэшировании)
        assert mock_repo.get_by_id.call_count == 1
        # Проверяем, что update был вызван 1 раз
        mock_repo.update.assert_called_once_with(1, {"price": 39.99})
        # Проверяем, что данные обновились
        assert result["price"] == 39.99
        # Проверяем, что кэш вернул те же данные, что и update
        assert result is updated
    
    def test_force_refresh_ignores_cache(self, mocker):
        mock_repo = mocker.Mock()
        mock_repo.get_by_id.side_effect = [
            {"id": 1, "name": "Book", "price": 29.99},
            {"id": 1, "name": "Book", "price": 39.99},
        ]
        
        service = ProductService(mock_repo)
        
        result1 = service.get_product_by_id(1)
        assert result1["price"] == 29.99
        
        result2 = service.get_product_by_id(1, force_refresh=True)
        
        assert mock_repo.get_by_id.call_count == 2
        assert result2["price"] == 39.99


class TestProductRepository:
    def test_repository_get_by_id(self):
        repo = ProductRepository()
        
        product = repo.get_by_id(1)
        assert product is not None
        assert product["id"] == 1
        assert product["name"] == "Book"
        
        not_found = repo.get_by_id(999)
        assert not_found is None
    
    def test_repository_update(self):
        repo = ProductRepository()
        
        updated = repo.update(1, {"price": 99.99})
        assert updated["price"] == 99.99
        
        with pytest.raises(ProductNotFoundError):
            repo.update(999, {"price": 10.0})