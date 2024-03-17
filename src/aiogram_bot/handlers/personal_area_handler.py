from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import user_reply_markup

from logger import logger
from loader import method_taxi_bot, db

router = Router()


@router.message(F.text == "👤 Личный кабинет")
async def personal_area(message: Message):
    user_id = int(message.from_user.id)
    user = db.get_driver_fio_profile(user_id)
    if user:
        await message.answer(
            "Выберите, какой режим заказов вы хотите установить, и бот переведет вас на него!\n\n"
            "🚨 **ВНИМАНИЕ!** Выбирайте режим только перед началом выхода на линию.\n\n"
            "После выбора режима работы подождите 2 минуты и выходите на смену.",
            reply_markup=user_reply_markup.personal_area_kb
        )
    else:
        await message.answer(
            "Вы незарегестрированы в боте😢\n\n" 
            "Зарегестрируйтесь что-бы войти в личный кабинет!",
            reply_markup=user_reply_markup.start_kb
        )


@router.message(F.text.lower() == "🔙 назад")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=user_reply_markup.start_kb)


@router.message(F.text == "Только безналичные заказы 💳")
async def non_cash(message: Message):
    await message.answer("Вы выбрали безналичный вариант заказов!\nПодождите 2 минуты и вам будут приходить только безналичные заказы",
                         reply_markup=user_reply_markup.personal_area_kb)
    id = message.from_user.id
    url = db.get_link_profile(id)
    method_taxi_bot.non_cash(url[0])
    await message.answer("Бот успешно поменял заказы на безналичные")

    
@router.message(F.text == "Безналичные💳 и наличные💵 заказы")
async def non_cash_or_cash(message: Message):
    await message.answer("Вы выбрали безналичный и наличный вариант заказов!\nПодождите 2 минуты и вам будут приходить безналичные и наличные заказы",
                         reply_markup=user_reply_markup.personal_area_kb)
    id = message.from_user.id
    url = db.get_link_profile(id)
    method_taxi_bot.noncash_or_cash(url[0])
    await message.answer("Бот успешно поменял заказы на безналичные и наличные")


@router.message(F.text == "Cмена🔄 условий работы🚖")
async def change_working_conditions(message: Message):
    await message.answer('Выберите условия работы!', reply_markup=user_reply_markup.working_conditions_kb)


@router.message(F.text == "4р с заказа💰")
async def five_rubles_per_order(message: Message):
    await message.answer('Вы выбрали комиссию - "4 рубля с заказа"\nПодождите 2 минуты и комиссия изменится!',
                         reply_markup=user_reply_markup.personal_area_kb)
    id = message.from_user.id
    url = db.get_link_profile(id)
    method_taxi_bot.set_working_conditions(url=url[0], comission=4)
    await message.answer('Бот успешно поменял комиссию на "4 рубля с заказа"')
    

@router.message(F.text == "Комиссия 1.5%🚖")
async def Commission_one_and_half_percent(message: Message):
    await message.answer('Вы выбрали комиссию - "1.5%"\nПодождите 2 минуты и комиссия изменится!',
                         reply_markup=user_reply_markup.personal_area_kb)
    id = message.from_user.id
    url = db.get_link_profile(id)
    method_taxi_bot.set_working_conditions(url=url[0], comission=1)
    await message.answer('Бот успешно поменял комиссию на "1.5 рубля с заказа"')
    

@router.message(F.text == "Отмена текущего заказа❌")
async def cancellations(message: Message):
    await message.answer('Подождите 30 секунд и заказ отменится.',
                         reply_markup=user_reply_markup.personal_area_kb)
    id = message.from_user.id
    fio = db.get_driver_fio_profile(id)
    met = method_taxi_bot.cancellations(full_name=fio[0])
    if met == True:
        await message.answer('Бот успешно отменил текущий заказ!')
    else:
        await message.answer('Бот не отменил заказ, попробуйте еще раз!')