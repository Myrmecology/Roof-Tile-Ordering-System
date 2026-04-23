# ============================================================
# ROOF TILE ORDERING SYSTEM — CRUD Operations
# ============================================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import Optional, List
from app.models import (
    Customer, InventoryItem, Order, OrderItem,
    RestockOrder, RestockItem, Transaction, Budget,
    OrderStatus
)
from app.schemas import (
    CustomerCreate, CustomerUpdate,
    InventoryItemCreate, InventoryItemUpdate,
    OrderCreate, OrderUpdate,
    RestockOrderCreate
)
import os


# ============================================================
# UTILITY HELPERS
# ============================================================
def utcnow():
    return datetime.now(timezone.utc)

async def generate_order_number(db: AsyncSession, prefix: str = "ORD") -> str:
    result = await db.execute(select(func.count(Order.id)))
    count  = result.scalar() or 0
    return f"{prefix}-{str(count + 1).zfill(6)}"

async def generate_restock_number(db: AsyncSession) -> str:
    result = await db.execute(select(func.count(RestockOrder.id)))
    count  = result.scalar() or 0
    return f"RST-{str(count + 1).zfill(6)}"


# ============================================================
# BUDGET CRUD
# ============================================================
async def get_budget(db: AsyncSession) -> Budget:
    result = await db.execute(select(Budget))
    budget = result.scalar_one_or_none()
    if not budget:
        starting = float(os.getenv("STARTING_BUDGET", 50000.00))
        budget   = Budget(balance=starting)
        db.add(budget)
        await db.commit()
        await db.refresh(budget)
    return budget

async def update_budget(
    db: AsyncSession,
    amount: float,
    transaction_type: str,
    description: str,
    reference_id: Optional[int] = None
) -> Budget:
    budget = await get_budget(db)

    if transaction_type == "sale":
        budget.balance      += amount
        budget.total_earned += amount
    elif transaction_type == "restock":
        budget.balance     -= amount
        budget.total_spent += amount
    elif transaction_type == "profit":
        budget.total_profit += amount

    transaction = Transaction(
        transaction_type=transaction_type,
        amount=amount,
        balance_after=budget.balance,
        description=description,
        reference_id=reference_id
    )
    db.add(transaction)
    await db.commit()
    await db.refresh(budget)
    return budget


# ============================================================
# CUSTOMER CRUD
# ============================================================
async def get_customers(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Customer]:
    result = await db.execute(
        select(Customer)
        .order_by(desc(Customer.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_customer(
    db: AsyncSession,
    customer_id: int
) -> Optional[Customer]:
    result = await db.execute(
        select(Customer)
        .options(selectinload(Customer.orders))
        .where(Customer.id == customer_id)
    )
    return result.scalar_one_or_none()

async def get_customer_by_email(
    db: AsyncSession,
    email: str
) -> Optional[Customer]:
    result = await db.execute(
        select(Customer).where(Customer.email == email)
    )
    return result.scalar_one_or_none()

async def create_customer(
    db: AsyncSession,
    data: CustomerCreate
) -> Customer:
    customer = Customer(**data.model_dump())
    db.add(customer)
    await db.commit()
    await db.refresh(customer)
    return customer

async def update_customer(
    db: AsyncSession,
    customer_id: int,
    data: CustomerUpdate
) -> Optional[Customer]:
    customer = await get_customer(db, customer_id)
    if not customer:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    await db.commit()
    await db.refresh(customer)
    return customer

async def get_top_customers(
    db: AsyncSession,
    limit: int = 10
) -> List[Customer]:
    result = await db.execute(
        select(Customer)
        .order_by(desc(Customer.total_spent))
        .limit(limit)
    )
    return result.scalars().all()


# ============================================================
# INVENTORY CRUD
# ============================================================
async def get_inventory(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[InventoryItem]:
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.is_active == True)
        .order_by(InventoryItem.category, InventoryItem.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_inventory_item(
    db: AsyncSession,
    item_id: int
) -> Optional[InventoryItem]:
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.id == item_id)
    )
    return result.scalar_one_or_none()

async def get_inventory_item_by_sku(
    db: AsyncSession,
    sku: str
) -> Optional[InventoryItem]:
    result = await db.execute(
        select(InventoryItem).where(InventoryItem.sku == sku)
    )
    return result.scalar_one_or_none()

async def create_inventory_item(
    db: AsyncSession,
    data: InventoryItemCreate
) -> InventoryItem:
    item = InventoryItem(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

async def update_inventory_item(
    db: AsyncSession,
    item_id: int,
    data: InventoryItemUpdate
) -> Optional[InventoryItem]:
    item = await get_inventory_item(db, item_id)
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item

async def get_low_stock_items(
    db: AsyncSession
) -> List[InventoryItem]:
    result = await db.execute(
        select(InventoryItem)
        .where(
            InventoryItem.is_active == True,
            InventoryItem.quantity  <= InventoryItem.reorder_point
        )
        .order_by(InventoryItem.quantity)
    )
    return result.scalars().all()

async def get_top_sellers(
    db: AsyncSession,
    limit: int = 5
) -> List[InventoryItem]:
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.is_active == True)
        .order_by(desc(InventoryItem.total_sold))
        .limit(limit)
    )
    return result.scalars().all()

async def get_slowest_sellers(
    db: AsyncSession,
    limit: int = 5
) -> List[InventoryItem]:
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.is_active == True)
        .order_by(InventoryItem.total_sold)
        .limit(limit)
    )
    return result.scalars().all()


