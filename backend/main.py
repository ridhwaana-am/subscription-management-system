
from datetime import date, timedelta
from calendar import monthrange
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, SessionLocal
from models import Base, Product
from plan_models import SubscriptionPlan
from subscription_models import CustomerSubscription


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Subscription Management System",
    description="Product, Plan and Customer Subscription Management API",
    version="1.0.0"
)


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# REQUEST MODELS
# ==========================================

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    variant: Optional[str] = None


class PlanCreate(BaseModel):
    name: str
    product_id: int
    price: float
    billing_frequency: str
    minimum_quantity: int = 1
    availability_start: Optional[date] = None
    availability_end: Optional[date] = None
    auto_close: bool = False


class SubscriptionCreate(BaseModel):
    customer_name: str
    customer_email: str
    plan_id: int
    quantity: int = 1
    start_date: date


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def add_months(start_date: date, months: int) -> date:
    """
    Add months to a date.
    Handles dates such as January 31.
    """

    month_index = start_date.month - 1 + months

    year = start_date.year + month_index // 12
    month = month_index % 12 + 1

    day = min(
        start_date.day,
        monthrange(year, month)[1]
    )

    return date(year, month, day)


def calculate_end_date(
    start_date: date,
    billing_frequency: str
) -> date:
    """
    Calculate subscription end date using billing frequency.
    """

    frequency = billing_frequency.lower()

    if frequency == "monthly":
        return add_months(start_date, 1)

    elif frequency == "quarterly":
        return add_months(start_date, 3)

    elif frequency == "yearly":
        return add_months(start_date, 12)

    else:
        raise HTTPException(
            status_code=400,
            detail="Billing frequency must be Monthly, Quarterly, or Yearly"
        )


def calculate_status(end_date: Optional[date]) -> str:
    """
    Automatically determine subscription status.
    """

    if end_date is None:
        return "Active"

    today = date.today()

    if end_date < today:
        return "Expired"

    if end_date <= today + timedelta(days=7):
        return "Expiring soon"

    return "Active"


def update_subscription_status(subscription):
    """
    Update status without changing cancelled subscriptions.
    """

    if subscription.status != "Cancelled":
        subscription.status = calculate_status(
            subscription.end_date
        )


# ==========================================
# HOME API
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Subscription Management System API is running"
    }


# ==========================================
# PRODUCT APIs
# ==========================================

@app.post("/products")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        variant=product.variant
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product created successfully",
        "product": new_product
    }


@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    existing_product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_product.name = product.name
    existing_product.description = product.description
    existing_product.price = product.price
    existing_product.variant = product.variant

    db.commit()
    db.refresh(existing_product)

    return {
        "message": "Product updated successfully",
        "product": existing_product
    }


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    existing_product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if existing_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(existing_product)
    db.commit()

    return {
        "message": "Product deleted successfully"
    }


# ==========================================
# SUBSCRIPTION PLAN APIs
# ==========================================

@app.post("/plans")
def create_plan(
    plan: PlanCreate,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == plan.product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    allowed_frequencies = [
        "Monthly",
        "Quarterly",
        "Yearly"
    ]

    if plan.billing_frequency not in allowed_frequencies:
        raise HTTPException(
            status_code=400,
            detail="Billing frequency must be Monthly, Quarterly, or Yearly"
        )

    new_plan = SubscriptionPlan(
        name=plan.name,
        product_id=plan.product_id,
        price=plan.price,
        billing_frequency=plan.billing_frequency,
        minimum_quantity=plan.minimum_quantity,
        availability_start=plan.availability_start,
        availability_end=plan.availability_end,
        auto_close=plan.auto_close
    )

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return {
        "message": "Subscription plan created successfully",
        "plan": new_plan
    }


@app.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    return db.query(SubscriptionPlan).all()


@app.get("/plans/{plan_id}")
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found"
        )

    return plan


@app.put("/plans/{plan_id}")
def update_plan(
    plan_id: int,
    plan: PlanCreate,
    db: Session = Depends(get_db)
):
    existing_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()

    if existing_plan is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found"
        )

    product = db.query(Product).filter(
        Product.id == plan.product_id
    ).first()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    existing_plan.name = plan.name
    existing_plan.product_id = plan.product_id
    existing_plan.price = plan.price
    existing_plan.billing_frequency = plan.billing_frequency
    existing_plan.minimum_quantity = plan.minimum_quantity
    existing_plan.availability_start = plan.availability_start
    existing_plan.availability_end = plan.availability_end
    existing_plan.auto_close = plan.auto_close

    db.commit()
    db.refresh(existing_plan)

    return {
        "message": "Subscription plan updated successfully",
        "plan": existing_plan
    }


@app.delete("/plans/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    existing_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == plan_id
    ).first()

    if existing_plan is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found"
        )

    db.delete(existing_plan)
    db.commit()

    return {
        "message": "Subscription plan deleted successfully"
    }


# ==========================================
# CUSTOMER SUBSCRIPTION APIs
# ==========================================

# CREATE SUBSCRIPTION

