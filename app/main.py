from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.db.pool import create_pool, close_pool
from app.exceptions import APIException
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await create_pool()
    yield
    await close_pool(app.state.db_pool)


app = FastAPI(title="User Registration API", lifespan=lifespan)

app.include_router(users.router)


@app.exception_handler(APIException)
async def api_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
