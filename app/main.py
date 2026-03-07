from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.db.pool import create_pool, close_pool
from app.exceptions import UserAlreadyExists
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_pool()
    yield
    await close_pool(app.state.db_pool)


app = FastAPI(title="User Registration API", lifespan=lifespan)

app.include_router(users.router)


@app.exception_handler(UserAlreadyExists)
async def user_already_exists_handler(request, exc):
    return JSONResponse(
        status_code=409,
        content={"detail": exc.detail, "code": exc.code},
    )


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
