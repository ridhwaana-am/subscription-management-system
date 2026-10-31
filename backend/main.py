from datetime import date
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import engine, SessionLocal
from models import Base, Product
from plan_models import SubscriptionPlan
from subscription_models import CustomerSubscription


# Create database tables
Base.metadata.create_all(bind=engine)


# FastAPI application
app = FastAPI(
    title="Subscription Management System",
    description="Product, Plan and Customer Subscription Management API",
    version="1.0.0"
)


# Database connection
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

# CREATE CUSTOMER SUBSCRIPTION
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

    total_price = plan.price * subscription.quantity

    new_subscription = CustomerSubscription(
        customer_name=subscription.customer_name,
        customer_email=subscription.customer_email,
        plan_id=subscription.plan_id,
        quantity=subscription.quantity,
        start_date=subscription.start_date,
        status="Active",
        total_price=total_price
    )

    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return {
        "message": "Customer subscription created successfully",
        "subscription": new_subscription
    }


# GET ALL CUSTOMER SUBSCRIPTIONS
@app.get("/subscriptions")
def get_subscriptions(db: Session = Depends(get_db)):
    return db.query(CustomerSubscription).all()


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

    return subscription


# CANCEL CUSTOMER SUBSCRIPTION
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
        "subscription": subscription
    }