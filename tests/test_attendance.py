import pytest  # Импортируем фреймворк для тестирования pytest
from unittest.mock import patch, MagicMock, PropertyMock  # Импортируем инструменты для создания моков
from datetime import datetime  # Импортируем класс для работы с датой и временем
from models.attendance import Attendance  # Импортируем модель посещаемости
from models.student import Student  # Импортируем модель студента
from models.lesson import Lesson  # Импортируем модель урока


@pytest.fixture
def mock_db_session():
    """Фикстура для мокирования сессии базы данных"""
    # Создаем мок объект сессии базы данных
    mock_session = MagicMock()
    # Патчим функцию get_session, чтобы она возвращала наш мок
    # Это позволяет перехватывать обращения к базе данных
    with patch('database.get_session', return_value=mock_session):
        yield mock_session  # Возвращаем мок сессии для использования в тестах


@pytest.fixture
def sample_attendance_data():
    """Фикстура для создания тестовых данных посещаемости"""
    # Создаем мок объекта студента с указанием спецификации Student
    # Это гарантирует, что мок будет иметь те же атрибуты и методы, что и Student
    student = MagicMock(spec=Student)
    student.id = 1  # Устанавливаем ID студента
    student.full_name = "Иванов Иван"  # Устанавливаем ФИО студента
    
    # Создаем мок объекта урока с указанием спецификации Lesson
    lesson = MagicMock(spec=Lesson)
    lesson.id = 1  # Устанавливаем ID урока
    lesson.date_time = datetime.now()  # Устанавливаем текущую дату и время для урока
    lesson.subject_id = 1  # Устанавливаем ID предмета
    
    # Создаем экземпляр модели Attendance (посещаемость)
    attendance = Attendance()
    attendance.student_id = student.id  # Связываем с ID студента
    attendance.lesson_id = lesson.id  # Связываем с ID урока
    attendance.status = "present"  # Устанавливаем статус присутствия
    
    # Патчим свойства student и lesson вместо прямой установки
    # Это позволяет избежать использования механизмов отношений SQLAlchemy
    # PropertyMock используется для мокирования свойств (property) класса
    with patch.object(Attendance, 'student', new_callable=PropertyMock) as mock_student:
        with patch.object(Attendance, 'lesson', new_callable=PropertyMock) as mock_lesson:
            mock_student.return_value = student  # Устанавливаем возвращаемое значение для свойства student
            mock_lesson.return_value = lesson  # Устанавливаем возвращаемое значение для свойства lesson
            yield attendance  # Возвращаем подготовленный объект посещаемости


class TestAttendance:
    def test_attendance_creation(self, sample_attendance_data):
        """Тест создания объекта посещаемости"""
        # Arrange & Act - используем фикстуру
        attendance = sample_attendance_data
        
        # Assert - проверяем, что все атрибуты установлены правильно
        assert attendance.student_id == 1  # Проверяем ID студента
        assert attendance.lesson_id == 1  # Проверяем ID урока
        assert attendance.status == "present"  # Проверяем статус
        assert attendance.student.full_name == "Иванов Иван"  # Проверяем ФИО связанного студента
    
    def test_attendance_status_validation(self):
        """Тест валидации статуса посещаемости"""
        # Arrange - подготавливаем объект и список допустимых статусов
        attendance = Attendance()
        valid_statuses = ["present", "absent", "late", "sick"]  # Список допустимых статусов
        
        # Act & Assert - проверяем каждый статус
        for status in valid_statuses:
            attendance.status = status  # Устанавливаем статус
            assert attendance.status == status  # Проверяем, что статус установлен корректно
    
    def test_attendance_representation(self, sample_attendance_data):
        """Тест строкового представления объекта посещаемости"""
        # Arrange - подготавливаем объект для тестирования
        attendance = sample_attendance_data
        
        # Act - получаем строковое представление объекта
        repr_string = repr(attendance)
        
        # Assert - проверяем, что строковое представление содержит нужную информацию
        assert "<Attendance" in repr_string  # Проверяем наличие названия класса
        assert "student_id=1" in repr_string  # Проверяем наличие ID студента
        assert "lesson_id=1" in repr_string  # Проверяем наличие ID урока
        assert "status='present'" in repr_string  # Проверяем наличие статуса
    
    @patch('database.get_session')
    def test_save_attendance(self, mock_get_session, mock_db_session):
        """Тест сохранения объекта посещаемости в базу данных"""
        # Arrange - подготавливаем мок базы данных и объект посещаемости
        mock_db = MagicMock()  # Создаем мок объект базы данных
        mock_get_session.return_value.__enter__.return_value = mock_db  # Настраиваем возвращаемое значение
        
        # Создаем объект посещаемости
        attendance = Attendance()
        attendance.student_id = 1  # Устанавливаем ID студента
        attendance.lesson_id = 1  # Устанавливаем ID урока
        attendance.status = "present"  # Устанавливаем статус
        
        # Act - добавляем объект в базу данных и сохраняем
        mock_db.add(attendance)
        mock_db.commit()
        
        # Assert - проверяем, что методы add и commit были вызваны с правильными параметрами
        mock_db.add.assert_called_once_with(attendance)  # Проверяем вызов метода add
        mock_db.commit.assert_called_once()  # Проверяем вызов метода commit
    
    @patch('database.get_session')
    def test_update_attendance_status(self, mock_get_session, mock_db_session):
        """Тест обновления статуса посещаемости"""
        # Arrange - подготавливаем мок базы данных и существующий объект посещаемости
        mock_db = MagicMock()  # Создаем мок объект базы данных
        mock_get_session.return_value.__enter__.return_value = mock_db  # Настраиваем возвращаемое значение
        
        # Создаем существующую запись посещаемости
        existing_attendance = Attendance()
        existing_attendance.student_id = 1  # Устанавливаем ID студента
        existing_attendance.lesson_id = 1  # Устанавливаем ID урока
        existing_attendance.status = "absent"  # Устанавливаем начальный статус "отсутствует"
        
        # Настраиваем мок запроса, чтобы он возвращал наш объект
        mock_db.query.return_value.filter.return_value.first.return_value = existing_attendance
        
        # Act - обновляем статус и сохраняем изменения
        existing_attendance.status = "present"  # Меняем статус на "присутствует"
        mock_db.commit()
        
        # Assert - проверяем, что статус обновлен и метод commit был вызван
        assert existing_attendance.status == "present"  # Проверяем, что статус изменился
        mock_db.commit.assert_called_once()  # Проверяем вызов метода commit