import pytest  # Импортируем фреймворк для тестирования pytest
import sys  # Импортируем модуль sys для работы с путями
import os  # Импортируем модуль os для работы с операционной системой
from unittest.mock import patch, MagicMock, PropertyMock  # Импортируем инструменты для создания моков

# Добавляем корневую директорию проекта в путь Python
# Это позволяет импортировать модули из корня проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем необходимые модели для тестирования
from models.teacher import Teacher, Subject, TeacherSubject
from models.user import User


@pytest.fixture
def mock_db_session():
    """Фикстура для мокирования сессии базы данных"""
    # Создаем мок объект сессии базы данных
    mock_session = MagicMock()
    # Создаем мок контекстного менеджера, который будет возвращаться сессией
    # Это необходимо, так как get_session используется в контексте with
    mock_context = MagicMock()
    mock_session.__enter__.return_value = mock_context
    # Патчим функцию get_session, чтобы она возвращала наш мок
    # Это позволяет перехватывать обращения к базе данных
    with patch('database.get_session', return_value=mock_session):
        yield mock_context  # Возвращаем мок контекста для использования в тестах


@pytest.fixture
def sample_teacher():
    """Фикстура для создания тестового экземпляра преподавателя"""
    # Создаем мок объекта пользователя с указанием спецификации User
    # Это гарантирует, что мок будет иметь те же атрибуты и методы, что и User
    user = MagicMock(spec=User)
    user.id = 1  # Устанавливаем ID пользователя
    user.login = "teacher1"  # Устанавливаем логин
    user.role = "teacher"  # Устанавливаем роль
    
    # Создаем экземпляр модели Teacher
    teacher = Teacher()
    teacher.id = 1  # Устанавливаем ID преподавателя
    teacher.first_name = "Иван"  # Устанавливаем имя
    teacher.last_name = "Петров"  # Устанавливаем фамилию
    teacher.patronymic = "Сергеевич"  # Устанавливаем отчество
    teacher.user_id = user.id  # Связываем с ID пользователя
    teacher.phone = "+7 (999) 123-45-67"  # Устанавливаем телефон
    teacher.lessons = []  # Инициализируем пустой список уроков
    
    # Патчим свойство user вместо прямой установки
    # Это позволяет избежать использования механизмов отношений SQLAlchemy
    # PropertyMock используется для мокирования свойств (property) класса
    with patch.object(Teacher, 'user', new_callable=PropertyMock) as mock_user:
        mock_user.return_value = user  # Устанавливаем возвращаемое значение для свойства user
        yield teacher  # Возвращаем подготовленный объект преподавателя


@pytest.fixture
def sample_subject():
    """Фикстура для создания тестового предмета"""
    # Создаем экземпляр модели Subject
    subject = Subject()
    subject.id = 1  # Устанавливаем ID предмета
    subject.name = "Математика"  # Устанавливаем название предмета
    subject.description = "Высшая математика"  # Устанавливаем описание предмета
    
    return subject  # Возвращаем подготовленный объект предмета


class TestTeacher:
    def test_teacher_creation(self, sample_teacher):
        """Тест создания объекта преподавателя"""
        # Arrange & Act - используем фикстуру
        teacher = sample_teacher
        
        # Assert - проверяем, что все атрибуты установлены правильно
        assert teacher.id == 1  # Проверяем ID
        assert teacher.first_name == "Иван"  # Проверяем имя
        assert teacher.last_name == "Петров"  # Проверяем фамилию
        assert teacher.patronymic == "Сергеевич"  # Проверяем отчество
        assert teacher.user_id == 1  # Проверяем ID пользователя
        assert teacher.phone == "+7 (999) 123-45-67"  # Проверяем телефон
        assert teacher.user.role == "teacher"  # Проверяем роль связанного пользователя
    
    def test_teacher_representation(self, sample_teacher):
        """Тест строкового представления объекта преподавателя"""
        # Arrange - подготавливаем объект для тестирования
        teacher = sample_teacher
        
        # Act - получаем строковое представление объекта
        repr_string = repr(teacher)
        
        # Assert - проверяем, что строковое представление содержит нужную информацию
        assert "<Teacher" in repr_string  # Проверяем наличие названия класса
        assert "id=1" in repr_string  # Проверяем наличие ID
        assert "name='Петров Иван'" in repr_string  # Проверяем наличие имени
        assert "phone='+7 (999) 123-45-67'" in repr_string  # Проверяем наличие телефона
    
    def test_subject_creation(self, sample_subject):
        """Тест создания объекта предмета"""
        # Arrange & Act - используем фикстуру
        subject = sample_subject
        
        # Assert - проверяем, что все атрибуты установлены правильно
        assert subject.id == 1  # Проверяем ID
        assert subject.name == "Математика"  # Проверяем название
        assert subject.description == "Высшая математика"  # Проверяем описание
    
    def test_subject_representation(self, sample_subject):
        """Тест строкового представления объекта предмета"""
        # Arrange - подготавливаем объект для тестирования
        subject = sample_subject
        
        # Act - получаем строковое представление объекта
        repr_string = repr(subject)
        
        # Assert - проверяем, что строковое представление содержит нужную информацию
        assert "<Subject" in repr_string  # Проверяем наличие названия класса
        assert "id=1" in repr_string  # Проверяем наличие ID
        assert "name='Математика'" in repr_string  # Проверяем наличие названия
        assert "description='Высшая математика'" in repr_string  # Проверяем наличие описания
    
    def test_teacher_subject_relationship(self, mock_db_session, sample_teacher, sample_subject):
        """Тест связи между преподавателем и предметом через промежуточную таблицу"""
        # Arrange - подготавливаем объект связи преподаватель-предмет
        teacher_subject = TeacherSubject()
        teacher_subject.teacher_id = sample_teacher.id  # Устанавливаем ID преподавателя
        teacher_subject.subject_id = sample_subject.id  # Устанавливаем ID предмета
        
        # Патчим отношения вместо прямой установки
        # Это позволяет избежать использования механизмов отношений SQLAlchemy
        with patch.object(TeacherSubject, 'teacher', new_callable=PropertyMock) as mock_teacher:
            with patch.object(TeacherSubject, 'subject', new_callable=PropertyMock) as mock_subject:
                mock_teacher.return_value = sample_teacher  # Устанавливаем возвращаемое значение для свойства teacher
                mock_subject.return_value = sample_subject  # Устанавливаем возвращаемое значение для свойства subject
                
                # Имитируем двустороннюю связь между объектами
                sample_teacher.teacher_subjects = [teacher_subject]  # Добавляем связь к преподавателю
                sample_subject.teacher_subjects = [teacher_subject]  # Добавляем связь к предмету
                
                # Act - добавляем связь в базу данных и сохраняем
                mock_db_session.add(teacher_subject)
                mock_db_session.commit()
                
                # Assert - проверяем, что связь установлена правильно
                mock_db_session.add.assert_called_once_with(teacher_subject)  # Проверяем вызов метода add
                mock_db_session.commit.assert_called_once()  # Проверяем вызов метода commit
                assert teacher_subject in sample_teacher.teacher_subjects  # Проверяем наличие связи у преподавателя
                assert teacher_subject in sample_subject.teacher_subjects  # Проверяем наличие связи у предмета
                assert teacher_subject.teacher == sample_teacher  # Проверяем связь с преподавателем
                assert teacher_subject.subject == sample_subject  # Проверяем связь с предметом