from functools import lru_cache

import dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    API_URL: str
    API_SECRET: str
    TELEGRAM_PROXY_URL: str | None = None

    def __init__(self):
        super().__init__(_env_file=None)


@lru_cache
def get_settings():
    if dotenv.find_dotenv():
        dotenv.load_dotenv()
    return Settings()
