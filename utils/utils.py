from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.models.methods import get_client_id, insert_new_order


class Order:
    def __init__(self, telegram_id, country: str, category: str, description: str, photo_path: str, client_id: int):
        self.telegram_id = telegram_id
        self.client_id = client_id
        self.photo_path = photo_path
        self.description = description
        self.category = category
        self.country = country

    def __str__(self):
        return f"<b>Получен новый заказ</b>\n\nСтрана: {self.country}\nКатегория: {self.category}\nИнформация от " \
               f"клиента: {self.description}"


async def download_photo(message: Message, bot: Bot) -> str:
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    local_path = f"media/pictures/{file_id}.jpg"
    await bot.download_file(file_path, local_path)
    return local_path


async def accept_order(message: Message, state: FSMContext) -> Order:
    data = await state.get_data()
    telegram_id = message.from_user.id
    client_id = await get_client_id(telegram_id=telegram_id)
    order = Order(
        country=data["country"],
        category=data["category"],
        description=data["description"],
        photo_path=data["photo_path"],
        telegram_id=telegram_id,
        client_id=client_id
    )

    await insert_new_order(description=order.description, country=order.country, category=order.category,
                           photo_path=order.photo_path,
                           from_client_id=order.client_id)

    return order
