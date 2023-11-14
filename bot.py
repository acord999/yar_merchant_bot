import asyncio
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_media_group import media_group_handler, MediaGroupFilter

from config_data.config import Config, load_config
from handlers import user_handlers, admin_handlers
from states.states import FSMCreateProduct
from database.models.methods import insert_new_product
from keyboards.keyboard_utils import create_inline_kb
from  lexicon.lexicon_ru import LEXICON_RU


async def main():
    # Загружаем конфиг в переменную config
    config: Config = load_config('.env')

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML")
    dp = Dispatcher()

    @dp.message(StateFilter(FSMCreateProduct.photo_paths), MediaGroupFilter())
    @media_group_handler
    async def process_product_photo(messages: List[Message], state: FSMContext):
        for message in messages:
            file_id = message.photo[-1].file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            await bot.download_file(file_path, f"media/pictures/{file_id}.jpg")
            prv_data = await state.get_data()
            await state.update_data(prv_data["photo_paths"].append(f"media/pictures/{file_id}.jpg"))

        data = await state.get_data()
        await state.clear()
        await insert_new_product(title=data["title"], description=data["description"], photo_paths=data["photo_paths"],
                                 category_id=data["category_id"])
        await message.answer(text=LEXICON_RU["edited_successfully"],
                             reply_markup=create_inline_kb(1, **{"manage_products": "<< Назад <<"}))

    # Регистриуем роутеры в диспетчере
    dp.include_router(user_handlers.user_router)
    dp.include_router(admin_handlers.admin_router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
