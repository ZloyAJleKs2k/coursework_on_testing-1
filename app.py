import sys
from PyQt5 import QtWidgets
from sqlalchemy import text
from database import engine, db_session, close_session
from models import Base
from views import LoginWindow
from views import MainWindow
from utils import get_logger

logger = get_logger()

if __name__ == "__main__":
    try:
        # Создаем таблицы при первом запуске
        Base.metadata.create_all(bind=engine)

        # Проверка подключения
        with db_session() as session:
            session.execute(text("SELECT 1"))  # Обернули в text()
            logger.info("Database connection successful")

        app = QtWidgets.QApplication(sys.argv)

        # # Загрузка стилей
        # with open("styles.qss", "r") as f:
        #     app.setStyleSheet(f.read())
        # app.aboutToQuit.connect(close_session)  # Автоматическое закрытие сессий

        login_window = LoginWindow()
        if login_window.exec_() == QtWidgets.QDialog.Accepted:
            main_window = MainWindow(role=login_window.role, user_id=login_window.user_id)
            main_window.show()
            sys.exit(app.exec_())

    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}")
        QtWidgets.QMessageBox.critical(
            None,
            "Ошибка запуска",
            f"Не удалось запустить приложение: {str(e)}"
        )
    finally:
        close_session()


