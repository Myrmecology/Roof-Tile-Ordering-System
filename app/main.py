# ============================================================
# ROOF TILE ORDERING SYSTEM — FastAPI Application Core
# ============================================================

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import asyncio
import os

from app.database import init_db, AsyncSessionLocal
from app.websocket_manager import manager
from app.order_generator import start_order_generator, seed_inventory
from app.routers import orders, inventory, customers, analytics
from app import crud

load_dotenv()

# ============================================================
# LIFESPAN — Startup & Shutdown
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    # ── STARTUP ──────────────────────────────────────────────
    print("\n⚙️  Initializing database...")
    await init_db()

    async with AsyncSessionLocal() as db:
        await seed_inventory(db)
        await crud.get_budget(db)

    print("✅ Database ready.")

    # Start the background order generator
    asyncio.create_task(
        start_order_generator(manager.broadcast)
    )
    print("✅ Order generator running.")

    yield

    # ── SHUTDOWN ─────────────────────────────────────────────
    from app.order_generator import stop_order_generator
    stop_order_generator()
    print("👋 Roof Tile Ordering System shut down cleanly.")


# ============================================================
# FASTAPI APP INSTANCE
# ============================================================
app = FastAPI(
    title="Roof Tile Ordering System",
    description="A real-time roofing supply distribution simulator.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================
# STATIC FILES & TEMPLATES
# ============================================================
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ============================================================
# ROUTERS
# ============================================================
app.include_router(orders.router,    prefix="/api/orders",    tags=["Orders"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])


# ============================================================
# PAGE ROUTES
# ============================================================
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html", {"request": request}
    )

@app.get("/orders", response_class=HTMLResponse)
async def orders_page(request: Request):
    return templates.TemplateResponse(
        "orders.html", {"request": request}
    )

@app.get("/inventory", response_class=HTMLResponse)
async def inventory_page(request: Request):
    return templates.TemplateResponse(
        "inventory.html", {"request": request}
    )

@app.get("/customers", response_class=HTMLResponse)
async def customers_page(request: Request):
    return templates.TemplateResponse(
        "customers.html", {"request": request}
    )

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse(
        "analytics.html", {"request": request}
    )


# ============================================================
# WEBSOCKET ENDPOINT
# ============================================================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send a welcome message immediately on connect
        await manager.send_personal({
            "event": "connected",
            "payload": {
                "message": "Connected to Roof Tile Ordering System",
                "connections": manager.connection_count
            }
        }, websocket)

        # Keep the connection alive and listen for
        # any messages sent from the browser
        while True:
            data = await websocket.receive_text()
            # Echo back any client-side pings to keep alive
            if data == "ping":
                await manager.send_personal(
                    {"event": "pong", "payload": {}}, websocket
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"⚠️  WebSocket error: {e}")
        await manager.disconnect(websocket)


# ============================================================
# HEALTH CHECK
# ============================================================
@app.get("/health")
async def health_check():
    return {
        "status":      "online",
        "app":         "Roof Tile Ordering System",
        "version":     "1.0.0",
        "websockets":  manager.connection_count,
        "author":      "Justin Computer Science — 2026"
    }