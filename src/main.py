from typing import AsyncGenerator, Any
from contextlib import asynccontextmanager
import asyncpg
import uvicorn
from fastapi import FastAPI, Depends, APIRouter
from settings import settings
from loguru import logger

# Создаем пул соединений
async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_HOST
    )

# Зависимость для получения соединения с базой данных
async def get_pg_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    pool = await create_pool()
    async with pool.acquire() as connection:
        yield connection

# Обработчик для получения версии базы данных
async def get_db_version(conn: asyncpg.Connection = Depends(get_pg_connection)) -> Any:
    return await conn.fetchval("SELECT version()")

# Регистрация маршрутов
def register_routes(app: FastAPI) -> None:
    router = APIRouter(prefix="/api")
    router.add_api_route(path="/db_version", endpoint=get_db_version)
    app.include_router(router)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Execute when the application starts.

    Yields:
        None: None.
    """
    logger.info("Starting up...")

    logger.info("Application started successfully.")

    yield

    """Execute when the application shutdowns."""

# Создание приложения FastAPI
app = FastAPI(title="e-Comet", openapi_url=settings.OPENAPI_URL, lifespan=lifespan)
register_routes(app)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.SERVER_HOST, port=settings.DEBUG_PORT)
