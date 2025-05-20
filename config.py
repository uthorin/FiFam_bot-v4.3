from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()
        self.bot_token = os.getenv("BOT_TOKEN")
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_dsn = os.getenv("DB_DSN")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        # 👇 Добавлено: строка подключения для asyncpg
        self.database_url = (
            f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

def load_config():
    return Config()
