from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from services import AuthService
from utils import show_error, show_info
from utils import get_logger
from views.register_window import RegisterWindow
from sqlalchemy.exc import SQLAlchemyError, OperationalError


logger = get_logger()


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.login_button = None
        self.username_input = None
        self.password_input = None
        self.btn_register = None
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Поля ввода
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Кнопка входа
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.authenticate)

        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

        self.btn_register = QPushButton("Зарегистрироваться")
        self.btn_register.clicked.connect(show_register)
        layout.addWidget(self.btn_register)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            show_error("Ошибка", "Заполните все поля!")
            return

        try:
            success, role, user_id = AuthService.login(username, password)
            if success:
                logger.info(f"Успешный вход пользователя: {username}")
                self.accept()
                self.role = role
                self.user_id = user_id
            else:
                show_error("Ошибка", "Неверные учетные данные")
        except OperationalError as e:
            logger.error(f"Ошибка подключения к базе данных: {str(e)}")
            show_error("Ошибка", "Не удалось подключиться к базе данных. Проверьте, что PostgreSQL запущен.")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка авторизации: {str(e)}")
            show_error("Ошибка", "Ошибка при работе с базой данных. Обратитесь к администратору.")


def show_register():
    register_window = RegisterWindow()
    if register_window.exec_() == QDialog.Accepted:
        show_info("Успех", "Теперь вы можете войти с новыми учетными данными")



