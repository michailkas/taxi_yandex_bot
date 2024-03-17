import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from logger import logger
from data import sql

from utils import link_drivers

load_dotenv()

TOKEN_BOT = str(os.getenv("TOKEN_API"))

IP = os.getenv("IP")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
DATABASE = os.getenv("DATABASE")

dsn = f"dbname={DATABASE} user={PGUSER} password={PGPASSWORD} host={IP}"
db = sql.DataBase(dsn)
method_taxi_bot = link_drivers.YandexTaxiBot()

try:
    # Логирование инициализации бота
    logger.info("Initializing Bot...")
    bot = Bot(TOKEN_BOT, parse_mode="HTML")
    logger.info("Bot initialized successfully.")

    # Логирование инициализации диспетчера
    logger.info("Initializing Dispatcher...")
    dp = Dispatcher()
    logger.info("Dispatcher initialized successfully.")

    # Добавьте здесь код для запуска бота
    # Например: 
    # from aiogram import executor
    # executor.start_polling(dp, skip_updates=True)
except Exception as e:
    # Логирование ошибки инициализации
    logger.error(f"Error during initialization: {e}")