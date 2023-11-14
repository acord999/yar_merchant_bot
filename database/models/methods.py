import asyncio

import datetime
from sqlalchemy import Integer, and_, func, text, insert, select, update, and_
from sqlalchemy.orm import aliased, Session
from database import async_engine, async_session_factory
from database.models.models import metadata, OrdersOrm, ClientsOrm, CategoriesOrm, ProductsOrm
from errors.errors import ClientAlreadyExistError, NoSuchClientError, NoSuchCategoryError, NoSuchProductError


async def is_client_exist(telegram_id: int) -> bool:
    async with async_session_factory() as session:
        q = select(ClientsOrm).where(ClientsOrm.telegram_id == telegram_id)
        result = await session.execute(q)
        return bool(result.first())


async def insert_new_client(telegram_id: int, name: str, lastname: str) -> None:
    existence = await is_client_exist(telegram_id)
    if not existence:
        async with async_session_factory() as session:
            new_client = ClientsOrm(telegram_id=telegram_id, name=name, lastname=lastname)
            session.add(new_client)
            await session.commit()
    else:
        raise ClientAlreadyExistError


async def change_client_status(client_id: [int, None] = None, telegram_id: [int, None] = None,
                               is_active: bool = True) -> None:
    async with async_session_factory() as session:
        if client_id and type(client_id) == int:
            client_for_ban = await session.get(ClientsOrm, client_id)
            if not client_for_ban:
                raise NoSuchClientError
            client_for_ban.is_active = is_active
        await session.commit()

        if telegram_id and type(telegram_id) == int:
            existence = await is_client_exist(telegram_id)
            if not existence:
                raise NoSuchClientError
            q = select(ClientsOrm).where(ClientsOrm.telegram_id == telegram_id)
            result = await session.execute(q)
            client_for_ban = result.first()[0]
            client_for_ban.is_active = is_active
            await session.commit()


async def get_client_id(telegram_id: int):
    async with async_session_factory() as session:
        q = select(ClientsOrm).where(ClientsOrm.telegram_id == telegram_id)
        result = await session.execute(q)
        client = result.first()
        if not client:
            raise NoSuchClientError
        return client[0].id


async def insert_new_category(title: str) -> None:
    if isinstance(title, str):
        async with async_session_factory() as session:
            new_category = CategoriesOrm(title=title)
            session.add(new_category)
            await session.commit()
    else:
        raise ValueError


async def is_category_exist(category_id: int) -> bool:
    async with async_session_factory() as session:
        q = select(ClientsOrm).where(CategoriesOrm.id == category_id)
        result = await session.execute(q)
        return bool(result.first())


async def change_category_status(category_id: int, enabled: bool = True) -> None:
    if not await is_category_exist(category_id):
        raise NoSuchCategoryError

    async with async_session_factory() as session:
        q = select(CategoriesOrm).where(CategoriesOrm.id == category_id)
        result = await session.execute(q)
        category = result.first()[0]
        category.enabled = enabled
        await session.commit()


async def get_category_list(enabled: bool = True) -> list[(int, str)]:
    res = []
    async with async_session_factory() as session:
        q = select(CategoriesOrm).where(CategoriesOrm.enabled == enabled)
        ex = await session.execute(q)
        _objs = ex.all()
        for obj in _objs:
            res.append((obj[0].id, obj[0].title))
    return res


async def change_category_title(category_id: int, title: str) -> None:
    if not await is_category_exist(category_id):
        raise NoSuchCategoryError

    async with async_session_factory() as session:
        q = select(CategoriesOrm).where(CategoriesOrm.id == category_id)
        result = await session.execute(q)
        category_to_edit = result.first()[0]
        category_to_edit.title = title
        await session.commit()


async def insert_new_product(title: str, description: str, photo_paths: list[str], category_id: int) -> None:
    async with async_session_factory() as session:
        new_product = ProductsOrm(title=title, description=description, photo_paths=photo_paths,
                                  category_id=category_id)
        session.add(new_product)
        await session.commit()


async def is_product_exist(product_id: int):
    async with async_session_factory() as session:
        q = select(ProductsOrm).where(ProductsOrm.id == product_id)
        result = await session.execute(q)
        return bool(result.first())


async def change_product_status(product_id: int, enabled: bool = True) -> None:
    if not await is_product_exist(product_id):
        raise NoSuchProductError

    async with async_session_factory() as session:
        q = select(ProductsOrm).where(ProductsOrm.id == product_id)
        result = await session.execute(q)
        product_to_change = result.first()[0]
        product_to_change.enabled = enabled
        await session.commit()


async def get_product_list(enabled: bool = True) -> list[(int, str)]:
    res = []
    async with async_session_factory() as session:
        q = select(ProductsOrm).where(ProductsOrm.enabled == enabled)
        ex = await session.execute(q)
        _objs = ex.all()
        for obj in _objs:
            res.append((obj[0].id, obj[0].title))
    return res


async def insert_new_order(title: str, description: str, link: str, from_client_id: int) -> None:
    async with async_session_factory() as session:
        new_order = OrdersOrm(title=title, description=description, link=link, from_client_id=from_client_id)
        session.add(new_order)
        await session.commit()
