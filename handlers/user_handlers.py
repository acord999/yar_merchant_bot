from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.filters import Command, CommandStart, StateFilter, or_f
from aiogram.types import Message, CallbackQuery, FSInputFile

from config_data.config import load_config
from database.models.methods import is_client_exist, insert_new_client, get_category_list, \
    get_product_list, get_client_username
from database.models.models import ProductsOrm
from keyboards.keyboard_utils import create_inline_kb, create_order_report_kb
from lexicon.lexicon_ru import LEXICON_RU
from states.states import FSMProductUserView, FSMContext, FSMMakeOrder
from utils.utils import download_photo, accept_order
from .bot_instance import bot

ORDERS_CHANEL = load_config().tg_bot.orders_chanel

user_router = Router()


async def get_main_menu_view(message: Message, edit: bool = False):
    text = LEXICON_RU['/start']
    reply_markup = create_inline_kb(1, 'start_order', 'reviews', 'lists', 'sites',
                                    'in_stock',
                                    'faq')

    if edit:
        await message.edit_text(text=text, reply_markup=reply_markup)
    else:
        await message.answer(text=text, reply_markup=reply_markup)


async def get_user_category_view(message: Message, category_list: list, edit: bool = True) -> None:
    category_dict = {}
    for category in category_list:
        new_callback = f"user_category_{category[0]}"
        new_title = f"{category[1]}"
        category_dict[new_callback] = new_title
    category_dict["back_main"] = "<< Назад <<"
    if edit:
        await message.edit_text(text=LEXICON_RU["lists_info"], reply_markup=create_inline_kb(1, **category_dict))
    else:
        await message.answer(text=LEXICON_RU["lists_info"], reply_markup=create_inline_kb(1, **category_dict))


async def create_client_if_not_exist(message: Message) -> None:
    telegram_id: int = message.from_user.id
    if not await is_client_exist(telegram_id):
        name: str = message.from_user.first_name
        lastname: str = message.from_user.last_name
        tg_username: str = message.from_user.username
        await insert_new_client(telegram_id=telegram_id, name=name, lastname=lastname, tg_username=tg_username)


async def get_product_view(message: Message, product_list: list[ProductsOrm], current_product_number: int) -> None:
    title = product_list[current_product_number].title
    description = product_list[current_product_number].description
    photo_path = product_list[current_product_number].photo_path
    info_btn = f"{current_product_number + 1}/{len(product_list)}"

    await message.answer_photo(caption=f"<b>{title}</b>\n\n"
                                       f"<b>Описание</b>\n\n"
                                       f"{description}", photo=FSInputFile(photo_path),
                               reply_markup=create_inline_kb(3, "previous_product", info_btn, "next_product",
                                                             **{"lists_back": "<< Назад <<"}))
    await message.delete()


async def scroll_product_view(state: FSMContext, callback: CallbackQuery, nxt: bool = False, prv: bool = False):
    data = await state.get_data()
    current_product_number = data["current_product_number"]
    product_list = data["product_list"]
    if nxt:
        current_product_number = current_product_number if current_product_number + 1 == len(
            product_list) else current_product_number + 1
    elif prv:
        current_product_number = current_product_number if current_product_number - 1 < 0 else current_product_number - 1
    else:
        raise AttributeError("Вы не выбрали куда листать")
    await state.update_data(current_product_number=current_product_number)

    await get_product_view(message=callback.message, current_product_number=current_product_number,
                           product_list=product_list)


@user_router.message(CommandStart())
async def process_command_start(message: Message):
    await create_client_if_not_exist(message)
    await get_main_menu_view(message=message, edit=False)


@user_router.callback_query(F.data == "back_main")
async def process_callback_back_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await get_main_menu_view(message=callback.message, edit=True)
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


@user_router.callback_query(or_f(F.data == "lists", F.data == "lists_back"))
async def process_callback_restrictions(callback: CallbackQuery, state: FSMContext):
    category_list = await get_category_list(enabled=True)
    if callback.data == "lists":
        await get_user_category_view(message=callback.message, category_list=category_list, edit=True)
        print(F.data)
    elif callback.data == "lists_back":
        await get_user_category_view(message=callback.message, category_list=category_list, edit=False)
        await state.clear()
        await callback.message.delete()

    await callback.answer()


@user_router.callback_query(F.data.startswith("user_category_"))
async def process_user_category_callback(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[-1])
    await state.update_data(category_id=category_id)
    await state.set_state(FSMProductUserView.products_list)
    product_list = await get_product_list(enabled=True, category_id=category_id, full_obj=True)
    await state.update_data(product_list=product_list)
    await state.set_state(FSMProductUserView.current_product_number)
    await state.update_data(current_product_number=0)
    data = await state.get_data()
    current_product_number = data["current_product_number"]
    product_list = data["product_list"]

    await get_product_view(message=callback.message, current_product_number=current_product_number,
                           product_list=product_list)


@user_router.callback_query(StateFilter(FSMProductUserView.current_product_number), F.data == "next_product")
async def process_next_product_callback(callback: CallbackQuery, state: FSMContext):
    await scroll_product_view(callback=callback, state=state, nxt=True)


@user_router.callback_query(StateFilter(FSMProductUserView.current_product_number), F.data == "previous_product")
async def process_next_product_callback(callback: CallbackQuery, state: FSMContext):
    await scroll_product_view(callback=callback, state=state, prv=True)


@user_router.callback_query(F.data == "start_order")
async def process_start_order_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMMakeOrder.country)
    await callback.message.edit_text(text=LEXICON_RU["start_order_message"],
                                     reply_markup=create_inline_kb(
                                         2, "country_usa", "country_china", **{"back_main": "<< Назад <<"}))


@user_router.callback_query(F.data.startswith("country_"),
                            or_f(StateFilter(FSMMakeOrder.country), StateFilter(FSMMakeOrder.description)))
async def process_country_callback(callback: CallbackQuery, state: FSMContext):
    country = callback.data.split('_')[-1]
    await state.update_data(country=country)
    await state.set_state(FSMMakeOrder.category)
    await callback.message.edit_text(text=LEXICON_RU["choose_category_message"],
                                     reply_markup=create_inline_kb(
                                         2, "order_category_shoes", "order_category_clothes", "order_category_bags",
                                         "order_category_electronics", "order_category_others",
                                         **{"start_order": "<< Назад <<"}))


@user_router.callback_query(F.data.startswith("order_category_"), StateFilter(FSMMakeOrder.category))
async def process_order_category_callback(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split('_')[-1]
    data = await state.get_data()
    country = data["country"]
    await state.update_data(category=category)
    await state.set_state(FSMMakeOrder.description)
    await callback.message.edit_text(text=LEXICON_RU["send_description_message"],
                                     reply_markup=create_inline_kb(1, **{f"country_{country}": "<< Назад <<"}))


@user_router.message(StateFilter(FSMMakeOrder.description), F.content_type == ContentType.PHOTO)
async def process_description_message(message: Message, state: FSMContext):
    await state.update_data(description=message.caption)
    await state.set_state(FSMMakeOrder.photo_path)
    local_path = await download_photo(message, bot)
    await state.update_data(photo_path=local_path)
    order = await accept_order(message, state)
    await message.answer(text=LEXICON_RU["finish_order_message"],
                         reply_markup=create_inline_kb(1, **{"back_main": "<< Вернуться в главное меню <<"}))
    client_username = await get_client_username(message.from_user.id)
    report_keyboard = await create_order_report_kb(client_username)
    await bot.send_photo(chat_id=ORDERS_CHANEL, caption=str(order),
                         photo=FSInputFile(order.photo_path), reply_markup=report_keyboard)