# ============================================================
# ORDER CRUD
# ============================================================
async def get_orders(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None
) -> List[Order]:
    query = (
        select(Order)
        .options(
            selectinload(Order.customer),
            selectinload(Order.items)
            .selectinload(OrderItem.inventory_item)
        )
        .order_by(desc(Order.created_at))
        .offset(skip)
        .limit(limit)
    )
    if status:
        query = query.where(Order.status == status)
    result = await db.execute(query)
    return result.scalars().all()

async def get_order(
    db: AsyncSession,
    order_id: int
) -> Optional[Order]:
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.customer),
            selectinload(Order.items)
            .selectinload(OrderItem.inventory_item)
        )
        .where(Order.id == order_id)
    )
    return result.scalar_one_or_none()

async def create_order(
    db: AsyncSession,
    data: OrderCreate
) -> Order:
    order_number = await generate_order_number(db)
    order = Order(
        order_number=order_number,
        customer_id=data.customer_id,
        notes=data.notes,
        is_auto_generated=data.is_auto_generated,
        status=OrderStatus.PENDING
    )
    db.add(order)
    await db.flush()

    total_amount = 0.0
    for item_data in data.items:
        line_total = item_data.quantity_ordered * item_data.unit_price
        order_item = OrderItem(
            order_id=order.id,
            inventory_item_id=item_data.inventory_item_id,
            quantity_ordered=item_data.quantity_ordered,
            unit_price=item_data.unit_price,
            line_total=line_total
        )
        db.add(order_item)
        total_amount += line_total

    order.total_amount = total_amount
    await db.commit()
    await db.refresh(order)
    return order

async def fulfill_order(
    db: AsyncSession,
    order_id: int
) -> Optional[Order]:
    order = await get_order(db, order_id)
    if not order or order.status != OrderStatus.PENDING:
        return None

    total_profit = 0.0
    for item in order.items:
        inv = await get_inventory_item(db, item.inventory_item_id)
        if not inv:
            continue

        fulfill_qty       = min(item.quantity_ordered, inv.quantity)
        item.quantity_fulfilled = fulfill_qty
        item.line_total   = fulfill_qty * item.unit_price

        inv.quantity      -= fulfill_qty
        inv.total_sold    += fulfill_qty
        inv.total_revenue += item.line_total

        cost          = fulfill_qty * inv.cost_price
        total_profit += (item.line_total - cost)

    order.status       = OrderStatus.FULFILLED
    order.profit       = total_profit
    order.fulfilled_at = utcnow()

    customer = await get_customer(db, order.customer_id)
    if customer:
        customer.total_spent += order.total_amount
        customer.order_count += 1

    await update_budget(
        db,
        amount=order.total_amount,
        transaction_type="sale",
        description=f"Sale — Order {order.order_number}",
        reference_id=order.id
    )

    await db.commit()
    await db.refresh(order)
    return order

async def cancel_order(
    db: AsyncSession,
    order_id: int
) -> Optional[Order]:
    order = await get_order(db, order_id)
    if not order or order.status != OrderStatus.PENDING:
        return None
    order.status = OrderStatus.CANCELLED
    await db.commit()
    await db.refresh(order)
    return order

async def get_pending_orders(
    db: AsyncSession
) -> List[Order]:
    return await get_orders(db, status=OrderStatus.PENDING)

