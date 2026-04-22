from fastapi import FastAPI
from app.routes.api import router

app = FastAPI(title="Wealth Engine")

app.include_router(router, prefix="/api")