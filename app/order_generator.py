# ============================================================
# ROOF TILE ORDERING SYSTEM — Random Order Generator Engine
# ============================================================

import asyncio
import random
import os
from faker import Faker
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models import CustomerType, OrderStatus
from app import crud
from app.schemas import CustomerCreate, OrderCreate, OrderItemCreate

fake = Faker()
Faker.seed(0)

# ------------------------------------------------------------
# SUPPLY CATALOG
# Defines every orderable item by its SKU
# ------------------------------------------------------------
SUPPLY_CATALOG = [
    # SHINGLES
    {"sku": "SHG-GRN-001",  "name": "Green Roof Shingles",       "unit": "bundle"},
    {"sku": "SHG-BLK-002",  "name": "Black Roof Shingles",       "unit": "bundle"},
    {"sku": "SHG-DRD-003",  "name": "Dark Red Roof Shingles",    "unit": "bundle"},
    {"sku": "SHG-BRN-004",  "name": "Brown Roof Shingles",       "unit": "bundle"},
    {"sku": "SHG-GRY-005",  "name": "Charcoal Grey Shingles",    "unit": "bundle"},
    {"sku": "SHG-TAN-006",  "name": "Desert Tan Shingles",       "unit": "bundle"},

    # TAR
    {"sku": "TAR-STD-001",  "name": "Standard Roofing Tar",      "unit": "gallon"},
    {"sku": "TAR-PRO-002",  "name": "Pro Grade Roofing Tar",     "unit": "gallon"},
    {"sku": "TAR-WTP-003",  "name": "Waterproof Tar Sealant",    "unit": "gallon"},

    # GLOVES
    {"sku": "GLV-LTX-SM",   "name": "Small Latex Gloves",        "unit": "box"},
    {"sku": "GLV-LTX-MD",   "name": "Medium Latex Gloves",       "unit": "box"},
    {"sku": "GLV-LTX-LG",   "name": "Large Latex Gloves",        "unit": "box"},
    {"sku": "GLV-NTR-SM",   "name": "Small Nitrile Gloves",      "unit": "box"},
    {"sku": "GLV-NTR-MD",   "name": "Medium Nitrile Gloves",     "unit": "box"},
    {"sku": "GLV-NTR-LG",   "name": "Large Nitrile Gloves",      "unit": "box"},

    # UNDERLAYMENT
    {"sku": "UND-FLT-001",  "name": "Felt Underlayment Roll",    "unit": "roll"},
    {"sku": "UND-SYN-002",  "name": "Synthetic Underlayment Roll","unit": "roll"},
    {"sku": "UND-ICE-003",  "name": "Ice & Water Shield Roll",   "unit": "roll"},

    # NAILS
    {"sku": "NAL-COL-001",  "name": "Coil Roofing Nails",        "unit": "box"},
    {"sku": "NAL-GAL-002",  "name": "Galvanized Roofing Nails",  "unit": "box"},
    {"sku": "NAL-PLT-003",  "name": "Plastic Cap Nails",         "unit": "box"},

    # TOOLS
    {"sku": "TLS-CAU-001",  "name": "Roofing Caulk Tubes",       "unit": "box"},
    {"sku": "TLS-FLS-002",  "name": "Aluminum Flashing Rolls",   "unit": "roll"},
    {"sku": "TLS-RDG-003",  "name": "Ridge Cap Shingles",        "unit": "bundle"},
    {"sku": "TLS-DRP-004",  "name": "Drip Edge Strips",          "unit": "pack"},
]

# ------------------------------------------------------------
# FICTIONAL COMPANY NAMES
# ------------------------------------------------------------
COMPANY_NAMES = [
    "Summit Roofing Solutions",
    "Apex Construction Group",
    "Ridgeline Contractors LLC",
    "BlueSky Building Services",
    "IronClad Roofing Co.",
    "Pinnacle Home Repairs",
    "StormShield Contractors",
    "Keystone Roofing Inc.",
    "TerraFirm Construction",
    "HighGround Roofing",
    "Solid Roof Specialists",
    "Crestview Construction Co.",
    "ProRoof Services",
    "AllWeather Contractors",
    "TruShield Building Group",
    "Cornerstone Roofing LLC",
    "Elevated Structures Inc.",
    "Rooftop Masters",
    "Horizon Home Services",
    "DuraCraft Contractors",
]

