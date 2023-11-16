import asyncio
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_media_group import media_group_handler, MediaGroupFilter
from handlers.bot_instance import bot
from config_data.config import Config, load_config
from handlers import user_handlers, admin_handlers
from states.states import FSMCreateProduct
from database.models.methods import insert_new_product
from keyboards.keyboard_utils import create_inline_kb
from  lexicon.lexicon_ru import LEXICON_RU


async def main(bot=bot):
    # Загружаем конфиг в переменную config
    config: Config = load_config('.env')

    # Инициализируем бот и диспетчер
    dp = Dispatcher()



    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.user_router)
    dp.include_router(admin_handlers.admin_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
