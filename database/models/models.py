import datetime
import os.path

from sqlalchemy import MetaData, Table, Column, Integer, Date, BigInteger, String, TIMESTAMP, ForeignKey, text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from typing import Annotated

# Создаем метаданные для таблиц
metadata = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True)]


class ClientsOrm(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    tg_username: Mapped[str] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=True)
    lastname: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    is_active: Mapped[bool] = mapped_column(server_default=text("True"))


class OrdersOrm(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column()
    photo_path: Mapped[str] = mapped_column(nullable=False)
    category: Mapped[str] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(nullable=False)
    from_client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))


class CategoriesOrm(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                          nullable=False)
    enabled: Mapped[bool] = mapped_column(server_default=text("True"))


class ProductsOrm(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    photo_path: Mapped[str] = mapped_column(nullable=True)
    enabled: Mapped[bool] = mapped_column(server_default=text("True"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))



