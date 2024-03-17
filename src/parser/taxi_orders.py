import asyncio
import pickle 
import requests
from time import sleep

from telethon.sync import TelegramClient

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from loader import db, API_KEY, CLID, API_KEY_MAP, API_ID, API_HASH
from logger import logger


def getting_coordinates(address: str) -> dict:
    """
        Функция возвращает координаты,
        а на вход получает адрес
    """
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY_MAP}&geocode={address}&rspnrspn=1&format=json&results=1"
    response = requests.get(url)
    data = response.json()
    
    try:
        # Извлечение координат
        coordinates_str = data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        longitude, latitude = map(float, coordinates_str.split())
        logger.info(f"Функция getting_coordinates отработала, вот координаты: \n{longitude, latitude}")
        return {'longitude': longitude, 'latitude': latitude}
    except (KeyError, IndexError) as e:
        logger.error(f"Функция getting_coordinates не отработала, вот ответ response {response}, а вот ошибка: \n{e}")
        logger.info("Ошибка в ответе геокодера или нет результатов геокодирования.")


def order_price(clid, apikey, long1, lat1, long2, lat2):
    """
        функция получает на вход апи ключи яндекса и 
        координаты 2-х адресов, на выходе выдает цену
        такси из полученных координатов.
    """
    print(clid, apikey, long1, lat1, long2, lat2, end="\n")
    class_str = "econom"
    req_str = "<req_str>"
    url = f"https://taxi-routeinfo.taxi.yandex.net/taxi_info?clid={clid}&apikey={apikey}&rll={long1},{lat1}~{long2},{lat2}&class={class_str}&req={req_str}&lang=ru"        
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Успешно получена информация о цене такси: {data}")
            return data
        else:
            error_message = f"Ошибка {response.status_code}: {response.text}"
            logger.error(error_message)
            return error_message

    except Exception as e:
        logger.error(f"Произошла ошибка при запросе информации о цене такси: {e}")
        return f"Произошла ошибка: {e}"


async def send_telegram_message(message: str, username: int) -> None:
    async with TelegramClient('/home/vol_user/taxi_yandex_bot/src/parser/anon.session', API_ID, API_HASH) as client:
        await client.send_message(username, message)


async def add_db(drivers_list: str):
    """
        Функция добавляет всю информацию в базу данных
    """
    try:
        db.create_table_orders()
        db.create_table_drivers()
        if drivers_list is not None and len(drivers_list) > 0:
            for i in range(0, len(drivers_list), 6):
                fio = drivers_list[i]
                address_1 = drivers_list[i + 4] if i + 4 < len(drivers_list) else None
                address_2 = drivers_list[i + 5] if i + 5 < len(drivers_list) else None
                
                full_address_1 = f"{address_1}, Саратовская область"
                full_address_2 = f"{address_2}, Саратовская область"
            
                try:
                    # Проверяем, есть ли уже запись в таблице для данного водителя и адресов
                    check_table = db.checking_data_table({'ФИО': fio, '1 улица': full_address_1, '2 улица': full_address_2})
                except Exception as ex:
                    logger.error(f"Ошибка в процессе работы с функцией sql.checking_data_table: {e}")
                    check_table = None    
                
                sleep(5)
                if not check_table:
                    coordinates_1 = getting_coordinates(full_address_1)
                    coordinates_2 = getting_coordinates(full_address_2)
                    print(coordinates_1, coordinates_2)
                    if coordinates_1 is not None and coordinates_2 is not None:
                        order_info = order_price(CLID, API_KEY, coordinates_1['longitude'], coordinates_1['latitude'], coordinates_2['longitude'], coordinates_2['latitude'])
                        price_value = order_info.get('options', [{}])[0].get('price', 0)
                        order_distance = order_info.get("distance", "Нет данных")
                        order_time = order_info.get("time_text", "Нет данных")
                        
                        driver_info = {
                                'ФИО': fio,
                                '1 улица': full_address_1,
                                '2 улица': full_address_2,
                                'координаты 1 улицы': coordinates_1,
                                'координаты 2 улицы': coordinates_2,
                                'цена': price_value
                            }            
                            
                        if driver_info:
                            # Добавляем запись в таблицу
                            db.add_order_to_database(driver_info)       
                            message = (
                                    f"🆕 **Новый заказ!**\n\n"
                                    f"👤 **Водитель:** {driver_info['ФИО']}\n"
                                    f"🏠 **Откуда:** {driver_info['1 улица']}\n"
                                    f"🏠 **Куда:** {driver_info['2 улица']}\n"
                                    f"💰 **Цена:** {driver_info['цена']} руб.\n"
                                    f"🚖 **Время в пути:** {order_time}.\n"
                                    f"🌍 **Дистанция:** {round(order_distance / 1000)} км."
                                )
                            username_info = db.get_driver_profile(fio)
                            logger.info(message)
                            if username_info and len(username_info) > 0:
                                username_gt = username_info[0]               
                                await send_telegram_message(message, username_gt)
                                await send_telegram_message(message, 1851047530)     
                                logger.info(f"Сообщения для {username_gt} отправлено")
                
                else:
                    logger.info(f"Данные для водителя {fio} с адресами {address_1} и {address_2} уже существуют в таблице")
                
    except Exception as e:
        logger.error(f"Ошибка в процессе работы с функцией add_db: {e}")
        logger.error("Exception occurred", exc_info=True)


async def order_addresses():
    """
        Функция парсит заказы таксистов бесканечно и отправляет информацию в
        функцию add_db()
    """
    chrome_options = webdriver.ChromeOptions()
    chrome_options.page_load_strategy = "normal" #eager
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument(fr"--user-data-dir=/home/vol_user/taxi_yandex_bot/src/parser/file_of_selenium")
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = 'https://fleet.yandex.ru/map/drivers?statuses=in_order&sortBy=status_duration&sortDirection=desc&park_id=c0a8c5228fff4796abc901bcec379d45&theme=day' 
    driver.get(url)
    
    with open(r"C:\work\taxi_yandex_bot\src\parser\session.txt", "rb") as file:
        cookies = pickle.load(file)

    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.refresh()
    
    while True:
        try:
            sleep(5)
            fio_element = driver.find_element(By.CLASS_NAME, "wrAtHm")
            fio_text = fio_element.text.split("\n")
            
            # count_driver = fio_text[2] # количество водителей на заказах
            
            if len(fio_text) > 10:
                logger.info(f"Функция order_addresses отработала, вот адреса\n{fio_text[10:]}")
                await add_db(fio_text[10:])
            else:
                sleep(30)
                logger.info("Функция order_addresses отработала, не нашла работающих водителей и вернула None")
        except KeyboardInterrupt as e:
            driver.quit()
            logger.error(f"Функция order_addresses не отработала, вот ошибка: \n{e}")
            print("Работа остановлена")


async def main():
    await order_addresses()
    

if __name__ == "__main__":
    # while True:
    asyncio.run(main())
    # sleep(10)