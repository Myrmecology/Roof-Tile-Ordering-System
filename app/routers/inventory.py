# ============================================================
# ROOF TILE ORDERING SYSTEM — Inventory Router
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.websocket_manager import manager
from app import crud
from app.schemas import (
    InventoryItemOut,
    InventoryItemCreate,
    InventoryItemUpdate,
    RestockOrderCreate,
    RestockOrderOut
)

router = APIRouter()


# ============================================================
# GET ALL INVENTORY
# ============================================================
@router.get("/", response_model=List[InventoryItemOut])
async def get_inventory(
    skip:  int          = 0,
    limit: int          = 100,
    db:    AsyncSession = Depends(get_db)
):
    """Retrieve all active inventory items."""
    items = await crud.get_inventory(db, skip=skip, limit=limit)
    return items


# ============================================================
# GET SINGLE INVENTORY ITEM
# ============================================================
@router.get("/{item_id}", response_model=InventoryItemOut)
async def get_inventory_item(
    item_id: int,
    db:      AsyncSession = Depends(get_db)
):
    """Retrieve a single inventory item by ID."""
    item = await crud.get_inventory_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item ID {item_id} not found."
        )
    return item


# ============================================================
# GET LOW STOCK ITEMS
# ============================================================
@router.get("/alerts/low-stock", response_model=List[InventoryItemOut])
async def get_low_stock(
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all inventory items at or below their reorder point."""
    items = await crud.get_low_stock_items(db)
    return items


# ============================================================
# GET TOP SELLERS
# ============================================================
@router.get("/stats/top-sellers", response_model=List[InventoryItemOut])
async def get_top_sellers(
    limit: int          = 5,
    db:    AsyncSession = Depends(get_db)
):
    """Retrieve the best selling inventory items by total units sold."""
    items = await crud.get_top_sellers(db, limit=limit)
    return items


# ============================================================
# GET SLOWEST SELLERS
# ============================================================
@router.get("/stats/slowest-sellers", response_model=List[InventoryItemOut])
async def get_slowest_sellers(
    limit: int          = 5,
    db:    AsyncSession = Depends(get_db)
):
    """Retrieve the slowest moving inventory items by total units sold."""
    items = await crud.get_slowest_sellers(db, limit=limit)
    return items


# ============================================================
# CREATE INVENTORY ITEM
# ============================================================
@router.post("/", response_model=InventoryItemOut, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    data: InventoryItemCreate,
    db:   AsyncSession = Depends(get_db)
):
    """Create a new inventory item manually."""
    existing = await crud.get_inventory_item_by_sku(db, data.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An item with SKU '{data.sku}' already exists."
        )
    item = await crud.create_inventory_item(db, data)
    return item


# ============================================================
# UPDATE INVENTORY ITEM
# ============================================================
@router.patch("/{item_id}", response_model=InventoryItemOut)
async def update_inventory_item(
    item_id: int,
    data:    InventoryItemUpdate,
    db:      AsyncSession = Depends(get_db)
):
    """
    Update an inventory item's quantity, price,
    or reorder settings.
    Broadcasts a low stock alert if quantity
    drops at or below the reorder point.
    """
    item = await crud.update_inventory_item(db, item_id, data)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item ID {item_id} not found."
        )

    # Broadcast low stock alert if threshold crossed
    if item.quantity <= item.reorder_point:
        await manager.broadcast_low_stock({
            "item_id":       item.id,
            "name":          item.name,
            "sku":           item.sku,
            "quantity":      item.quantity,
            "reorder_point": item.reorder_point
        })

    return item


# ============================================================
# PLACE A RESTOCK ORDER
# ============================================================
@router.post("/restock", response_model=RestockOrderOut, status_code=status.HTTP_201_CREATED)
async def place_restock_order(
    data: RestockOrderCreate,
    db:   AsyncSession = Depends(get_db)
):
    """
    Place a restock order to replenish inventory.
    Instantly adds stock, deducts cost from budget,
    and broadcasts the event to all WebSocket clients.
    """
    # Verify budget can cover the restock
    budget = await crud.get_budget(db)
    total_cost = sum(
        item.quantity_ordered * item.unit_cost
        for item in data.items
    )

    if budget.balance < total_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient budget. "
                   f"Required: ${total_cost:,.2f} — "
                   f"Available: ${budget.balance:,.2f}"
        )

    restock = await crud.create_restock_order(db, data)

    # Get refreshed budget after deduction
    updated_budget = await crud.get_budget(db)

    # Broadcast restock placed event
    await manager.broadcast_restock_placed({
        "restock_id":    restock.id,
        "order_number":  restock.order_number,
        "total_cost":    restock.total_cost,
        "item_count":    len(restock.items),
        "status":        restock.status
    })

    # Broadcast updated budget
    await manager.broadcast_budget_update({
        "balance":      updated_budget.balance,
        "total_earned": updated_budget.total_earned,
        "total_profit": updated_budget.total_profit
    })

    return restock


# ============================================================
# GET ALL RESTOCK ORDERS
# ============================================================
@router.get("/restock/history", response_model=List[RestockOrderOut])
async def get_restock_history(
    skip:  int          = 0,
    limit: int          = 50,
    db:    AsyncSession = Depends(get_db)
):
    """Retrieve the full history of all restock orders placed."""
    restocks = await crud.get_restock_orders(db, skip=skip, limit=limit)
    return restocks