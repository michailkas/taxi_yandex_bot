import psycopg2


class DataBase:
    def __init__(self, dsn): # подключение к бд
        self.connection = psycopg2.connect(dsn)
        self.cursor = self.connection.cursor() 

    def create_table_orders(self): # создает бд если ее нет
        with self.connection:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY NOT NULL,
                    fio TEXT NOT NULL,
                    address_1 TEXT NOT NULL,
                    address_2 TEXT NOT NULL,
                    latitude_1 REAL NOT NULL,
                    longitude_1 REAL NOT NULL,
                    latitude_2 REAL NOT NULL,
                    longitude_2 REAL NOT NULL,
                    price REAL NOT NULL
                );
            ''')
    
    def create_table_drivers(self): # создает бд если ее нет
        with self.connection:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS drivers (
                    id SERIAL PRIMARY KEY NOT NULL,
                    fio TEXT NOT NULL,
                    username_tg TEXT,
                    id_tg BIGINT NOT NULL,
                    link_profile TEXT NOT NULL
                );
            ''')
    
    def get_driver_fio_profile(self, id_tg: int):
        with self.connection:
            self.cursor.execute('''
                    SELECT fio FROM drivers
                    WHERE id_tg = %s;
                ''', (id_tg,))

            existing_record = self.cursor.fetchone()
            return existing_record
    
    def get_driver_profile(self, fio: str):
        with self.connection:
            self.cursor.execute('''
                    SELECT id_tg FROM drivers
                    WHERE fio = %s;
                ''', (fio,))

            existing_record = self.cursor.fetchone()
            return existing_record
    
    def get_link_profile(self, id):
        with self.connection:
            self.cursor.execute('''
                    SELECT link_profile FROM drivers
                    WHERE id_tg = %s;
                ''', (id,))

            existing_record = self.cursor.fetchone()
            return existing_record
    
    def checking_data_table(self, driver):
        with self.connection:
            self.cursor.execute('''
                    SELECT id FROM orders
                    WHERE fio = %s AND address_1 = %s AND address_2 = %s;
                ''', (driver.get("ФИО", ""), driver.get('1 улица', ''), driver.get('2 улица', '')))

            existing_record = self.cursor.fetchone()
            return existing_record
            
    def add_order_to_database(self, driver):
        # Добавление заказа в таблицу
        with self.connection:
            self.cursor.execute('''
                INSERT INTO orders (fio, address_1, address_2, latitude_1, longitude_1, latitude_2, longitude_2, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            ''', (driver.get('ФИО', ''), driver.get('1 улица', ''), driver.get('2 улица', ''),
                driver['координаты 1 улицы'].get('longitude', 0), driver['координаты 1 улицы'].get('latitude', 0),
                driver['координаты 2 улицы'].get('longitude', 0), driver['координаты 2 улицы'].get('latitude', 0),
                driver.get('цена', 0))
            )

    def add_driver_to_database(self, fio, username, id, link):
        # Добавление водителя в таблицу
        with self.connection:
            self.cursor.execute('''
                INSERT INTO drivers (fio, username_tg, id_tg, link_profile)
                VALUES (%s, %s, %s, %s);
            ''', (fio, username, id, link)
            )
    