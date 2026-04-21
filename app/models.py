# ============================================================
# ROOF TILE ORDERING SYSTEM — Database Models
# ============================================================

from sqlalchemy import (
    Column, Integer, String, Float, Boolean,
    DateTime, Text, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

# ------------------------------------------------------------
# ENUMS
# ------------------------------------------------------------
class OrderStatus(str, enum.Enum):
    PENDING     = "pending"
    FULFILLED   = "fulfilled"
    CANCELLED   = "cancelled"
    BACKORDERED = "backordered"

class CustomerType(str, enum.Enum):
    COMPANY    = "company"
    INDIVIDUAL = "individual"

class SupplyCategory(str, enum.Enum):
    SHINGLES   = "shingles"
    GLOVES     = "gloves"
    TAR        = "tar"
    UNDERLAYMENT = "underlayment"
    NAILS      = "nails"
    TOOLS      = "tools"

# ------------------------------------------------------------
# CUSTOMER MODEL
# ------------------------------------------------------------
class Customer(Base):
    __tablename__ = "customers"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    customer_type = Column(String(20), default=CustomerType.INDIVIDUAL)
    company_name  = Column(String(150), nullable=True)
    email         = Column(String(120), unique=True, index=True)
    phone         = Column(String(30), nullable=True)
    address       = Column(String(255), nullable=True)
    city          = Column(String(100), nullable=True)
    state         = Column(String(50), nullable=True)
    total_spent   = Column(Float, default=0.0)
    order_count   = Column(Integer, default=0)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    orders = relationship("Order", back_populates="customer")


# ------------------------------------------------------------
# INVENTORY MODEL
# ------------------------------------------------------------
class InventoryItem(Base):
    __tablename__ = "inventory"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(150), nullable=False, unique=True)
    sku             = Column(String(50), unique=True, index=True)
    category        = Column(String(50), nullable=False)
    description     = Column(Text, nullable=True)
    unit            = Column(String(30), nullable=False)
    quantity        = Column(Integer, default=0)
    reorder_point   = Column(Integer, default=10)
    reorder_quantity= Column(Integer, default=50)
    cost_price      = Column(Float, nullable=False)
    sell_price      = Column(Float, nullable=False)
    total_sold      = Column(Integer, default=0)
    total_revenue   = Column(Float, default=0.0)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    order_items = relationship("OrderItem", back_populates="inventory_item")
    restock_items = relationship("RestockItem", back_populates="inventory_item")


# ------------------------------------------------------------
# ORDER MODEL
# ------------------------------------------------------------
class Order(Base):
    __tablename__ = "orders"

    id              = Column(Integer, primary_key=True, index=True)
    order_number    = Column(String(20), unique=True, index=True)
    customer_id     = Column(Integer, ForeignKey("customers.id"))
    status          = Column(String(20), default=OrderStatus.PENDING)
    total_amount    = Column(Float, default=0.0)
    profit          = Column(Float, default=0.0)
    notes           = Column(Text, nullable=True)
    is_auto_generated = Column(Boolean, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    fulfilled_at    = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer  = relationship("Customer", back_populates="orders")
    items     = relationship("OrderItem", back_populates="order")


# ------------------------------------------------------------
# ORDER ITEM MODEL
# ------------------------------------------------------------
class OrderItem(Base):
    __tablename__ = "order_items"

    id                  = Column(Integer, primary_key=True, index=True)
    order_id            = Column(Integer, ForeignKey("orders.id"))
    inventory_item_id   = Column(Integer, ForeignKey("inventory.id"))
    quantity_ordered    = Column(Integer, nullable=False)
    quantity_fulfilled  = Column(Integer, default=0)
    unit_price          = Column(Float, nullable=False)
    line_total          = Column(Float, default=0.0)

    # Relationships
    order          = relationship("Order", back_populates="items")
    inventory_item = relationship("InventoryItem", back_populates="order_items")


# ------------------------------------------------------------
# RESTOCK ORDER MODEL
# ------------------------------------------------------------
class RestockOrder(Base):
    __tablename__ = "restock_orders"

    id           = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(20), unique=True, index=True)
    total_cost   = Column(Float, default=0.0)
    status       = Column(String(20), default="ordered")
    notes        = Column(Text, nullable=True)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    received_at  = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    items = relationship("RestockItem", back_populates="restock_order")


# ------------------------------------------------------------
# RESTOCK ITEM MODEL
# ------------------------------------------------------------
class RestockItem(Base):
    __tablename__ = "restock_items"

    id                = Column(Integer, primary_key=True, index=True)
    restock_order_id  = Column(Integer, ForeignKey("restock_orders.id"))
    inventory_item_id = Column(Integer, ForeignKey("inventory.id"))
    quantity_ordered  = Column(Integer, nullable=False)
    unit_cost         = Column(Float, nullable=False)
    line_total        = Column(Float, default=0.0)

    # Relationships
    restock_order  = relationship("RestockOrder", back_populates="items")
    inventory_item = relationship("InventoryItem", back_populates="restock_items")


# ------------------------------------------------------------
# BUDGET / TRANSACTION MODEL
# ------------------------------------------------------------
class Transaction(Base):
    __tablename__ = "transactions"

    id               = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(20), nullable=False)
    amount           = Column(Float, nullable=False)
    balance_after    = Column(Float, nullable=False)
    description      = Column(String(255), nullable=True)
    reference_id     = Column(Integer, nullable=True)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())


# ------------------------------------------------------------
# BUDGET MODEL
# ------------------------------------------------------------
class Budget(Base):
    __tablename__ = "budget"

    id           = Column(Integer, primary_key=True, index=True)
    balance      = Column(Float, default=50000.00)
    total_earned = Column(Float, default=0.0)
    total_spent  = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())