# ============================================================
# ROOF TILE ORDERING SYSTEM — Application Entry Point
# ============================================================

import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"
DEBUG = os.getenv("DEBUG", "True").lower() == "true"

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║         ROOF TILE ORDERING SYSTEM — BOOTING UP...           ║
║                                                              ║
║   Dashboard  →  http://127.0.0.1:8000                        ║
║   API Docs   →  http://127.0.0.1:8000/docs                   ║
║                                                              ║
║   Justin Computer Science — 2026                             ║
╚══════════════════════════════════════════════════════════════╝
    """)

    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level="debug" if DEBUG else "info",
    )