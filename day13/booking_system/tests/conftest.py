import pytest


@pytest.fixture
def sample_hotel():
    return {
        "name": "Grand Hotel",
        "city": "Riga"
    }