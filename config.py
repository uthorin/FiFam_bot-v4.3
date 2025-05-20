import os

class Config:
    def __init__(self):
        self.bot_token = self.require("BOT_TOKEN")
        self.db_host = self.require("DB_HOST")
        self.db_port = self.require("DB_PORT")
        self.db_name = self.require("DB_NAME")
        self.db_user = self.require("DB_USER")
        self.db_password = self.require("DB_PASSWORD")
        self.db_dsn = os.getenv("DB_DSN")
        self.openai_api_key = self.require("OPENAI_API_KEY")

        self.database_url = (
            f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def require(self, name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise ValueError(f"❌ Обязательная переменная окружения не найдена: {name}")
        return value

def load_config():
    return Config()
