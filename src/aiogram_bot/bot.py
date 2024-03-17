import asyncio

from loader import db, dp, bot
from handlers import registration_handler, start_handler, personal_area_handler
from logger import logger


async def start() -> None:
    try:
        logger.info("Инициализация роутеров...")
        dp.include_routers(
            start_handler.router,
            registration_handler.router,
            personal_area_handler.router
        )

        logger.info("Удаление вебхука...")
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("Запуск поллинга...")
        await dp.start_polling(bot)

        db.create_table_drivers()
        db.create_table_orders()
        logger.info("База данных запущена")
        logger.info("Бот успешно запущен")

    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}")


async def main() -> None:
    try:
        logger.info("Запуск главной функции...")
        await start()

    except Exception as e:
        logger.error(f"Произошла ошибка в главной функции: {e}")


if __name__ == "__main__":
    logger.info("Бот запущен")
    asyncio.run(main())