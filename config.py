from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_DB = os.getenv("MYSQL_DB")
    FLASK_ENV = os.getenv("FLASK_ENV")
