"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import engine, Base, SessionLocal
from .seed_data import seed_database

# Import routers
from .routers import users, transactions, goals, assets, wealth, protection, chat, audit, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed data on startup."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered wealth intelligence with built-in cyber-security & fraud protection",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS – allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(transactions.router)
app.include_router(goals.router)
app.include_router(assets.router)
app.include_router(wealth.router)
app.include_router(protection.router)
app.include_router(chat.router)
app.include_router(audit.router)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}
