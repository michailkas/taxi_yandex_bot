import logging

# Настройка системы логирования
logging.basicConfig(
    level=logging.INFO,  # Можно установить другой уровень (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler("logfile.log")  # Сохранение ошибки в файл
    ]
)

# Получение экземпляра логгера
logger = logging.getLogger(__name__)
