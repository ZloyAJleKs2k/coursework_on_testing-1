from PyQt5.QtWidgets import (QDialog, QVBoxLayout,
                             QLineEdit, QPushButton, QLabel,
                             QMessageBox)
from services.auth import AuthService
from utils import show_info, show_error
from utils.logger import get_logger

logger = get_logger()


class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.username_input = None
        self.password_input = None
        self.confirm_password_input = None
        self.email_input = None  # Добавлено поле для электронной почты
        self.btn_register = None
        self.setWindowTitle("Регистрация")
        self.setFixedSize(300, 300)  # Увеличиваем размер окна для нового поля
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Подтвердите пароль")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.email_input = QLineEdit()  # Инициализация поля для электронной почты
        self.email_input.setPlaceholderText("Электронная почта")

        self.btn_register = QPushButton("Зарегистрироваться")
        self.btn_register.clicked.connect(self.register)

        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Подтверждение пароля:"))
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(QLabel("Электронная почта:"))  # Метка для поля электронной почты
        layout.addWidget(self.email_input)  # Добавляем поле для электронной почты
        layout.addWidget(self.btn_register)

        self.setLayout(layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        email = self.email_input.text()  # Получаем значение электронной почты

        if not username or not password or not email:  # Проверка на заполнение всех полей
            show_error("Ошибка", "Заполните все обязательные поля!")
            return

        if password != confirm_password:
            show_error("Ошибка", "Пароли не совпадают!")
            return

        try:
            success = AuthService.register(username, password, "student", email)  # Передаем email в AuthService
            if success:
                show_info("Успех", "Регистрация прошла успешно!")
                self.accept()
            else:
                show_error("Ошибка", "Пользователь с таким логином или электронной почтой уже существует")
        except Exception as e:
            logger.error(f"Ошибка регистрации: {str(e)}")
            show_error("Ошибка", "Ошибка при регистрации")


