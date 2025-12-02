from functools import wraps
from PyQt5.QtWidgets import QMessageBox
from database import get_session
from models.user import User
from utils import get_logger  # Прямой импорт из конкретного модуля
from utils import show_error  # Прямой импорт

logger = get_logger()


def admin_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with get_session() as db:  # Получаем сессию базы данных
            user = db.query(User).get(self.current_user_id)  # Получаем пользователя по ID
            if not user:
                logger.error(f"User  not found with id {self.current_user_id}")
                show_error("Ошибка", "Пользователь не найден")
                return
            if user.role != 'admin':
                logger.info(f"Access denied for user {user.login} with role {user.role}")
                # show_error("Ошибка", "Доступ запрещен")
                return
        return func(self, *args, **kwargs)

    return wrapper


def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            show_error("Ошибка", f"Произошла ошибка: {str(e)}")

    return wrapper
