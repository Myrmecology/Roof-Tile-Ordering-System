# ============================================================
# ROOF TILE ORDERING SYSTEM — Orders Router
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.websocket_manager import manager
from app import crud
from app.schemas import OrderOut, OrderUpdate

router = APIRouter()


# ============================================================
# GET ALL ORDERS
# ============================================================
@router.get("/", response_model=List[OrderOut])
async def get_orders(
    skip:   int            = 0,
    limit:  int            = 50,
    status: Optional[str]  = None,
    db:     AsyncSession   = Depends(get_db)
):
    """Retrieve all orders with optional status filter."""
    orders = await crud.get_orders(db, skip=skip, limit=limit, status=status)
    return orders


# ============================================================
# GET SINGLE ORDER
# ============================================================
@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db:       AsyncSession = Depends(get_db)
):
    """Retrieve a single order by ID."""
    order = await crud.get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order ID {order_id} not found."
        )
    return order


# ============================================================
# GET PENDING ORDERS
# ============================================================
@router.get("/status/pending", response_model=List[OrderOut])
async def get_pending_orders(
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all orders currently awaiting fulfillment."""
    orders = await crud.get_pending_orders(db)
    return orders


# ============================================================
# FULFILL AN ORDER
# ============================================================
@router.post("/{order_id}/fulfill", response_model=OrderOut)
async def fulfill_order(
    order_id: int,
    db:       AsyncSession = Depends(get_db)
):
    """
    Fulfill a pending order.
    Deducts inventory, records profit, updates budget,
    and broadcasts the event to all WebSocket clients.
    """
    order = await crud.fulfill_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order ID {order_id} could not be fulfilled. "
                   f"It may not exist or is not in PENDING status."
        )

    # Get updated budget to broadcast
    budget = await crud.get_budget(db)

    # Broadcast fulfillment event to all live clients
    await manager.broadcast_order_fulfilled({
        "order_id":     order.id,
        "order_number": order.order_number,
        "total_amount": order.total_amount,
        "profit":       order.profit,
        "status":       order.status,
        "fulfilled_at": order.fulfilled_at.isoformat()
            if order.fulfilled_at else None
    })

    # Broadcast updated budget
    await manager.broadcast_budget_update({
        "balance":      budget.balance,
        "total_earned": budget.total_earned,
        "total_profit": budget.total_profit
    })

    # Check for any low stock items and alert if needed
    low_stock = await crud.get_low_stock_items(db)
    for item in low_stock:
        await manager.broadcast_low_stock({
            "item_id":  item.id,
            "name":     item.name,
            "sku":      item.sku,
            "quantity": item.quantity,
            "reorder_point": item.reorder_point
        })

    return order


# ============================================================
# CANCEL AN ORDER
# ============================================================
@router.post("/{order_id}/cancel", response_model=OrderOut)
async def cancel_order(
    order_id: int,
    db:       AsyncSession = Depends(get_db)
):
    """
    Cancel a pending order.
    Broadcasts the cancellation to all WebSocket clients.
    """
    order = await crud.cancel_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order ID {order_id} could not be cancelled. "
                   f"It may not exist or is not in PENDING status."
        )

    # Broadcast cancellation to all live clients
    await manager.broadcast_order_cancelled({
        "order_id":     order.id,
        "order_number": order.order_number,
        "status":       order.status
    })

    return order


# ============================================================
# GET ORDER COUNT BY STATUS
# ============================================================
@router.get("/stats/counts")
async def get_order_counts(
    db: AsyncSession = Depends(get_db)
):
    """Return order counts grouped by status."""
    counts = await crud.get_orders_count_by_status(db)
    return counts