from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import Config

# Инициализация подключения
engine = create_engine(
    Config().DB_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    echo=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

# Используем scoped_session для автоматического управления сессиями
db_session = scoped_session(SessionLocal)


def get_session():
    """Возвращает новую сессию БД"""
    return SessionLocal()


def close_session(exception=None):
    """Закрывает сессию (для использования в контекстных менеджерах)"""
    db_session.remove()
