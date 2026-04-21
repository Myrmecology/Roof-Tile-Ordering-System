# ============================================================
# ROOF TILE ORDERING SYSTEM — Pydantic Schemas
# ============================================================

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models import OrderStatus, CustomerType, SupplyCategory

# ============================================================
# BASE CONFIG
# ============================================================
class AppModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CUSTOMER SCHEMAS
# ============================================================
class CustomerBase(AppModel):
    name:          str            = Field(..., min_length=2, max_length=100)
    customer_type: CustomerType   = CustomerType.INDIVIDUAL
    company_name:  Optional[str]  = Field(None, max_length=150)
    email:         str            = Field(..., max_length=120)
    phone:         Optional[str]  = Field(None, max_length=30)
    address:       Optional[str]  = Field(None, max_length=255)
    city:          Optional[str]  = Field(None, max_length=100)
    state:         Optional[str]  = Field(None, max_length=50)

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(AppModel):
    name:          Optional[str]          = None
    company_name:  Optional[str]          = None
    phone:         Optional[str]          = None
    address:       Optional[str]          = None
    city:          Optional[str]          = None
    state:         Optional[str]          = None

class CustomerOut(CustomerBase):
    id:           int
    total_spent:  float
    order_count:  int
    created_at:   datetime
    updated_at:   Optional[datetime] = None


# ============================================================
# INVENTORY SCHEMAS
# ============================================================
class InventoryItemBase(AppModel):
    name:             str            = Field(..., min_length=2, max_length=150)
    sku:              str            = Field(..., max_length=50)
    category:         str
    description:      Optional[str]  = None
    unit:             str            = Field(..., max_length=30)
    quantity:         int            = Field(0, ge=0)
    reorder_point:    int            = Field(10, ge=0)
    reorder_quantity: int            = Field(50, ge=1)
    cost_price:       float          = Field(..., gt=0)
    sell_price:       float          = Field(..., gt=0)

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(AppModel):
    quantity:         Optional[int]   = Field(None, ge=0)
    reorder_point:    Optional[int]   = Field(None, ge=0)
    reorder_quantity: Optional[int]   = Field(None, ge=1)
    cost_price:       Optional[float] = Field(None, gt=0)
    sell_price:       Optional[float] = Field(None, gt=0)
    is_active:        Optional[bool]  = None

class InventoryItemOut(InventoryItemBase):
    id:            int
    total_sold:    int
    total_revenue: float
    is_active:     bool
    created_at:    datetime
    updated_at:    Optional[datetime] = None


# ============================================================
# ORDER ITEM SCHEMAS
# ============================================================
class OrderItemBase(AppModel):
    inventory_item_id:  int
    quantity_ordered:   int   = Field(..., ge=1)
    unit_price:         float = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemOut(OrderItemBase):
    id:                 int
    quantity_fulfilled: int
    line_total:         float
    inventory_item:     Optional[InventoryItemOut] = None


# ============================================================
# ORDER SCHEMAS
# ============================================================
class OrderBase(AppModel):
    customer_id:       int
    notes:             Optional[str] = None
    is_auto_generated: bool          = True

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(AppModel):
    status: Optional[OrderStatus] = None
    notes:  Optional[str]         = None

class OrderOut(OrderBase):
    id:           int
    order_number: str
    status:       OrderStatus
    total_amount: float
    profit:       float
    created_at:   datetime
    fulfilled_at: Optional[datetime] = None
    customer:     Optional[CustomerOut]    = None
    items:        Optional[List[OrderItemOut]] = []


# ============================================================
# RESTOCK SCHEMAS
# ============================================================
class RestockItemBase(AppModel):
    inventory_item_id: int
    quantity_ordered:  int   = Field(..., ge=1)
    unit_cost:         float = Field(..., gt=0)

class RestockItemCreate(RestockItemBase):
    pass

class RestockItemOut(RestockItemBase):
    id:         int
    line_total: float
    inventory_item: Optional[InventoryItemOut] = None

class RestockOrderCreate(AppModel):
    notes: Optional[str] = None
    items: List[RestockItemCreate]

class RestockOrderOut(AppModel):
    id:           int
    order_number: str
    total_cost:   float
    status:       str
    notes:        Optional[str]  = None
    created_at:   datetime
    received_at:  Optional[datetime] = None
    items:        Optional[List[RestockItemOut]] = []


# ============================================================
# BUDGET & TRANSACTION SCHEMAS
# ============================================================
class TransactionOut(AppModel):
    id:               int
    transaction_type: str
    amount:           float
    balance_after:    float
    description:      Optional[str] = None
    reference_id:     Optional[int] = None
    created_at:       datetime

class BudgetOut(AppModel):
    id:           int
    balance:      float
    total_earned: float
    total_spent:  float
    total_profit: float
    updated_at:   Optional[datetime] = None


# ============================================================
# ANALYTICS SCHEMAS
# ============================================================
class TopSellerOut(AppModel):
    item_name:     str
    sku:           str
    total_sold:    int
    total_revenue: float

class SlowestSellerOut(AppModel):
    item_name:  str
    sku:        str
    total_sold: int
    quantity:   int

class AnalyticsSummaryOut(AppModel):
    total_orders:     int
    pending_orders:   int
    fulfilled_orders: int
    total_revenue:    float
    total_profit:     float
    top_sellers:      List[TopSellerOut]
    slowest_sellers:  List[SlowestSellerOut]


# ============================================================
# WEBSOCKET MESSAGE SCHEMAS
# ============================================================
class WebSocketMessage(AppModel):
    event:   str
    payload: dict


# ============================================================
# DASHBOARD SUMMARY SCHEMA
# ============================================================
class DashboardSummary(AppModel):
    budget:           BudgetOut
    pending_orders:   int
    fulfilled_today:  int
    low_stock_items:  int
    total_customers:  int