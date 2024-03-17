import os
from dotenv import load_dotenv
from logger import logger
from data import sql

load_dotenv()

API_KEY = os.getenv("api_key")
CLID = os.getenv("clid")
API_KEY_MAP = os.getenv("API_KEY_MAP")

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

IP = os.getenv("IP")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")
DATABASE = os.getenv("DATABASE")

dsn = f"dbname={DATABASE} user={PGUSER} password={PGPASSWORD} host={IP}"
db = sql.DataBase(dsn)