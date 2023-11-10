from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from lexicon.lexicon_ru import LEXICON_RU
from aiogram.filters import Command, CommandStart
from keyboards.keyboard_utils import create_inline_kb

user_router = Router()


@user_router.message(CommandStart())
async def process_command_start(message: Message):
    await message.answer(text=LEXICON_RU['/start'],
                         reply_markup=create_inline_kb(1, 'start_order', 'reviews', 'lists', 'sites', 'in_stock',
                                                       'faq'))


@user_router.callback_query(F.data == "back_main")
async def process_callback_back_main(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['/start'],
                                     reply_markup=create_inline_kb(1, 'start_order', 'reviews', 'lists', 'sites',
                                                                   'in_stock',
                                                                   'faq'))
    await callback.answer()


@user_router.message(Command('help'))
async def process_command_help(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


@user_router.callback_query(F.data == "sites")
async def process_callback_sites(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['country_shipper'],
                                     reply_markup=create_inline_kb(2, 'china', 'usa', **{"back_main": "<< Назад <<"}))
    await callback.answer()


@user_router.callback_query(F.data == "china")
async def process_callback_china(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['china_instructions'],
                                     reply_markup=create_inline_kb(1, **{"sites": "<< Назад <<"}))
    await callback.answer()


@user_router.callback_query(F.data == "usa")
async def process_callback_usa(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['usa_sites'],
                                     reply_markup=create_inline_kb(1, **{"sites": "<< Назад <<"}))
    await callback.answer()


@user_router.callback_query(F.data == "faq")
async def process_callback_faq(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['faq_desc'],
                                     reply_markup=create_inline_kb(1, 'ship', "restrictions", "contact",
                                                                   **{"back_main": "<< Назад <<"}))
    await callback.answer()


@user_router.callback_query(F.data == "ship")
async def process_callback_ship(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['ship_info'],
                                     reply_markup=create_inline_kb(1, **{"faq": "<< Назад <<"}))
    await callback.answer()


@user_router.callback_query(F.data == "restrictions")
async def process_callback_restrictions(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['restrictions_info'],
                                     reply_markup=create_inline_kb(1, **{"faq": "<< Назад <<"}))
    await callback.answer()


@user_router.callback_query(F.data == "lists")
async def process_callback_restrictions(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_RU['lists_info'],
                                     reply_markup=create_inline_kb(1, **{"back_main": "<< Назад <<"}))
    await callback.answer()
