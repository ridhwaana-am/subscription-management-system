from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False)

    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False
    )

    price = Column(Float, nullable=False)

    billing_frequency = Column(
        String(20),
        nullable=False
    )

    minimum_quantity = Column(
        Integer,
        default=1
    )

    availability_start = Column(
        Date,
        nullable=True
    )

    availability_end = Column(
        Date,
        nullable=True
    )

    auto_close = Column(
        Boolean,
        default=False
    )