# ------------------------------------------------------------
# ORDER QUANTITY RANGES BY UNIT TYPE
# Companies order more than individuals
# ------------------------------------------------------------
QUANTITY_RANGES = {
    "bundle": {"company": (10, 60),  "individual": (2, 15)},
    "gallon": {"company": (20, 150), "individual": (5, 40)},
    "box":    {"company": (5, 40),   "individual": (1, 10)},
    "roll":   {"company": (5, 30),   "individual": (1, 8)},
    "pack":   {"company": (10, 50),  "individual": (2, 12)},
}


# ============================================================
# SEED INVENTORY
# Called once at startup to populate the catalog
# ============================================================
INVENTORY_SEED = [
    # SHINGLES
    {"sku": "SHG-GRN-001", "name": "Green Roof Shingles",        "category": "shingles",     "unit": "bundle", "cost_price": 28.50,  "sell_price": 47.99,  "quantity": 200, "reorder_point": 30},
    {"sku": "SHG-BLK-002", "name": "Black Roof Shingles",        "category": "shingles",     "unit": "bundle", "cost_price": 27.00,  "sell_price": 45.99,  "quantity": 220, "reorder_point": 30},
    {"sku": "SHG-DRD-003", "name": "Dark Red Roof Shingles",     "category": "shingles",     "unit": "bundle", "cost_price": 29.00,  "sell_price": 48.99,  "quantity": 180, "reorder_point": 25},
    {"sku": "SHG-BRN-004", "name": "Brown Roof Shingles",        "category": "shingles",     "unit": "bundle", "cost_price": 27.50,  "sell_price": 46.50,  "quantity": 190, "reorder_point": 25},
    {"sku": "SHG-GRY-005", "name": "Charcoal Grey Shingles",     "category": "shingles",     "unit": "bundle", "cost_price": 30.00,  "sell_price": 49.99,  "quantity": 175, "reorder_point": 25},
    {"sku": "SHG-TAN-006", "name": "Desert Tan Shingles",        "category": "shingles",     "unit": "bundle", "cost_price": 28.00,  "sell_price": 46.99,  "quantity": 160, "reorder_point": 25},

    # TAR
    {"sku": "TAR-STD-001", "name": "Standard Roofing Tar",       "category": "tar",          "unit": "gallon", "cost_price": 8.50,   "sell_price": 14.99,  "quantity": 500, "reorder_point": 80},
    {"sku": "TAR-PRO-002", "name": "Pro Grade Roofing Tar",      "category": "tar",          "unit": "gallon", "cost_price": 12.00,  "sell_price": 21.99,  "quantity": 350, "reorder_point": 60},
    {"sku": "TAR-WTP-003", "name": "Waterproof Tar Sealant",     "category": "tar",          "unit": "gallon", "cost_price": 15.00,  "sell_price": 27.99,  "quantity": 280, "reorder_point": 50},

    # GLOVES
    {"sku": "GLV-LTX-SM",  "name": "Small Latex Gloves",         "category": "gloves",       "unit": "box",    "cost_price": 6.00,   "sell_price": 11.99,  "quantity": 300, "reorder_point": 40},
    {"sku": "GLV-LTX-MD",  "name": "Medium Latex Gloves",        "category": "gloves",       "unit": "box",    "cost_price": 6.00,   "sell_price": 11.99,  "quantity": 320, "reorder_point": 40},
    {"sku": "GLV-LTX-LG",  "name": "Large Latex Gloves",         "category": "gloves",       "unit": "box",    "cost_price": 6.00,   "sell_price": 11.99,  "quantity": 290, "reorder_point": 40},
    {"sku": "GLV-NTR-SM",  "name": "Small Nitrile Gloves",       "category": "gloves",       "unit": "box",    "cost_price": 7.50,   "sell_price": 13.99,  "quantity": 280, "reorder_point": 40},
    {"sku": "GLV-NTR-MD",  "name": "Medium Nitrile Gloves",      "category": "gloves",       "unit": "box",    "cost_price": 7.50,   "sell_price": 13.99,  "quantity": 310, "reorder_point": 40},
    {"sku": "GLV-NTR-LG",  "name": "Large Nitrile Gloves",       "category": "gloves",       "unit": "box",    "cost_price": 7.50,   "sell_price": 13.99,  "quantity": 270, "reorder_point": 40},

    # UNDERLAYMENT
    {"sku": "UND-FLT-001", "name": "Felt Underlayment Roll",     "category": "underlayment", "unit": "roll",   "cost_price": 18.00,  "sell_price": 31.99,  "quantity": 150, "reorder_point": 20},
    {"sku": "UND-SYN-002", "name": "Synthetic Underlayment Roll","category": "underlayment", "unit": "roll",   "cost_price": 24.00,  "sell_price": 42.99,  "quantity": 130, "reorder_point": 20},
    {"sku": "UND-ICE-003", "name": "Ice & Water Shield Roll",    "category": "underlayment", "unit": "roll",   "cost_price": 32.00,  "sell_price": 56.99,  "quantity": 100, "reorder_point": 15},

    # NAILS
    {"sku": "NAL-COL-001", "name": "Coil Roofing Nails",         "category": "nails",        "unit": "box",    "cost_price": 14.00,  "sell_price": 24.99,  "quantity": 250, "reorder_point": 35},
    {"sku": "NAL-GAL-002", "name": "Galvanized Roofing Nails",   "category": "nails",        "unit": "box",    "cost_price": 11.00,  "sell_price": 19.99,  "quantity": 260, "reorder_point": 35},
    {"sku": "NAL-PLT-003", "name": "Plastic Cap Nails",          "category": "nails",        "unit": "box",    "cost_price": 9.00,   "sell_price": 16.99,  "quantity": 220, "reorder_point": 30},

    # TOOLS
    {"sku": "TLS-CAU-001", "name": "Roofing Caulk Tubes",        "category": "tools",        "unit": "box",    "cost_price": 18.00,  "sell_price": 32.99,  "quantity": 120, "reorder_point": 20},
    {"sku": "TLS-FLS-002", "name": "Aluminum Flashing Rolls",    "category": "tools",        "unit": "roll",   "cost_price": 22.00,  "sell_price": 38.99,  "quantity": 110, "reorder_point": 15},
    {"sku": "TLS-RDG-003", "name": "Ridge Cap Shingles",         "category": "tools",        "unit": "bundle", "cost_price": 25.00,  "sell_price": 43.99,  "quantity": 140, "reorder_point": 20},
    {"sku": "TLS-DRP-004", "name": "Drip Edge Strips",           "category": "tools",        "unit": "pack",   "cost_price": 12.00,  "sell_price": 21.99,  "quantity": 180, "reorder_point": 25},
]

