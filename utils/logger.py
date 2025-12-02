import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import Config
import os


class Logger:
    def __init__(self, name: str = "AttendanceSystem"):
        self._logger = self._setup_logger(name)

    def _setup_logger(self, name: str) -> logging.Logger:
        """Настройка и получение логгера"""
        logger = logging.getLogger(name)

        if logger.hasHandlers():
            return logger

        logger.setLevel(logging.DEBUG)

        # Формат сообщений
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Консольный вывод
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Файловый вывод с ротацией
        logs_dir = Config().LOGS_PATH
        logs_dir.mkdir(exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=logs_dir / "app.log",
            maxBytes=Config().LOG_MAX_SIZE,
            backupCount=Config().LOG_BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def debug(self, message: str):
        self._logger.debug(message)

    def info(self, message: str):
        self._logger.info(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def critical(self, message: str):
        self._logger.critical(message)


def get_logger():
    return Logger()

