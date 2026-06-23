import pytest
from unittest.mock import Mock
from app.services import ProductService, ProductRepository


@pytest.fixture
def mock_repository():
    return Mock(spec=ProductRepository)


@pytest.fixture
def product_service(mock_repository):
    return ProductService(mock_repository, cache_duration=60)


@pytest.fixture
def real_repository():
    return ProductRepository()


@pytest.fixture
def real_product_service(real_repository):
    return ProductService(real_repository, cache_duration=0.5)