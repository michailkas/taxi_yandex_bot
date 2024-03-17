from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import re

from keyboards import user_reply_markup
from state.user_state import RegisterState

from loader import db, method_taxi_bot
from logger import logger

router = Router()

@router.message(F.text == "🔐 Регистрация")
async def register(message: Message, state: FSMContext):
    await state.set_state(RegisterState.fio)
    await message.answer("Введите свое ФИО в формате - Пупкин Василий Викторович. Обязательно введите как в примере!",
                         reply_markup=user_reply_markup.back_kb)


@router.message(F.text.lower() == "🔙 назад")
async def register(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=user_reply_markup.start_kb)


@router.message(RegisterState.fio)
async def fio(message: Message, state: FSMContext):
    # Удаляем кавычки из введенного текста с помощью регулярного выражения
    db.create_table_drivers()
    fio_text = re.sub(r'[\'‘’"]', '', message.text)
    await state.update_data(fio=fio_text)
    fio_data = await state.get_data()
    fio_data = fio_data.get("fio")
    
    username = message.from_user.username
    id = message.from_user.id
    
    await state.clear()
    
    check_registration_user = db.get_driver_profile(fio_data)
    if check_registration_user:
        await message.answer("Вы уже зарегистрированы в системе!", reply_markup=user_reply_markup.start_kb)
    else:
        link_driver = method_taxi_bot.get_links_drivers()
        link = link_driver.get(fio_data)
        if link != None:
            db.add_driver_to_database(fio=fio_data, username=username, id=id, link=link)
            logger.info(f"Бот зарегистрировал в базе данных нового пользователя {fio_data, username, id, link}")
            await message.answer("Спасибо за регистрацию! Желаем вам побольше денег на линии и надеемся, что вам понравится работа нашего бота.",
                                reply_markup=user_reply_markup.start_kb)
        else:
            await message.answer("Пользователь с таким ФИО не найден в базе данных таксопарка!", reply_markup=user_reply_markup.start_kb)
