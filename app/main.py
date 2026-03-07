from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.pool import create_pool, close_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_pool()
    yield
    await close_pool(app.state.db_pool)


app = FastAPI(title="User Registration API", lifespan=lifespan)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