async def seed_inventory(db: AsyncSession):
    """Seed the inventory table if it is empty."""
    from app.schemas import InventoryItemCreate
    existing = await crud.get_inventory(db)
    if existing:
        return
    for item_data in INVENTORY_SEED:
        item = InventoryItemCreate(
            name=item_data["name"],
            sku=item_data["sku"],
            category=item_data["category"],
            unit=item_data["unit"],
            cost_price=item_data["cost_price"],
            sell_price=item_data["sell_price"],
            quantity=item_data["quantity"],
            reorder_point=item_data["reorder_point"],
            reorder_quantity=item_data.get("reorder_quantity", 100),
            description=f"{item_data['name']} — Professional grade roofing supply."
        )
        await crud.create_inventory_item(db, item)
    print("✅ Inventory seeded successfully.")


# ============================================================
# CUSTOMER GENERATOR
# ============================================================
async def get_or_create_customer(db: AsyncSession) -> int:
    """Return an existing customer or create a new fictional one."""
    all_customers = await crud.get_customers(db, limit=500)

    # 60% chance to reuse an existing customer if we have some
    if all_customers and random.random() < 0.60:
        return random.choice(all_customers).id

    # Generate a new fictional customer
    is_company = random.random() < 0.55

    if is_company:
        company = random.choice(COMPANY_NAMES)
        name    = fake.name()
        email   = f"{fake.user_name()}.{fake.last_name().lower()}@{fake.domain_name()}"
        data    = CustomerCreate(
            name=name,
            customer_type=CustomerType.COMPANY,
            company_name=company,
            email=email,
            phone=fake.phone_number()[:20],
            address=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr()
        )
    else:
        name  = fake.name()
        email = fake.email()
        data  = CustomerCreate(
            name=name,
            customer_type=CustomerType.INDIVIDUAL,
            company_name=None,
            email=email,
            phone=fake.phone_number()[:20],
            address=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr()
        )

    # Avoid duplicate emails
    existing = await crud.get_customer_by_email(db, email)
    if existing:
        return existing.id

    customer = await crud.create_customer(db, data)
    return customer.id


