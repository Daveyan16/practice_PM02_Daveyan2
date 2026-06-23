import time
from typing import Dict, Any, Optional
from datetime import datetime

from app.exceptions import ProductNotFoundError, InsufficientStockError, RepositoryError


class ProductRepository:
    def __init__(self):
        self._products: Dict[int, Dict[str, Any]] = {
            1: {"id": 1, "name": "Book", "price": 29.99, "stock": 10},
            2: {"id": 2, "name": "Pen", "price": 1.99, "stock": 100},
            3: {"id": 3, "name": "Notebook", "price": 5.99, "stock": 50},
        }
    
    def get_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        time.sleep(0.05)
        return self._products.get(product_id)
    
    def update(self, product_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        if product_id not in self._products:
            raise ProductNotFoundError(product_id)
        self._products[product_id].update(data)
        return self._products[product_id]
    
    def reserve_stock(self, product_id: int, quantity: int) -> bool:
        product = self.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        if product["stock"] < quantity:
            raise InsufficientStockError(product_id, quantity, product["stock"])
        product["stock"] -= quantity
        return True


class ProductService:
    def __init__(self, repository: ProductRepository, cache_duration: int = 60):
        self.repository = repository
        self._cache: Dict[int, Dict[str, Any]] = {}
        self._cache_ttl: Dict[int, float] = {}
        self._cache_duration = cache_duration
        self._hit_count = 0
        self._miss_count = 0
    
    def get_product_by_id(self, product_id: int, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        if force_refresh:
            return self._get_from_repository_and_cache(product_id)
        
        if product_id in self._cache:
            if self._cache_ttl.get(product_id, 0) > datetime.now().timestamp():
                self._hit_count += 1
                return self._cache[product_id]
            else:
                del self._cache[product_id]
                del self._cache_ttl[product_id]
                self._miss_count += 1
        else:
            self._miss_count += 1
        
        return self._get_from_repository_and_cache(product_id)
    
    def _get_from_repository_and_cache(self, product_id: int) -> Optional[Dict[str, Any]]:
        try:
            product = self.repository.get_by_id(product_id)
            if product:
                
                self._cache[product_id] = product
                self._cache_ttl[product_id] = datetime.now().timestamp() + self._cache_duration
            return product
        except Exception as e:
            raise RepositoryError(f"Failed to fetch product {product_id}: {str(e)}")
    
    def clear_cache(self, product_id: Optional[int] = None) -> None:
        if product_id is not None:
            self._cache.pop(product_id, None)
            self._cache_ttl.pop(product_id, None)
        else:
            self._cache.clear()
            self._cache_ttl.clear()
            self._hit_count = 0
            self._miss_count = 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        return {
            "cache_size": len(self._cache),
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "total_requests": self._hit_count + self._miss_count,
            "hit_rate": self._hit_count / (self._hit_count + self._miss_count) 
                        if (self._hit_count + self._miss_count) > 0 else 0.0,
        }
    
    def update_product(self, product_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        updated = self.repository.update(product_id, data)
        self._cache[product_id] = updated
        self._cache_ttl[product_id] = datetime.now().timestamp() + self._cache_duration
        return updated