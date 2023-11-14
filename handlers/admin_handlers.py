from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config_data.config import load_config
from database.models.methods import insert_new_category, get_category_list, change_category_title, \
    change_category_status, get_product_list, change_product_status
from keyboards.keyboard_utils import create_inline_kb
from lexicon.lexicon_ru import LEXICON_RU
from states.states import FSMCreateCategory, FSMEditCategory, FSMChangeCategoryStatus, FSMCreateProduct, \
    FSMChangeProductStatus

admin_router = Router()
ADMIN_IDS = load_config().tg_bot.admin_ids


async def parse_status_callback(callback: CallbackQuery, state: FSMContext,
                                FSM: FSMChangeCategoryStatus | FSMChangeProductStatus, product: bool = False,
                                category: bool = False) -> dict:
    if category:
        await state.update_data(category_id=int(callback.data.split("_")[-2]))
    elif product:
        await state.update_data(product_id=int(callback.data.split("_")[-2]))
    else:
        raise ValueError
    await state.set_state(FSM.enabled)
    await state.update_data(enabled=True if callback.data.split("_")[-1] == "True" else False)
    data = await state.get_data()
    return data


async def get_category_panel(message: Message, edit: bool = False):
    text = LEXICON_RU["category_panel"]
    reply_markup = create_inline_kb(1, "create_category", "edit_category",
                                    "change_category_status",
                                    **{"back_admin": "<< Назад <<"})
    if edit:
        await message.edit_text(text=text, reply_markup=reply_markup)
    else:
        await message.answer(text=text, reply_markup=reply_markup)


async def get_category_view(message: Message, keyword: str):
    category_dict = {}
    enabled_categories = await get_category_list()
    disabled_categories = await get_category_list(enabled=False)
    for category in enabled_categories:
        category_dict[f"change_category_{keyword}_{str(category[0])}_True"] = f"✅ {category[0]} {category[1]}"
    for category in disabled_categories:
        category_dict[f"change_category_{keyword}_{str(category[0])}_False"] = f"❌ {category[0]} {category[1]}"
    await message.edit_text(text='Пожалуйста, выберите категорию для изменения\n'
                                 'Если передумаете команда /cancel',
                            reply_markup=create_inline_kb(1, **category_dict))


async def get_product_view(message: Message, keyword: str):
    product_dict = {}
    enabled_products = await get_product_list()
    disabled_products = await get_product_list(enabled=False)
    for product in enabled_products:
        product_dict[f"change_product_{keyword}_{str(product[0])}_True"] = f"✅ {product[0]} {product[1]}"
    for product in disabled_products:
        product_dict[f"change_product_{keyword}_{str(product[0])}_False"] = f"❌ {product[0]} {product[1]}"
    await message.edit_text(text='Пожалуйста, выберите товар для изменения\n'
                                 'Если передумаете команда /cancel',
                            reply_markup=create_inline_kb(1, **product_dict))


async def get_main_admin(message: Message, edit: bool = False):
    text = LEXICON_RU["admin_panel"]
    reply_markup = create_inline_kb(1, "manage_categories", "manage_products")

    if edit:
        await message.edit_text(text=text, reply_markup=reply_markup)
    else:
        await message.answer(text=text, reply_markup=reply_markup)


async def get_manage_product_view(message: Message, edit: bool = False):
    text = LEXICON_RU["manage_products"]
    reply_markup = create_inline_kb(1, "create_product", "change_product_status", **{"back_admin": "<< Назад <<"})

    if edit:
        await message.edit_text(text=text, reply_markup=reply_markup)
    else:
        await message.answer(text=text, reply_markup=reply_markup)


@admin_router.message(Command("admin"))
async def process_admin_command(message: Message):
    if message.chat.id in ADMIN_IDS:
        await get_main_admin(message=message, edit=False)


@admin_router.callback_query(F.data == "back_admin")
async def process_admin_callback(callback: CallbackQuery):
    if callback.message.chat.id in ADMIN_IDS:
        await get_main_admin(message=callback.message, edit=True)


@admin_router.callback_query(F.data == "manage_categories")
async def process_manage_categories_callback(callback: CallbackQuery):
    if callback.message.chat.id in ADMIN_IDS:
        await get_category_panel(message=callback.message, edit=True)


@admin_router.callback_query(F.data == "create_category")
async def process_create_category_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        await callback.message.edit_text(text=LEXICON_RU["insert_category_name"])
        await state.set_state(FSMCreateCategory.title)


@admin_router.message(
    and_f(or_f(StateFilter(FSMCreateCategory), StateFilter(FSMEditCategory), StateFilter(FSMChangeCategoryStatus)),
          Command('cancel')))
async def proces_command_cancel(message: Message, state: FSMContext):
    if message.chat.id in ADMIN_IDS:
        await get_category_panel(message=message, edit=False)
        await state.clear()


@admin_router.message(StateFilter(FSMCreateCategory.title))
async def process_new_category_title(message: Message, state: FSMContext):
    if message.chat.id in ADMIN_IDS:
        await state.update_data(title=message.text)
        data = await state.get_data()
        title = data['title']
        await state.clear()
        await insert_new_category(title=title)
        await message.answer(text=LEXICON_RU["added_successfully"],
                             reply_markup=create_inline_kb(1, **{"manage_categories": "<< Назад <<"}))


@admin_router.callback_query(F.data == "edit_category")
async def process_edit_category_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        await get_category_view(message=callback.message, keyword="title")
        await state.set_state(FSMEditCategory.category_id)