@app.post("/subscriptions")
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == subscription.plan_id
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found"
        )

    if subscription.quantity < plan.minimum_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum quantity for this plan is {plan.minimum_quantity}"
        )

    # Calculate subscription end date
    end_date = calculate_end_date(
        subscription.start_date,
        plan.billing_frequency
    )

    # Calculate subscription price
    total_price = plan.price * subscription.quantity

    # Calculate subscription status
    status = calculate_status(end_date)

    new_subscription = CustomerSubscription(
        customer_name=subscription.customer_name,
        customer_email=subscription.customer_email,
        plan_id=subscription.plan_id,
        quantity=subscription.quantity,
        start_date=subscription.start_date,
        end_date=end_date,
        status=status,
        total_price=total_price
    )

    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return {
        "message": "Customer subscription created successfully",
        "subscription": {
            "id": new_subscription.id,
            "customer_name": new_subscription.customer_name,
            "customer_email": new_subscription.customer_email,
            "plan_id": new_subscription.plan_id,
            "quantity": new_subscription.quantity,
            "start_date": new_subscription.start_date,
            "end_date": new_subscription.end_date,
            "status": new_subscription.status,
            "total_price": new_subscription.total_price
        }
    }


# GET ALL SUBSCRIPTIONS

@app.get("/subscriptions")
def get_subscriptions(db: Session = Depends(get_db)):
    subscriptions = db.query(CustomerSubscription).all()

    result = []

    for subscription in subscriptions:
        update_subscription_status(subscription)

        result.append({
            "id": subscription.id,
            "customer_name": subscription.customer_name,
            "customer_email": subscription.customer_email,
            "plan_id": subscription.plan_id,
            "quantity": subscription.quantity,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "status": subscription.status,
            "total_price": subscription.total_price
        })

    db.commit()

    return result


# GET SUBSCRIPTION BY ID

@app.get("/subscriptions/{subscription_id}")
def get_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = db.query(CustomerSubscription).filter(
        CustomerSubscription.id == subscription_id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    update_subscription_status(subscription)

    db.commit()
    db.refresh(subscription)

    return {
        "id": subscription.id,
        "customer_name": subscription.customer_name,
        "customer_email": subscription.customer_email,
        "plan_id": subscription.plan_id,
        "quantity": subscription.quantity,
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "status": subscription.status,
        "total_price": subscription.total_price
    }


# UPDATE SUBSCRIPTION

@app.put("/subscriptions/{subscription_id}")
def update_subscription(
    subscription_id: int,
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    existing_subscription = db.query(CustomerSubscription).filter(
        CustomerSubscription.id == subscription_id
    ).first()

    if existing_subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.id == subscription.plan_id
    ).first()

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found"
        )

    if subscription.quantity < plan.minimum_quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Minimum quantity for this plan is {plan.minimum_quantity}"
        )

    # Recalculate end date and price
    end_date = calculate_end_date(
        subscription.start_date,
        plan.billing_frequency
    )

    total_price = plan.price * subscription.quantity

    existing_subscription.customer_name = subscription.customer_name
    existing_subscription.customer_email = subscription.customer_email
    existing_subscription.plan_id = subscription.plan_id
    existing_subscription.quantity = subscription.quantity
    existing_subscription.start_date = subscription.start_date
    existing_subscription.end_date = end_date
    existing_subscription.total_price = total_price
    existing_subscription.status = calculate_status(end_date)

    db.commit()
    db.refresh(existing_subscription)

    return {
        "message": "Subscription updated successfully",
        "subscription": {
            "id": existing_subscription.id,
            "customer_name": existing_subscription.customer_name,
            "customer_email": existing_subscription.customer_email,
            "plan_id": existing_subscription.plan_id,
            "quantity": existing_subscription.quantity,
            "start_date": existing_subscription.start_date,
            "end_date": existing_subscription.end_date,
            "status": existing_subscription.status,
            "total_price": existing_subscription.total_price
        }
    }


# CANCEL SUBSCRIPTION

@app.put("/subscriptions/{subscription_id}/cancel")
def cancel_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = db.query(CustomerSubscription).filter(
        CustomerSubscription.id == subscription_id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    subscription.status = "Cancelled"

    db.commit()
    db.refresh(subscription)

    return {
        "message": "Subscription cancelled successfully",
        "subscription": {
            "id": subscription.id,
            "customer_name": subscription.customer_name,
            "customer_email": subscription.customer_email,
            "plan_id": subscription.plan_id,
            "quantity": subscription.quantity,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "status": subscription.status,
            "total_price": subscription.total_price
        }
    }


# DELETE SUBSCRIPTION

@app.delete("/subscriptions/{subscription_id}")
def delete_subscription(
    subscription_id: int,
    db: Session = Depends(get_db)
):
    subscription = db.query(CustomerSubscription).filter(
        CustomerSubscription.id == subscription_id
    ).first()

    if subscription is None:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found"
        )

    db.delete(subscription)
    db.commit()

    return {
        "message": "Subscription deleted successfully"
    }

