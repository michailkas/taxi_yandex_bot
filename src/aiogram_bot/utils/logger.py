import logging

# Настройка системы логирования
logging.basicConfig(
    level=logging.INFO,  # Можно установить другой уровень (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("logfile_bot.log", encoding="utf-8")  # Сохранение ошибки в файл
    ]
)

# Получение экземпляра логгера
logger = logging.getLogger(__name__)
