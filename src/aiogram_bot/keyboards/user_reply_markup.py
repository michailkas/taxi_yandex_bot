from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔐 Регистрация")
        ],
        [
            KeyboardButton(text="👤 Личный кабинет")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите действия из меню"
)


personal_area_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Только безналичные заказы 💳")
        ],
        [
            KeyboardButton(text="Безналичные💳 и наличные💵 заказы")
        ],
        # [
        #     KeyboardButton(text="Cмена🔄 условий работы🚖")
        # ],
        [
            KeyboardButton(text="Отмена текущего заказа❌")
        ],
        [
            KeyboardButton(text="🔙 назад")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите действия из меню"
)


working_conditions_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="4р с заказа💰")
        ],
        [
            KeyboardButton(text="Комиссия 1.5%🚖")
        ],
        [
            KeyboardButton(text="🔙 назад")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите действия из меню"
)


back_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔙 назад")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Для выхода в главное меню нажмите кнопку назад"
)