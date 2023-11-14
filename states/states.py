from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis
from config_data.config import load_config

redis = Redis(host=load_config().redis_config.host)
storage = RedisStorage(redis=redis)


class FSMCreateCategory(StatesGroup):
    title = State()


class FSMEditCategory(StatesGroup):
    category_id = State()
    new_title = State()


class FSMChangeCategoryStatus(StatesGroup):
    category_id = State()
    enabled = State()


class FSMCreateProduct(StatesGroup):
    category_id = State()
    title = State()
    description = State()
    photo_paths = State()


class FSMChangeProductStatus(StatesGroup):
    product_id = State()
    enabled = State()
