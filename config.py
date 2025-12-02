import os
from pathlib import Path


class Config:
    # Настройки БД
    DB_USER = ""
    DB_PASSWORD = ""
    DB_HOST = ""
    DB_PORT = ""
    DB_NAME = ""

    # Пути
    BASE_DIR = Path(__file__).parent
    LOGS_PATH = BASE_DIR / "logs"

    # Логирование
    LOG_LEVEL = "DEBUG"
    LOG_MAX_SIZE = 1024 * 1024  # 1 MB
    LOG_BACKUP_COUNT = 5

    # Автоматическое создание необходимых директорий
    LOGS_PATH.mkdir(exist_ok=True, parents=True)

    @property
    def DB_URL(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
