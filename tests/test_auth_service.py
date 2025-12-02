import pytest  # Импортируем фреймворк для тестирования pytest
from unittest.mock import patch, MagicMock  # Импортируем инструменты для создания моков
from werkzeug.security import generate_password_hash  # Импортируем функцию для хеширования паролей
from services.auth import AuthService  # Импортируем сервис аутентификации
from models.user import User  # Импортируем модель пользователя


@pytest.fixture
def mock_db_session():
    """Фикстура для мокирования сессии базы данных"""
    mock_session = MagicMock()  # Создаем мок объект сессии базы данных
    # Создаем мок контекстного менеджера, который будет возвращаться сессией
    mock_context = MagicMock()
    mock_session.__enter__.return_value = mock_context
    # Патчим функцию get_session в модуле services.auth, чтобы она возвращала наш мок
    # Это важно, так как мы тестируем именно AuthService, который использует эту функцию
    with patch('services.auth.get_session', return_value=mock_session):
        yield mock_context  # Возвращаем мок контекста для использования в тестах


class TestAuthService:
    def test_register_success(self, mock_db_session):
        """Тест успешной регистрации пользователя"""
        # Arrange - подготавливаем тестовые данные
        # Настраиваем мок, чтобы он возвращал None для проверок логина и email
        # Это имитирует ситуацию, когда пользователя с таким логином и email нет в базе
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [None, None]
        
        # Act - вызываем тестируемый метод
        result = AuthService.register("testuser", "password123", "student", "test@example.com")
        
        # Assert - проверяем результаты
        assert result is True  # Проверяем, что регистрация прошла успешно
        mock_db_session.add.assert_called_once()  # Проверяем, что метод add был вызван один раз
        mock_db_session.commit.assert_called_once()  # Проверяем, что изменения были сохранены
    
    def test_register_existing_login(self, mock_db_session):
        """Тест регистрации с уже существующим логином"""
        # Arrange - подготавливаем тестовые данные
        existing_user = MagicMock()  # Создаем мок существующего пользователя
        existing_user.login = "testuser"  # Устанавливаем логин
        # Настраиваем мок, чтобы он возвращал существующего пользователя при проверке логина
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_user
        
        # Act - вызываем тестируемый метод
        result = AuthService.register("testuser", "password123", "student", "test@example.com")
        
        # Assert - проверяем результаты
        assert result is False  # Проверяем, что регистрация не удалась
        mock_db_session.add.assert_not_called()  # Проверяем, что метод add не был вызван
        mock_db_session.commit.assert_not_called()  # Проверяем, что изменения не были сохранены
    
    def test_register_existing_email(self, mock_db_session):
        """Тест регистрации с уже существующим email"""
        # Arrange - подготавливаем тестовые данные
        # Настраиваем мок, чтобы он возвращал None для проверки логина (логин не существует)
        # и существующего пользователя для проверки email (email существует)
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [None, MagicMock()]
        
        # Act - вызываем тестируемый метод
        result = AuthService.register("newuser", "password123", "student", "existing@example.com")
        
        # Assert - проверяем результаты
        assert result is False  # Проверяем, что регистрация не удалась
        mock_db_session.add.assert_not_called()  # Проверяем, что метод add не был вызван
        mock_db_session.commit.assert_not_called()  # Проверяем, что изменения не были сохранены
    
    def test_login_success(self, mock_db_session):
        """Тест успешного входа в систему"""
        # Arrange - подготавливаем тестовые данные
        mock_user = MagicMock()  # Создаем мок пользователя
        mock_user.password = generate_password_hash("password123")  # Устанавливаем хешированный пароль
        mock_user.role = "student"  # Устанавливаем роль
        mock_user.id = 1  # Устанавливаем ID
        # Настраиваем мок, чтобы он возвращал пользователя при поиске по логину
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act - вызываем тестируемый метод
        success, role, user_id = AuthService.login("testuser", "password123")
        
        # Assert - проверяем результаты
        assert success is True  # Проверяем, что вход выполнен успешно
        assert role == "student"  # Проверяем, что роль соответствует ожидаемой
        assert user_id == 1  # Проверяем, что ID пользователя соответствует ожидаемому
    
    def test_login_wrong_password(self, mock_db_session):
        """Тест входа с неправильным паролем"""
        # Arrange - подготавливаем тестовые данные
        mock_user = MagicMock()  # Создаем мок пользователя
        mock_user.password = generate_password_hash("password123")  # Устанавливаем хешированный пароль
        # Настраиваем мок, чтобы он возвращал пользователя при поиске по логину
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Act - вызываем тестируемый метод с неправильным паролем
        success, role, user_id = AuthService.login("testuser", "wrongpassword")
        
        # Assert - проверяем результаты
        assert success is False  # Проверяем, что вход не выполнен
        assert role == ""  # Проверяем, что роль пустая
        assert user_id == 0  # Проверяем, что ID пользователя равен 0
    
    def test_login_user_not_found(self, mock_db_session):
        """Тест входа с несуществующим пользователем"""
        # Arrange - подготавливаем тестовые данные
        # Настраиваем мок, чтобы он возвращал None при поиске пользователя
        # Это имитирует ситуацию, когда пользователя с таким логином нет в базе
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        # Act - вызываем тестируемый метод
        success, role, user_id = AuthService.login("nonexistentuser", "password123")
        
        # Assert - проверяем результаты
        assert success is False  # Проверяем, что вход не выполнен
        assert role == ""  # Проверяем, что роль пустая
        assert user_id == 0  # Проверяем, что ID пользователя равен 0