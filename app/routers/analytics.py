# ============================================================
# ROOF TILE ORDERING SYSTEM — Analytics Router
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List
from app.database import get_db
from app import crud
from app.models import Order, OrderItem, InventoryItem, Transaction, OrderStatus
from app.schemas import (
    AnalyticsSummaryOut,
    TransactionOut,
    BudgetOut,
    TopSellerOut,
    SlowestSellerOut
)

router = APIRouter()


# ============================================================
# GET FULL ANALYTICS SUMMARY
# ============================================================
@router.get("/summary", response_model=AnalyticsSummaryOut)
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a complete analytics snapshot including
    order counts, revenue, profit, top sellers
    and slowest moving items.
    """
    summary = await crud.get_analytics_summary(db)

    top_sellers = [
        TopSellerOut(
            item_name=item.name,
            sku=item.sku,
            total_sold=item.total_sold,
            total_revenue=item.total_revenue
        )
        for item in summary["top_sellers"]
    ]

    slowest_sellers = [
        SlowestSellerOut(
            item_name=item.name,
            sku=item.sku,
            total_sold=item.total_sold,
            quantity=item.quantity
        )
        for item in summary["slowest_sellers"]
    ]

    return AnalyticsSummaryOut(
        total_orders=summary["total_orders"],
        pending_orders=summary["pending_orders"],
        fulfilled_orders=summary["fulfilled_orders"],
        total_revenue=summary["total_revenue"],
        total_profit=summary["total_profit"],
        top_sellers=top_sellers,
        slowest_sellers=slowest_sellers
    )


# ============================================================
# GET BUDGET OVERVIEW
# ============================================================
@router.get("/budget", response_model=BudgetOut)
async def get_budget(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns the current budget state including
    balance, total earned, total spent and net profit.
    """
    budget = await crud.get_budget(db)
    return budget


# ============================================================
# GET TRANSACTION HISTORY
# ============================================================
@router.get("/transactions", response_model=List[TransactionOut])
async def get_transactions(
    skip:  int          = 0,
    limit: int          = 50,
    db:    AsyncSession = Depends(get_db)
):
    """
    Returns a paginated list of all financial transactions
    — both sales and restock orders — newest first.
    """
    transactions = await crud.get_transactions(db, skip=skip, limit=limit)
    return transactions


# ============================================================
# GET REVENUE BY CATEGORY
# ============================================================
@router.get("/revenue-by-category")
async def get_revenue_by_category(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns total revenue broken down by supply category.
    Powers the category revenue chart on the analytics page.
    """
    result = await db.execute(
        select(
            InventoryItem.category,
            func.sum(InventoryItem.total_revenue).label("total_revenue"),
            func.sum(InventoryItem.total_sold).label("total_sold")
        )
        .where(InventoryItem.is_active == True)
        .group_by(InventoryItem.category)
        .order_by(desc("total_revenue"))
    )
    rows = result.all()
    return [
        {
            "category":      row.category,
            "total_revenue": round(row.total_revenue or 0.0, 2),
            "total_sold":    row.total_sold or 0
        }
        for row in rows
    ]


# ============================================================
# GET DAILY ORDER VOLUME
# ============================================================
@router.get("/daily-volume")
async def get_daily_order_volume(
    days: int           = 7,
    db:   AsyncSession  = Depends(get_db)
):
    """
    Returns order counts and revenue per day
    for the last N days. Powers the daily
    volume trend chart on the analytics page.
    """
    result = await db.execute(
        select(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("order_count"),
            func.sum(Order.total_amount).label("revenue")
        )
        .where(Order.status == OrderStatus.FULFILLED)
        .group_by(func.date(Order.created_at))
        .order_by(desc("date"))
        .limit(days)
    )
    rows = result.all()
    return [
        {
            "date":        str(row.date),
            "order_count": row.order_count or 0,
            "revenue":     round(row.revenue or 0.0, 2)
        }
        for row in rows
    ]


# ============================================================
# GET PROFIT MARGIN BY ITEM
# ============================================================
@router.get("/profit-margins")
async def get_profit_margins(
    db: AsyncSession = Depends(get_db)
):
    """
    Returns profit margin percentage for every
    active inventory item. Powers the margin
    breakdown chart on the analytics page.
    """
    result = await db.execute(
        select(InventoryItem)
        .where(
            InventoryItem.is_active == True,
            InventoryItem.total_sold > 0
        )
        .order_by(desc(InventoryItem.total_revenue))
    )
    items = result.scalars().all()

    margins = []
    for item in items:
        revenue = item.total_revenue or 0.0
        cost    = item.total_sold * item.cost_price
        profit  = revenue - cost
        margin  = (profit / revenue * 100) if revenue > 0 else 0.0
        margins.append({
            "item_name":     item.name,
            "sku":           item.sku,
            "category":      item.category,
            "total_sold":    item.total_sold,
            "total_revenue": round(revenue, 2),
            "total_cost":    round(cost, 2),
            "total_profit":  round(profit, 2),
            "margin_pct":    round(margin, 1)
        })

    return margins


# ============================================================
# GET DASHBOARD SUMMARY
# ============================================================
@router.get("/dashboard")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Single endpoint that powers the entire
    dashboard header — budget, pending orders,
    fulfilled today, low stock count
    and total customers.
    """
    summary = await crud.get_dashboard_summary(db)
    budget  = summary["budget"]
    return {
        "balance":         round(budget.balance, 2),
        "total_earned":    round(budget.total_earned, 2),
        "total_spent":     round(budget.total_spent, 2),
        "total_profit":    round(budget.total_profit, 2),
        "pending_orders":  summary["pending_orders"],
        "fulfilled_today": summary["fulfilled_today"],
        "low_stock_items": summary["low_stock_items"],
        "total_customers": summary["total_customers"]
    }