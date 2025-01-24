from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER = os.getenv("MYSQL_USER", "sentiment_user")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "user_password")
    MYSQL_DB = os.getenv("MYSQL_DB", "sentiment_db")
    FLASK_ENV = os.getenv("FLASK_ENV")
