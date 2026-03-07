from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For DB pool init later
    yield


app = FastAPI(title="User Registration API", lifespan=lifespan)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}
