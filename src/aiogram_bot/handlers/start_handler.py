from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from keyboards import user_reply_markup


router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Добро пожаловать в бот таксопарка Luxtaxi", reply_markup=user_reply_markup.start_kb)
