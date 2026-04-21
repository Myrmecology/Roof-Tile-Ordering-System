# 🏗️ Roof Tile Ordering System

> A real-time roofing supply distribution simulator built for operational command.  
> Orders flow in live. You manage inventory, budget, fulfillment, and profit — all from one industrial-grade dashboard.

---

## 🖥️ Overview

The **Roof Tile Ordering System** is a full-stack Python web application that simulates running a roofing supply distribution business. Fictional companies and individual customers place randomized orders every 10–15 seconds via WebSocket. You receive the orders, fulfill them from your inventory, manage your budget, restock supplies, and track every dollar in and out.

This is not a form. This is not a tutorial clone. This is a live, breathing business simulation.

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+ / FastAPI |
| Real-Time | WebSockets |
| Database | SQLite + SQLAlchemy |
| Frontend | Tailwind CSS + Vanilla JS |
| Charts | Chart.js |
| Templates | Jinja2 |
| Server | Uvicorn |

---

## 🚀 Features

- 🔴 **Live Order Feed** — Randomized orders arrive every 10–15 seconds via WebSocket
- 📦 **Inventory Management** — Track all roofing supplies in real time
- 💰 **Budget & Profit System** — Monitor cash flow, costs, and profits
- 🛒 **Restocking System** — Place your own supply orders when inventory runs low
- 📊 **Analytics Dashboard** — See bestsellers, slow movers, and revenue trends
- 🧾 **Customer History** — Full log of every fictional customer and what they ordered
- ⚠️ **Low Stock Alerts** — Visual warnings when supplies are running critically low

---

## 📁 Project Structure
roof-tile-ordering-system/
├── app/
│   ├── main.py               # FastAPI application entry point
│   ├── models.py             # SQLAlchemy database models
│   ├── database.py           # Database connection and session
│   ├── schemas.py            # Pydantic schemas
│   ├── crud.py               # Database operations
│   ├── order_generator.py    # Random order generation engine
│   ├── websocket_manager.py  # WebSocket connection manager
│   └── routers/
│       ├── orders.py         # Order routes
│       ├── inventory.py      # Inventory routes
│       ├── customers.py      # Customer routes
│       └── analytics.py      # Analytics routes
├── static/
│   ├── css/dashboard.css     # Industrial UI styles
│   ├── js/                   # Frontend JavaScript modules
│   └── assets/textures/      # UI texture overlays
├── templates/                # Jinja2 HTML templates
├── data/                     # SQLite database (auto-generated)
├── .env                      # Environment variables (never committed)
├── requirements.txt          # Python dependencies
└── run.py                    # App launcher

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Myrmecology/Roof-Tile-Ordering-System.git
cd roof-tile-ordering-system
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/Scripts/activate  # Windows Bash
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your settings
```

### 5. Run the Application
```bash
python run.py
```

### 6. Open in Browser
http://localhost:8000

---

## 📊 Dashboard Panels

| Panel | Description |
|---|---|
| **Incoming Orders** | Live feed of arriving customer orders |
| **Inventory** | Current stock levels for all supply items |
| **Fulfillment Queue** | Orders awaiting your action |
| **Budget Overview** | Cash on hand, costs, and net profit |
| **Analytics** | Charts for sales trends and item performance |
| **Customer History** | Complete log of all past customers and orders |

---

## 🔐 Security

- All secrets and API keys stored in `.env` — never committed
- `.gitignore` configured for YubiKey, PGP, PEM, and all credential file types
- Database stays local — never pushed to version control

---


---

