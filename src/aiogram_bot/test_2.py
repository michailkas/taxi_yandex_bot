from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from selenium.common.exceptions import TimeoutException, NoSuchWindowException, NoSuchElementException

from time import sleep
import pickle
from logger import logger


class YandexTaxiBot:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.page_load_strategy = "normal" #eager
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.3")
        chrome_options.add_argument("--lang=ru")
        self.service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)
        self.load_cookies()

    def load_cookies(self):
        # Путь к файлу с cookies
        cookies_file_path = r"C:\work\taxi_yandex_bot\src\aiogram_bot\session.txt"

        try:
            with open(cookies_file_path, "rb") as file:
                cookies = pickle.load(file)

            # Добавление каждого cookie в веб-драйвер
            for cookie in cookies:
                self.driver.add_cookie(cookie)

            logger.info("Cookies успешно добавлены.")
        except Exception as e:
            logger.error(f"Произошла ошибка при загрузке cookies: {e}")
    
    def get_links_drivers(self) -> dict:
        """
            Парсит ФИО водителей и ссылки на их профиль.
            Возвращает словарь
        """
        try:
            url = r"https://fleet.yandex.ru/drivers?limit=100&status=working&park_id=c0a8c5228fff4796abc901bcec379d45"
            self.driver.get(url)
            self.load_cookies()
            self.driver.refresh()
            
            # with open(r"C:\work\taxi_yandex_bot\src\aiogram_bot\session.txt", "rb") as file:
            #     cookies = pickle.load(file)

            # for cookie in cookies:
            #     self.driver.add_cookie(cookie)

            # self.driver.refresh()
            
            sleep(5)
    
            column_xpath = ("xpath", "//tbody//tr")
            rows = self.wait.until(
                EC.presence_of_all_elements_located(column_xpath)
            )
            driver_data = {}
            
            for row in rows:
                # Извлекаем ФИО водителя
                full_name_element = row.find_element("xpath", './/td[4]')
                full_name = full_name_element.text
                
                # Извлекаем ссылку на профиль водителя
                profile_link_element = row.find_element("xpath", './/td[4]/a')
                profile_link = profile_link_element.get_attribute("href")
                
                # Добавляем данные в словарь
                driver_data[full_name] = profile_link
                
            return driver_data
        except Exception as e:
            logger.error(f"Error in get_links_drivers: {str(e)}")

    def set_balance_limit(self, url: str, limit: int) -> None:
        """
            Функция меняет балансы в личном кабинете
        """
        try:
            self.driver.get(url)
            self.load_cookies()
            self.driver.refresh()
            # Ждем, пока элемент формы не станет доступным
            form = self.wait.until(
                EC.presence_of_element_located(("css selector", 'input.Textinput-Control[name="accounts.balance_limit"]'))
            )   
            
            # Выделить текст в поле и удалить его
            form.send_keys(Keys.CONTROL + "a")  # Выделить весь текст
            form.send_keys(Keys.DELETE)  # Удалить выделенный текст

            # Теперь вводим новое значение
            form.send_keys(limit)

            submit_save = self.driver.find_element('xpath', '//button[@type="submit"]')
            submit_save.click()
        except Exception as e:
            logger.error(f"Error in set_balance_limit: {str(e)}")

    def non_cash(self, url: str) -> None:
        """
            Функция получает на вход ссылку на профиль водителя
            и меняет приходящие заказы только на безналичные
        """
        self.set_balance_limit(url, 50000)

    def noncash_or_cash(self, url: str) -> None:
        """ 
            Функция получает на вход ссылку на профиль водителя
            и меняет приходящие заказы на наличные и безналичные
        """
        self.set_balance_limit(url, 10)
        
    def set_working_conditions(self, url: str, comission: int) -> None:
        """
            Функция меняет условия работы в личном кабинете
        """
        try:
            self.driver.get(url)
            self.load_cookies()
            self.driver.refresh()
            sleep(5)
            
            # ищем элемент "условия работы"
            elem_select_control = ("class name", "Select__control.css-13cymwt-control")
            menu = self.wait.until(
                EC.presence_of_all_elements_located(elem_select_control)
            )
            # скролим до элемента в конце страницы
            sleep(5)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", menu[-1]) 
            # Нажимаем на элемент "условия работы"
            menu[-1].click()

            commission_15 = "Комиссия 1.5℅"
            commission_4_rubles = "Комиссия 4р с заказа"

            # Проверяем выбранную комиссию
            if comission == 1:
                # Создаем локатор с текстом комиссии
                working_condition_locator = f"//div[text()='{commission_15}']"
            elif comission == 4:
                # Создаем локатор с текстом комиссии
                working_condition_locator = f"//div[text()='{commission_4_rubles}']"
                
            # Ищем локатор с текстом комиссии
            working_condition = self.wait.until(
                EC.presence_of_element_located(("xpath", working_condition_locator))
            )
            # Кликаем 
            working_condition.click()
            
            #Сохраняем
            submit_save = self.driver.find_element('xpath', '//button[@type="submit"]')
            submit_save.click()
        except Exception as e:
            logger.error(f"Error in set_working_conditions: {str(e)}")
            
    def cancellations(self, full_name: str) -> None:
        """
            Функция отменяет заказы
            
            Parameters:
                self (YandexTaxiBot): The YandexTaxiBot object.
                full_name (str): The full name of the driver to cancel orders for.
                
            Returns: 
                None
        """
        try:
            url = "https://fleet.yandex.ru/map/drivers?statuses=in_order&sortBy=status_duration&sortDirection=desc&park_id=c0a8c5228fff4796abc901bcec379d45"
            self.driver.get(url)
            self.load_cookies()
            self.driver.refresh()
            
            xpath_drivers = ("xpath", f'//span[text()="{full_name}"]')
            driver_card = self.wait.until(
                EC.visibility_of_element_located(xpath_drivers)
            )
            self.driver.save_screenshot("driver_card.png")
            driver_card.click()

            xpath_order = ("xpath", '//span[text()="Перейти к заказу"]')
            go_order = self.wait.until(
                EC.presence_of_element_located(xpath_order)
            )
            self.driver.save_screenshot("go_order.png")
            go_order.click()

            self.driver.switch_to.window(self.driver.window_handles[1])

            xpath_cancel = ("xpath", '//span[text()="Отменить"]')
            cancel = self.wait.until(
                EC.presence_of_element_located(xpath_cancel)
            )
            sleep(3)
            self.driver.save_screenshot("cancellations.png")
            logger.info(f"Cancelling order for {full_name}.\n{cancel}")
            print(cancel)
            # cancel.click()
        except TimeoutException:
            logger.error("Func cancellations: Timeout waiting for an element to be present.")
        except NoSuchElementException:
            logger.error("Func cancellations: Element not found.")
        except NoSuchWindowException:
            logger.error("Func cancellations: No such window exception. Window switch might have failed.")
        except Exception as e:
            logger.error(f"Error in Cancellations: {str(e)}")
            
cl = YandexTaxiBot()
url = "https://fleet.yandex.ru/drivers/54cfac7bb46f48ecb1a45bdedea34252/details?park_id=c0a8c5228fff4796abc901bcec379d45"
comission = 1
s = cl.cancellations("Мясников Андрей Владимирович")