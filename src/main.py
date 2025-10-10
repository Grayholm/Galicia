# ruff: noqa: E402
import sys
from pathlib import Path
import logging

from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)

from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.api.auth import router as router_auth
from src.api.hotels import router as router_hotels
from src.api.rooms import router as router_rooms
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.api.images import router as router_images
from src.init import redis_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    logging.info("FastAPI Cache connection initialized")
    yield
    await redis_manager.close()


app = FastAPI(lifespan=lifespan)
app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)
app.include_router(router_images)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400, content={"detail": "Поля не должны быть пустыми и не должны быть пустой строкой"}
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