# ============================================================
# ORDER GENERATOR
# ============================================================
async def generate_random_order(db: AsyncSession) -> dict:
    """Generate one complete random order and return it as a dict."""
    inventory = await crud.get_inventory(db)
    if not inventory:
        return {}

    customer_id  = await get_or_create_customer(db)
    customer     = await crud.get_customer(db, customer_id)
    is_company   = customer.customer_type == CustomerType.COMPANY
    cust_type    = "company" if is_company else "individual"

    # Pick 2 to 6 random items, never duplicates
    num_items    = random.randint(2, 6)
    chosen_items = random.sample(inventory, min(num_items, len(inventory)))

    order_items = []
    for inv_item in chosen_items:
        unit    = inv_item.unit
        ranges  = QUANTITY_RANGES.get(unit, {"company": (5, 30), "individual": (1, 10)})
        lo, hi  = ranges[cust_type]
        qty     = random.randint(lo, hi)

        order_items.append(OrderItemCreate(
            inventory_item_id=inv_item.id,
            quantity_ordered=qty,
            unit_price=inv_item.sell_price
        ))

    order_data = OrderCreate(
        customer_id=customer_id,
        items=order_items,
        is_auto_generated=True,
        notes=None
    )

    order = await crud.create_order(db, order_data)

    # Build a human-readable summary for the WebSocket broadcast
    item_lines = []
    for oi, inv_item in zip(order_items, chosen_items):
        item_lines.append(
            f"{oi.quantity_ordered} {inv_item.unit}(s) of {inv_item.name}"
        )

    display_name = (
        customer.company_name
        if is_company and customer.company_name
        else customer.name
    )

    return {
        "order_id":     order.id,
        "order_number": order.order_number,
        "customer":     display_name,
        "customer_type": cust_type,
        "total_amount": order.total_amount,
        "item_count":   len(order_items),
        "items":        item_lines,
        "status":       order.status,
        "created_at":   order.created_at.isoformat()
            if order.created_at else datetime.now(timezone.utc).isoformat()
    }


# ============================================================
# BACKGROUND LOOP
# ============================================================
_generator_running = False

async def start_order_generator(broadcast_callback):
    """
    Infinite loop that generates a new order every 10-15 seconds
    and broadcasts it to all connected WebSocket clients.
    """
    global _generator_running
    if _generator_running:
        return
    _generator_running = True

    min_interval = int(os.getenv("ORDER_MIN_INTERVAL", 10))
    max_interval = int(os.getenv("ORDER_MAX_INTERVAL", 15))

    print("🏭 Order generator started — orders arriving every "
          f"{min_interval}–{max_interval} seconds.")

    while _generator_running:
        wait = random.randint(min_interval, max_interval)
        await asyncio.sleep(wait)

        try:
            async with AsyncSessionLocal() as db:
                order_data = await generate_random_order(db)
                if order_data:
                    await broadcast_callback({
                        "event":   "new_order",
                        "payload": order_data
                    })
                    print(f"📦 New order generated: {order_data.get('order_number')} "
                          f"— {order_data.get('customer')}")
        except Exception as e:
            print(f"⚠️  Order generator error: {e}")

def stop_order_generator():
    global _generator_running
    _generator_running = False
    print("🛑 Order generator stopped.")