@admin_router.callback_query(StateFilter(FSMEditCategory.category_id), F.data.startswith('change_category_title_'))
async def process_category_id_edit_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        category_id: int = int(callback.data.split('_')[-2])
        await state.update_data(category_id=category_id)
        await callback.message.answer(f"<b>Вы выбрали категорию под номером</b>: {category_id}\n"
                                      f"<b>Пожалуйста введите новое название категории</b>\n"
                                      f"Для отмены /cancel")
        await callback.answer()
        await state.set_state(FSMEditCategory.new_title)


@admin_router.message(StateFilter(FSMEditCategory.new_title))
async def process_category_new_title_edit_callback(message: Message, state: FSMContext):
    if message.chat.id in ADMIN_IDS:
        await state.update_data(new_title=message.text)
        data = await state.get_data()
        await change_category_title(category_id=data['category_id'], title=data['new_title'])
        await message.answer(text=LEXICON_RU["edited_successfully"],
                             reply_markup=create_inline_kb(1, **{"manage_categories": "<< Назад <<"}))
        await state.clear()


@admin_router.callback_query(F.data == "change_category_status")
async def process_change_category_status_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        await state.set_state(FSMChangeCategoryStatus.category_id)
        await get_category_view(message=callback.message, keyword="status")


@admin_router.callback_query(StateFilter(FSMChangeCategoryStatus.category_id),
                             F.data.startswith("change_category_status_"))
async def process_change_category_status_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        data = await parse_status_callback(callback=callback, state=state, FSM=FSMChangeCategoryStatus, category=True)
        category_id = data['category_id']
        enabled = data["enabled"]
        await change_category_status(category_id=category_id, enabled=not enabled)
        await state.clear()
        await state.set_state(FSMChangeCategoryStatus.category_id)
        await get_category_view(message=callback.message, keyword="status")


@admin_router.callback_query(F.data == "manage_products")
async def process_manage_products_callback(callback: CallbackQuery):
    if callback.message.chat.id in ADMIN_IDS:
        await get_manage_product_view(message=callback.message, edit=True)


@admin_router.callback_query(F.data == "create_product")
async def process_create_product_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        await state.set_state(FSMCreateProduct.category_id)
        category_dict = {}
        enabled_categories = await get_category_list()
        disabled_categories = await get_category_list(enabled=False)
        for category in enabled_categories:
            category_dict[f"product_category_{str(category[0])}_{category[1]}"] = f"✅ {category[0]} {category[1]}"
        for category in disabled_categories:
            category_dict[f"product_category_{str(category[0])}"] = f"❌ {category[0]} {category[1]}"
        await callback.message.edit_text(text=LEXICON_RU["pls_select_category"],
                                         reply_markup=create_inline_kb(1, **category_dict))


@admin_router.message(or_f(StateFilter(FSMCreateProduct), StateFilter(FSMChangeProductStatus)), Command('cancel'))
async def proces_command_cancel(message: Message, state: FSMContext):
    if message.chat.id in ADMIN_IDS:
        await get_manage_product_view(message=message, edit=False)
        await state.clear()


@admin_router.callback_query(F.data.startswith("product_category_"), StateFilter(FSMCreateProduct.category_id))
async def process_product_category_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        category_id = int(callback.data.split("_")[-2])
        title = callback.data.split("_")[-1]
        await state.update_data(category_id=category_id)
        await state.set_state(FSMCreateProduct.title)
        await callback.message.edit_text(text=f"Вы выбрали категорию: <b>{title}</b>\n"
                                              f"Пожалуйста введите название нового товара\n"
                                              f"Если передумаете команда /cancel")


@admin_router.message(StateFilter(FSMCreateProduct.title))
async def process_product_title_message(message: Message, state: FSMContext):
    if message.chat.id in ADMIN_IDS:
        title = message.text
        await state.update_data(title=title)
        await state.set_state(FSMCreateProduct.description)
        await message.answer(f"<b>Название товара</b> {title}\n"
                             f"Напишите описание для товара\n"
                             f"Если передумаете команда /cancel")


@admin_router.message(StateFilter(FSMCreateProduct.description))
async def process_product_title_message(message: Message, state: FSMContext):
    if message.chat.id in ADMIN_IDS:
        description = message.text
        await state.update_data(description=description)
        await state.set_state(FSMCreateProduct.photo_paths)
        await message.answer(f"<b>Описание товара</b> {description}\n"
                             f"Пришлите фото для товара. Одним альбомом\n"
                             f"Если передумаете команда /cancel")
        await state.update_data(photo_paths=[])


@admin_router.callback_query(F.data == "change_product_status")
async def process_change_product_status_callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        await state.set_state(FSMChangeProductStatus.product_id)
        await get_product_view(message=callback.message, keyword="status")


@admin_router.callback_query(StateFilter(FSMChangeProductStatus.product_id),
                             F.data.startswith("change_product_status_"))
async def process_change_product_status__callback(callback: CallbackQuery, state: FSMContext):
    if callback.message.chat.id in ADMIN_IDS:
        data = await parse_status_callback(callback=callback, state=state, FSM=FSMChangeProductStatus, product=True)
        product_id = data['product_id']
        enabled = data["enabled"]
        await change_product_status(product_id=product_id, enabled=not enabled)
        await state.clear()
        await state.set_state(FSMChangeProductStatus.product_id)
        await get_product_view(message=callback.message, keyword="status")
