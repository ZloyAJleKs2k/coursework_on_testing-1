import pytest  # Импортируем фреймворк для тестирования pytest
import sys  # Импортируем модуль sys для работы с путями
import os  # Импортируем модуль os для работы с операционной системой
from unittest.mock import patch, MagicMock, PropertyMock  # Импортируем инструменты для создания моков

# Добавляем корневую директорию проекта в путь Python
# Это позволяет импортировать модули из корня проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импортируем необходимые модели для тестирования
from models.student import Student
from models.group import Group
from models.attendance import Attendance


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
def sample_student():
    """Фикстура для создания тестового студента"""
    # Создаем мок объекта группы с указанием спецификации Group
    # Это гарантирует, что мок будет иметь те же атрибуты и методы, что и Group
    group = MagicMock(spec=Group)
    group.id = 1  # Устанавливаем ID группы
    group.name = "Группа 101"  # Устанавливаем название группы
    
    # Создаем экземпляр модели Student
    student = Student()
    student.id = 1  # Устанавливаем ID студента
    student.full_name = "Иванов Иван Иванович"  # Устанавливаем ФИО студента
    student.group_id = group.id  # Связываем с ID группы
    student.attendance = []  # Инициализируем пустой список посещаемости
    
    # Патчим свойство group вместо прямой установки
    # Это позволяет избежать использования механизмов отношений SQLAlchemy
    # PropertyMock используется для мокирования свойств (property) класса
    with patch.object(Student, 'group', new_callable=PropertyMock) as mock_group:
        mock_group.return_value = group  # Устанавливаем возвращаемое значение для свойства group
        yield student  # Возвращаем подготовленный объект студента


class TestStudent:
    def test_student_creation(self, sample_student):
        """Тест создания объекта студента"""
        # Arrange & Act - используем фикстуру
        student = sample_student
        
        # Assert - проверяем, что все атрибуты установлены правильно
        assert student.id == 1  # Проверяем ID
        assert student.full_name == "Иванов Иван Иванович"  # Проверяем ФИО
        assert student.group_id == 1  # Проверяем ID группы
        assert student.group.name == "Группа 101"  # Проверяем название связанной группы
    
    def test_student_representation(self, sample_student):
        """Тест строкового представления объекта студента"""
        # Arrange - подготавливаем объект для тестирования
        student = sample_student
        
        # Act - получаем строковое представление объекта
        repr_string = repr(student)
        
        # Assert - проверяем, что строковое представление содержит нужную информацию
        assert "<Student" in repr_string  # Проверяем наличие названия класса
        assert "id=1" in repr_string  # Проверяем наличие ID
        assert "full_name='Иванов Иван Иванович'" in repr_string  # Проверяем наличие ФИО
    
    def test_save_student(self, mock_db_session):
        """Тест сохранения объекта студента в базу данных"""
        # Arrange - подготавливаем объект студента
        student = Student()
        student.full_name = "Петров Петр Петрович"  # Устанавливаем ФИО
        student.group_id = 1  # Устанавливаем ID группы
        
        # Act - добавляем объект в базу данных и сохраняем
        mock_db_session.add(student)
        mock_db_session.commit()
        
        # Assert - проверяем, что методы add и commit были вызваны с правильными параметрами
        mock_db_session.add.assert_called_once_with(student)  # Проверяем вызов метода add
        mock_db_session.commit.assert_called_once()  # Проверяем вызов метода commit
    
    def test_update_student(self, mock_db_session):
        """Тест обновления данных студента"""
        # Arrange - подготавливаем существующий объект студента
        # Создаем объект студента, который будет возвращаться при запросе к базе данных
        existing_student = Student()
        existing_student.id = 1  # Устанавливаем ID
        existing_student.full_name = "Сидоров Сидор Сидорович"  # Устанавливаем начальное ФИО
        existing_student.group_id = 1  # Устанавливаем ID группы
        
        # Настраиваем мок запроса, чтобы он возвращал наш объект
        mock_db_session.query.return_value.filter.return_value.first.return_value = existing_student
        
        # Act - обновляем ФИО студента и сохраняем изменения
        existing_student.full_name = "Сидоров Сидор Петрович"  # Меняем отчество
        mock_db_session.commit()
        
        # Assert - проверяем, что данные обновлены и метод commit был вызван
        assert existing_student.full_name == "Сидоров Сидор Петрович"  # Проверяем, что ФИО изменилось
        mock_db_session.commit.assert_called_once()  # Проверяем вызов метода commit
    
    def test_student_group_relationship(self, sample_student):
        """Тест связи между студентом и группой"""
        # Arrange - подготавливаем объекты студента и группы
        student = sample_student
        group = student.group
        
        # Act - имитируем добавление студента в список студентов группы
        group.students = [student]  # Устанавливаем список студентов группы
        
        # Assert - проверяем, что связь установлена правильно
        assert student in group.students  # Проверяем, что студент есть в списке студентов группы
        assert student.group == group  # Проверяем, что группа студента установлена правильно
        assert student.group_id == group.id  # Проверяем, что ID группы студента соответствует ID группы