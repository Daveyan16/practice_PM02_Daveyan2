from datetime import datetime

import httpx

from sqlalchemy import (
    select,
    func
)

from app.models import (
    Order,
    OrderItem
)

from app.exceptions import (
    EntityNotFoundException,
    DeliveryCalculationException
)


class OrderRepository:

    VALID_STATUSES = {
        "PENDING",
        "PAID",
        "SHIPPED",
        "CANCELLED"
    }

    def __init__(self, session):
        self.session = session

    def create(self, order_data: dict) -> Order:

        try:

            order = Order(
                status=order_data["status"],
                customer_name=order_data["customer_name"],
                delivery_address=order_data["delivery_address"],
                total_amount=order_data["total_amount"]
            )

            for item in order_data["items"]:

                if item["quantity"] <= 0:
                    raise ValueError(
                        "Quantity must be positive"
                    )

                order.items.append(
                    OrderItem(
                        product_name=item["product_name"],
                        quantity=item["quantity"],
                        price=item["price"]
                    )
                )

            self.session.add(order)
            self.session.commit()
            self.session.refresh(order)

            return order

        except Exception:
            self.session.rollback()
            raise

    def find_by_id(
        self,
        order_id: int
    ) -> Order | None:

        return self.session.get(
            Order,
            order_id
        )

    def find_all_by_status(
        self,
        status: str
    ):

        stmt = (
            select(Order)
            .where(Order.status == status)
        )

        return self.session.scalars(stmt).all()

    def update_status(
        self,
        order_id: int,
        new_status: str
    ) -> Order:

        order = self.find_by_id(order_id)

        if not order:
            raise EntityNotFoundException()

        order.status = new_status

        self.session.commit()
        self.session.refresh(order)

        return order

    def delete(
        self,
        order_id: int
    ) -> None:

        order = self.find_by_id(order_id)

        if not order:
            raise EntityNotFoundException()

        self.session.delete(order)
        self.session.commit()

    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ):

        stmt = (
            select(Order)
            .where(
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        )

        return self.session.scalars(stmt).all()

    def get_total_amount_for_order(
        self,
        order_id: int
    ) -> float:

        total = self.session.scalar(
            select(
                func.sum(
                    OrderItem.quantity *
                    OrderItem.price
                )
            )
            .where(
                OrderItem.order_id == order_id
            )
        )

        return float(total or 0)

    def calculate_delivery_cost(
        self,
        order_id: int
    ) -> float:

        order = self.find_by_id(order_id)

        if not order:
            raise EntityNotFoundException()

        weight = sum(
            item.quantity * 0.5
            for item in order.items
        )

        response = httpx.post(
            "https://api.delivery.com/calculate",
            json={
                "address": order.delivery_address,
                "weight": weight
            }
        )

        if response.status_code >= 400:
            raise DeliveryCalculationException()

        return response.json()["cost"]