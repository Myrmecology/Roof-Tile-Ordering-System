# ============================================================
# ROOF TILE ORDERING SYSTEM — Customers Router
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app import crud
from app.schemas import (
    CustomerOut,
    CustomerCreate,
    CustomerUpdate,
    OrderOut
)

router = APIRouter()


# ============================================================
# GET ALL CUSTOMERS
# ============================================================
@router.get("/", response_model=List[CustomerOut])
async def get_customers(
    skip:  int          = 0,
    limit: int          = 100,
    db:    AsyncSession = Depends(get_db)
):
    """Retrieve all customers ordered by most recent first."""
    customers = await crud.get_customers(db, skip=skip, limit=limit)
    return customers


# ============================================================
# GET SINGLE CUSTOMER
# ============================================================
@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: int,
    db:          AsyncSession = Depends(get_db)
):
    """Retrieve a single customer by ID."""
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer ID {customer_id} not found."
        )
    return customer


# ============================================================
# GET CUSTOMER ORDER HISTORY
# ============================================================
@router.get("/{customer_id}/orders", response_model=List[OrderOut])
async def get_customer_orders(
    customer_id: int,
    skip:        int          = 0,
    limit:       int          = 50,
    db:          AsyncSession = Depends(get_db)
):
    """
    Retrieve all orders placed by a specific customer.
    Useful for the customer history panel on the dashboard.
    """
    customer = await crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer ID {customer_id} not found."
        )
    orders = await crud.get_orders(db, skip=skip, limit=limit)
    customer_orders = [
        o for o in orders if o.customer_id == customer_id
    ]
    return customer_orders


# ============================================================
# GET TOP CUSTOMERS
# ============================================================
@router.get("/stats/top-spenders", response_model=List[CustomerOut])
async def get_top_customers(
    limit: int          = 10,
    db:    AsyncSession = Depends(get_db)
):
    """
    Retrieve the highest spending customers
    ranked by total amount spent.
    """
    customers = await crud.get_top_customers(db, limit=limit)
    return customers


# ============================================================
# CREATE CUSTOMER
# ============================================================
@router.post(
    "/",
    response_model=CustomerOut,
    status_code=status.HTTP_201_CREATED
)
async def create_customer(
    data: CustomerCreate,
    db:   AsyncSession = Depends(get_db)
):
    """
    Manually create a new customer.
    Returns 400 if the email address is already registered.
    """
    existing = await crud.get_customer_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A customer with email '{data.email}' already exists."
        )
    customer = await crud.create_customer(db, data)
    return customer


# ============================================================
# UPDATE CUSTOMER
# ============================================================
@router.patch("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: int,
    data:        CustomerUpdate,
    db:          AsyncSession = Depends(get_db)
):
    """Update an existing customer's contact information."""
    customer = await crud.update_customer(db, customer_id, data)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer ID {customer_id} not found."
        )
    return customer


# ============================================================
# GET CUSTOMER STATS SUMMARY
# ============================================================
@router.get("/stats/summary")
async def get_customer_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Return a high level summary of customer data
    for the dashboard analytics panel.
    """
    from sqlalchemy import select, func
    from app.models import Customer, Order, OrderStatus

    total_result = await db.execute(select(func.count(Customer.id)))
    total_customers = total_result.scalar() or 0

    company_result = await db.execute(
        select(func.count(Customer.id))
        .where(Customer.customer_type == "company")
    )
    total_companies = company_result.scalar() or 0

    individual_result = await db.execute(
        select(func.count(Customer.id))
        .where(Customer.customer_type == "individual")
    )
    total_individuals = individual_result.scalar() or 0

    top_spenders = await crud.get_top_customers(db, limit=5)

    return {
        "total_customers":   total_customers,
        "total_companies":   total_companies,
        "total_individuals": total_individuals,
        "top_spenders": [
            {
                "id":           c.id,
                "name":         c.name,
                "company_name": c.company_name,
                "customer_type": c.customer_type,
                "total_spent":  c.total_spent,
                "order_count":  c.order_count
            }
            for c in top_spenders
        ]
    }