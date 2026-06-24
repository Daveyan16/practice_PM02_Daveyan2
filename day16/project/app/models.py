from datetime import datetime

from sqlalchemy import (
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    customer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    delivery_address: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    total_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan"
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id")
    )

    product_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    order: Mapped["Order"] = relationship(
        back_populates="items"
    )