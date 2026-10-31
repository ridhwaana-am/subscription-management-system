from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from database import Base


class CustomerSubscription(Base):
    __tablename__ = "customer_subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100), nullable=False)

    plan_id = Column(
        Integer,
        ForeignKey("subscription_plans.id"),
        nullable=False
    )

    quantity = Column(Integer, default=1)

    start_date = Column(Date, nullable=False)

    end_date = Column(Date, nullable=True)

    status = Column(String(20), default="Active")

    total_price = Column(Float, nullable=False)