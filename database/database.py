import asyncio
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import String, create_engine, text
from config_data.config import DATABASE_URL_asyncpg, DATABASE_URL_psycopg


# Асинхронный движок
async_engine = create_async_engine(
    url=DATABASE_URL_asyncpg(),
    echo=True,
    # Количество одновременных подключений
    pool_size=5,
    # Количество запасных подключений
    max_overflow=10
)

# Синхронный движок
sync_engine = create_engine(
    url=DATABASE_URL_psycopg(),
    echo=True,
    # Количество одновременных подключений
    pool_size=5,
    # Количество запасных подключений
    max_overflow=10
)
# Объявление сессии
async_session_factory = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass


async def get_version() -> tuple:
    async with async_engine.connect() as conn:
        version = await conn.execute(text("SELECT VERSION()"))
        return version.first()


if __name__ == "__main__":
    # Тест подключения
    print(asyncio.run(get_version()))