async def get_orders_count_by_status(
    db: AsyncSession
) -> dict:
    result = await db.execute(
        select(Order.status, func.count(Order.id))
        .group_by(Order.status)
    )
    return {row[0]: row[1] for row in result.all()}


# ============================================================
# RESTOCK CRUD
# ============================================================
async def get_restock_orders(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50
) -> List[RestockOrder]:
    result = await db.execute(
        select(RestockOrder)
        .options(
            selectinload(RestockOrder.items)
            .selectinload(RestockItem.inventory_item)
        )
        .order_by(desc(RestockOrder.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def create_restock_order(
    db: AsyncSession,
    data: RestockOrderCreate
) -> RestockOrder:
    order_number = await generate_restock_number(db)
    restock = RestockOrder(
        order_number=order_number,
        notes=data.notes,
        status="ordered"
    )
    db.add(restock)
    await db.flush()

    total_cost = 0.0
    for item_data in data.items:
        line_total   = item_data.quantity_ordered * item_data.unit_cost
        restock_item = RestockItem(
            restock_order_id=restock.id,
            inventory_item_id=item_data.inventory_item_id,
            quantity_ordered=item_data.quantity_ordered,
            unit_cost=item_data.unit_cost,
            line_total=line_total
        )
        db.add(restock_item)
        total_cost += line_total

    restock.total_cost = total_cost

    for item_data in data.items:
        inv = await get_inventory_item(db, item_data.inventory_item_id)
        if inv:
            inv.quantity += item_data.quantity_ordered

    await update_budget(
        db,
        amount=total_cost,
        transaction_type="restock",
        description=f"Restock — Order {order_number}",
        reference_id=restock.id
    )

    await db.commit()

    # Re-fetch with all relationships eagerly loaded
    result = await db.execute(
        select(RestockOrder)
        .options(
            selectinload(RestockOrder.items)
            .selectinload(RestockItem.inventory_item)
        )
        .where(RestockOrder.id == restock.id)
    )
    return result.scalar_one()


# ============================================================
# ANALYTICS CRUD
# ============================================================
async def get_analytics_summary(db: AsyncSession) -> dict:
    total_orders_result = await db.execute(
        select(func.count(Order.id))
    )
    total_orders = total_orders_result.scalar() or 0

    pending_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.status == OrderStatus.PENDING)
    )
    pending_orders = pending_result.scalar() or 0

    fulfilled_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.status == OrderStatus.FULFILLED)
    )
    fulfilled_orders = fulfilled_result.scalar() or 0

    revenue_result = await db.execute(
        select(func.sum(Order.total_amount))
        .where(Order.status == OrderStatus.FULFILLED)
    )
    total_revenue = revenue_result.scalar() or 0.0

    profit_result = await db.execute(
        select(func.sum(Order.profit))
        .where(Order.status == OrderStatus.FULFILLED)
    )
    total_profit = profit_result.scalar() or 0.0

    top_sellers     = await get_top_sellers(db)
    slowest_sellers = await get_slowest_sellers(db)

    return {
        "total_orders":     total_orders,
        "pending_orders":   pending_orders,
        "fulfilled_orders": fulfilled_orders,
        "total_revenue":    total_revenue,
        "total_profit":     total_profit,
        "top_sellers":      top_sellers,
        "slowest_sellers":  slowest_sellers
    }

async def get_transactions(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50
) -> List[Transaction]:
    result = await db.execute(
        select(Transaction)
        .order_by(desc(Transaction.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_dashboard_summary(db: AsyncSession) -> dict:
    budget = await get_budget(db)

    pending_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.status == OrderStatus.PENDING)
    )
    pending_orders = pending_result.scalar() or 0

    today = datetime.now(timezone.utc).date()
    fulfilled_result = await db.execute(
        select(func.count(Order.id))
        .where(
            Order.status == OrderStatus.FULFILLED,
            func.date(Order.fulfilled_at) == today
        )
    )
    fulfilled_today = fulfilled_result.scalar() or 0

    low_stock = await get_low_stock_items(db)

    customers_result = await db.execute(
        select(func.count(Customer.id))
    )
    total_customers = customers_result.scalar() or 0

    return {
        "budget":          budget,
        "pending_orders":  pending_orders,
        "fulfilled_today": fulfilled_today,
        "low_stock_items": len(low_stock),
        "total_customers": total_customers
    }