import pytest

from datetime import timedelta

from app.repositories import OrderRepository
from app.exceptions import (
    EntityNotFoundException,
    DeliveryCalculationException
)
from app.models import OrderItem


@pytest.fixture
def repository(db_session):
    return OrderRepository(db_session)


@pytest.fixture
def order_data():
    return {
        "status": "PENDING",
        "customer_name": "Ivan Ivanov",
        "delivery_address": "Moscow",
        "total_amount": 300.0,
        "items": [
            {
                "product_name": "Phone",
                "quantity": 2,
                "price": 100.0
            },
            {
                "product_name": "Case",
                "quantity": 1,
                "price": 100.0
            }
        ]
    }



#CREATE


def test_create_order(repository, order_data):
    order = repository.create(order_data)

    assert order.id is not None
    assert order.customer_name == "Ivan Ivanov"
    assert order.status == "PENDING"
    assert len(order.items) == 2
    assert order.total_amount == 300.0


def test_create_order_with_items(repository, order_data):
    order = repository.create(order_data)

    assert len(order.items) == 2

    assert order.items[0].product_name == "Phone"
    assert order.items[1].product_name == "Case"



#FIND BY ID


def test_find_existing_order(repository, order_data):
    created_order = repository.create(order_data)

    found_order = repository.find_by_id(
        created_order.id
    )

    assert found_order is not None
    assert found_order.id == created_order.id


def test_find_non_existing_order(repository):
    result = repository.find_by_id(99999)

    assert result is None



#FIND BY STATUS


@pytest.mark.parametrize(
    "status",
    [
        "PENDING",
        "PAID",
        "SHIPPED",
        "CANCELLED"
    ]
)
def test_find_all_by_status(
    repository,
    order_data,
    status
):
    order_data["status"] = status

    repository.create(order_data)

    result = repository.find_all_by_status(
        status
    )

    assert len(result) == 1
    assert result[0].status == status


def test_find_only_needed_status(
    repository,
    order_data
):
    repository.create(order_data)

    second = order_data.copy()
    second["status"] = "PAID"

    repository.create(second)

    pending_orders = (
        repository.find_all_by_status(
            "PENDING"
        )
    )

    assert len(pending_orders) == 1
    assert pending_orders[0].status == "PENDING"



#UPDATE STATUS


def test_update_status(
    repository,
    order_data
):
    order = repository.create(order_data)

    updated_order = (
        repository.update_status(
            order.id,
            "PAID"
        )
    )

    assert updated_order.status == "PAID"


def test_update_status_not_found(
    repository
):
    with pytest.raises(
        EntityNotFoundException
    ):
        repository.update_status(
            999,
            "PAID"
        )



# DELETE


def test_delete_order(
    repository,
    order_data
):
    order = repository.create(order_data)

    repository.delete(order.id)

    deleted = repository.find_by_id(
        order.id
    )

    assert deleted is None


def test_delete_order_items_cascade(
    repository,
    order_data,
    db_session
):
    order = repository.create(order_data)

    repository.delete(order.id)

    items = db_session.query(
        OrderItem
    ).all()

    assert len(items) == 0


def test_delete_not_found(
    repository
):
    with pytest.raises(
        EntityNotFoundException
    ):
        repository.delete(999)



# DATE RANGE


def test_find_by_date_range(
    repository,
    order_data
):
    order = repository.create(order_data)

    start = (
        order.created_at -
        timedelta(days=1)
    )

    end = (
        order.created_at +
        timedelta(days=1)
    )

    result = (
        repository.find_by_date_range(
            start,
            end
        )
    )

    assert len(result) == 1
    assert result[0].id == order.id


def test_find_by_date_range_empty(
    repository,
    order_data
):
    repository.create(order_data)

    start = (
        order_data.get(
            "created_at",
            None
        )
    )

    result = repository.find_by_date_range(
        timedelta(days=100),
        timedelta(days=101)
    )

    assert result == []


# TOTAL AMOUNT


def test_get_total_amount_for_order(
    repository,
    order_data
):
    order = repository.create(order_data)

    total = (
        repository
        .get_total_amount_for_order(
            order.id
        )
    )

    assert total == 300.0


def test_get_total_amount_for_empty_order(
    repository,
    db_session
):
    from app.models import Order

    order = Order(
        status="PENDING",
        customer_name="Test",
        delivery_address="Address",
        total_amount=0
    )

    db_session.add(order)
    db_session.commit()

    total = (
        repository
        .get_total_amount_for_order(
            order.id
        )
    )

    assert total == 0



# TRANSACTION / ROLLBACK


def test_create_order_rollback(
    repository,
    order_data
):
    order_data["items"][0][
        "quantity"
    ] = -1

    with pytest.raises(
        ValueError
    ):
        repository.create(order_data)

    result = (
        repository.find_all_by_status(
            "PENDING"
        )
    )

    assert len(result) == 0



# DELIVERY API SUCCESS


def test_calculate_delivery_cost_success(
    repository,
    order_data,
    httpx_mock
):
    order = repository.create(order_data)

    httpx_mock.add_response(
        status_code=200,
        json={
            "cost": 150.0
        }
    )

    cost = (
        repository
        .calculate_delivery_cost(
            order.id
        )
    )

    assert cost == 150.0

    request = (
        httpx_mock
        .get_requests()[0]
    )

    assert str(request.url) == (
        "https://api.delivery.com/calculate"
    )

# DELIVERY API ERROR


def test_calculate_delivery_cost_error(
    repository,
    order_data,
    httpx_mock
):
    order = repository.create(order_data)

    httpx_mock.add_response(
        status_code=500
    )

    with pytest.raises(
        DeliveryCalculationException
    ):
        repository.calculate_delivery_cost(
            order.id
        )



#DELIVERY ORDER NOT FOUND


def test_calculate_delivery_order_not_found(
    repository
):
    with pytest.raises(
        EntityNotFoundException
    ):
        repository.calculate_delivery_cost(
            999
        )