
from datetime import date, timedelta
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import SessionLocal
from subscription_models import CustomerSubscription
from plan_models import SubscriptionPlan

router = APIRouter(prefix="/analytics", tags=["Subscription Analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1. SUBSCRIPTION SUMMARY
@router.get("/summary")
def subscription_summary(db: Session = Depends(get_db)):
    today = date.today()

    subscriptions = db.query(CustomerSubscription).all()

    total = len(subscriptions)
    active = sum(1 for s in subscriptions if s.status == "Active")
    cancelled = sum(1 for s in subscriptions if s.status == "Cancelled")
    expired = sum(
        1 for s in subscriptions
        if s.end_date and s.end_date < today
        and s.status == "Active"
    )

    expiring = sum(
        1 for s in subscriptions
        if s.status == "Active"
        and s.end_date
        and today <= s.end_date <= today + timedelta(days=7)
    )

    revenue = sum(s.total_price or 0 for s in subscriptions)

    return {
        "total_subscriptions": total,
        "active_subscriptions": active,
        "cancelled_subscriptions": cancelled,
        "expired_subscriptions": expired,
        "expiring_within_7_days": expiring,
        "recorded_subscription_value": round(revenue, 2)
    }


# 2. REVENUE ANALYSIS
@router.get("/revenue")
def revenue_analysis(db: Session = Depends(get_db)):
    result = db.query(
        func.sum(CustomerSubscription.total_price)
    ).scalar()

    return {
        "total_recorded_revenue": round(result or 0, 2)
    }


# 3. POPULAR SUBSCRIPTION PLANS
@router.get("/plans")
def popular_plans(db: Session = Depends(get_db)):
    results = (
        db.query(
            SubscriptionPlan.name,
            func.count(CustomerSubscription.id).label("subscribers")
        )
        .outerjoin(
            CustomerSubscription,
            CustomerSubscription.plan_id == SubscriptionPlan.id
        )
        .group_by(SubscriptionPlan.id, SubscriptionPlan.name)
        .order_by(func.count(CustomerSubscription.id).desc())
        .all()
    )

    return [
        {"plan_name": name, "subscriber_count": count}
        for name, count in results
    ]


# 4. MONTHLY SUBSCRIPTION TRENDS
@router.get("/trends")
def subscription_trends(db: Session = Depends(get_db)):
    results = (
        db.query(
            func.strftime("%Y-%m", CustomerSubscription.start_date),
            func.count(CustomerSubscription.id)
        )
        .group_by(
            func.strftime("%Y-%m", CustomerSubscription.start_date)
        )
        .order_by(
            func.strftime("%Y-%m", CustomerSubscription.start_date)
        )
        .all()
    )

    return [
        {"month": month, "subscriptions": count}
        for month, count in results
    ]


# 5. SUBSCRIPTIONS EXPIRING SOON
@router.get("/expiring")
def expiring_subscriptions(db: Session = Depends(get_db)):
    today = date.today()
    deadline = today + timedelta(days=7)

    results = (
        db.query(CustomerSubscription)
        .filter(
            CustomerSubscription.status == "Active",
            CustomerSubscription.end_date >= today,
            CustomerSubscription.end_date <= deadline
        )
        .all()
    )

    return [
        {
            "customer_name": s.customer_name,
            "customer_email": s.customer_email,
            "end_date": s.end_date,
            "total_price": s.total_price
        }
        for s in results
    ]
