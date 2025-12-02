import pytest  # Импортируем фреймворк для тестирования pytest
from unittest.mock import patch, MagicMock, mock_open  # Импортируем инструменты для создания моков
import os  # Импортируем модуль os для работы с операционной системой
from services.report_generator import ReportGenerator  # Импортируем тестируемый класс генератора отчетов


@pytest.fixture
def report_generator():
    """Фикстура для создания экземпляра ReportGenerator"""
    # Используем множественные патчи для изоляции тестов от внешних зависимостей
    # Патчим registerFont из reportlab.pdfbase.pdfmetrics, чтобы не регистрировать реальные шрифты
    with patch('services.report_generator.pdfmetrics.registerFont'):
        # Патчим os.path.exists, чтобы всегда возвращал True при проверке существования файлов
        with patch('services.report_generator.os.path.exists', return_value=True):
            # Патчим TTFont из reportlab.pdfbase.ttfonts, чтобы не загружать реальные шрифты
            with patch('services.report_generator.TTFont'):
                # Патчим os.environ для имитации переменных окружения Windows
                with patch('services.report_generator.os.environ', {'WINDIR': 'C:\\Windows'}):
                    # Патчим os.path.join, чтобы всегда возвращал фиксированный путь
                    with patch('services.report_generator.os.path.join', return_value='dummy_path'):
                        # Возвращаем экземпляр ReportGenerator для использования в тестах
                        yield ReportGenerator()


@pytest.fixture
def sample_data():
    """Фикстура с тестовыми данными для генерации отчетов"""
    # Возвращаем список словарей с данными о посещаемости
    # Каждый словарь содержит информацию о студенте, предмете, дате, статусе и преподавателе
    # Также включены заголовки для колонок отчета (с префиксом _header_)
    return [
        {
            'student_name': 'Иванов Иван',  # ФИО студента
            'subject': 'Математика',  # Название предмета
            'date': '2023-05-01',  # Дата занятия
            'status': 'Присутствовал',  # Статус посещения
            'teacher': 'Петров П.П.',  # ФИО преподавателя
            '_header_student_name': 'Студент',  # Заголовок колонки для ФИО студента
            '_header_subject': 'Предмет',  # Заголовок колонки для названия предмета
            '_header_date': 'Дата',  # Заголовок колонки для даты
            '_header_status': 'Статус',  # Заголовок колонки для статуса
            '_header_teacher': 'Преподаватель'  # Заголовок колонки для ФИО преподавателя
        },
        {
            'student_name': 'Сидоров Сидор',  # ФИО студента
            'subject': 'Математика',  # Название предмета
            'date': '2023-05-01',  # Дата занятия
            'status': 'Отсутствовал',  # Статус посещения
            'teacher': 'Петров П.П.',  # ФИО преподавателя
            '_header_student_name': 'Студент',  # Заголовок колонки для ФИО студента
            '_header_subject': 'Предмет',  # Заголовок колонки для названия предмета
            '_header_date': 'Дата',  # Заголовок колонки для даты
            '_header_status': 'Статус',  # Заголовок колонки для статуса
            '_header_teacher': 'Преподаватель'  # Заголовок колонки для ФИО преподавателя
        }
    ]


class TestReportGenerator:
    def test_generate_attendance_pdf_success(self, report_generator, sample_data):
        """Тест успешной генерации PDF-отчета о посещаемости"""
        # Arrange - подготавливаем тестовое окружение
        # Патчим классы из reportlab для работы с PDF
        with patch('services.report_generator.SimpleDocTemplate') as mock_doc:
            with patch('services.report_generator.Table') as mock_table:
                with patch('services.report_generator.TableStyle') as mock_style:
                    with patch('services.report_generator.Config') as mock_config:
                        # Настраиваем моки
                        mock_config.BASE_DIR = MagicMock()  # Мокируем базовую директорию
                        mock_table_instance = mock_table.return_value  # Получаем экземпляр мока таблицы
                        mock_doc_instance = mock_doc.return_value  # Получаем экземпляр мока документа
                        
                        # Act - вызываем тестируемый метод
                        result = report_generator.generate_attendance_pdf(sample_data, "test_report.pdf")
                        
                        # Assert - проверяем результаты
                        assert result is True  # Проверяем, что метод вернул True (успешное выполнение)
                        mock_table.assert_called_once()  # Проверяем, что была создана таблица
                        mock_table_instance.setStyle.assert_called_once()  # Проверяем, что был установлен стиль таблицы
                        mock_doc_instance.build.assert_called_once()  # Проверяем, что документ был построен
    
    def test_generate_attendance_pdf_empty_data(self, report_generator):
        """Тест генерации PDF-отчета с пустыми данными"""
        # Act - вызываем тестируемый метод с пустым списком данных
        result = report_generator.generate_attendance_pdf([], "test_report.pdf")
        
        # Assert - проверяем результаты
        assert result is False  # Проверяем, что метод вернул False (неуспешное выполнение)
    
    def test_generate_attendance_pdf_exception(self, report_generator, sample_data):
        """Тест обработки исключений при генерации PDF-отчета"""
        # Arrange - подготавливаем тестовое окружение
        # Патчим SimpleDocTemplate, чтобы он вызывал исключение
        with patch('services.report_generator.SimpleDocTemplate') as mock_doc:
            mock_doc.side_effect = Exception("Test exception")  # Настраиваем мок на вызов исключения
            
            # Act - вызываем тестируемый метод
            result = report_generator.generate_attendance_pdf(sample_data, "test_report.pdf")
            
            # Assert - проверяем результаты
            assert result is False  # Проверяем, что метод вернул False (неуспешное выполнение)
    
    def test_generate_attendance_excel_success(self, report_generator, sample_data):
        """Тест успешной генерации Excel-отчета о посещаемости"""
        # Arrange - подготавливаем тестовое окружение
        # Патчим openpyxl.Workbook для работы с Excel
        with patch('services.report_generator.openpyxl.Workbook') as mock_workbook:
            with patch('services.report_generator.Config') as mock_config:
                # Настраиваем моки
                mock_config.BASE_DIR = MagicMock()  # Мокируем базовую директорию
                mock_wb = MagicMock()  # Создаем мок рабочей книги
                mock_ws = MagicMock()  # Создаем мок рабочего листа
                mock_workbook.return_value = mock_wb  # Настраиваем возвращаемое значение
                mock_wb.active = mock_ws  # Устанавливаем активный лист
                
                # Act - вызываем тестируемый метод
                result = report_generator.generate_attendance_excel(sample_data, "test_report.xlsx")
                
                # Assert - проверяем результаты
                assert result is True  # Проверяем, что метод вернул True (успешное выполнение)
                mock_ws.append.assert_called()  # Проверяем, что данные были добавлены в лист
                mock_wb.save.assert_called_once()  # Проверяем, что файл был сохранен
    
    def test_generate_attendance_excel_empty_data(self, report_generator):
        """Тест генерации Excel-отчета с пустыми данными"""
        # Act - вызываем тестируемый метод с пустым списком данных
        result = report_generator.generate_attendance_excel([], "test_report.xlsx")
        
        # Assert - проверяем результаты
        assert result is False  # Проверяем, что метод вернул False (неуспешное выполнение)
    
    def test_generate_attendance_excel_exception(self, report_generator, sample_data):
        """Тест обработки исключений при генерации Excel-отчета"""
        # Arrange - подготавливаем тестовое окружение
        # Патчим openpyxl.Workbook, чтобы он вызывал исключение
        with patch('services.report_generator.openpyxl.Workbook') as mock_workbook:
            mock_workbook.side_effect = Exception("Test exception")  # Настраиваем мок на вызов исключения
            
            # Act - вызываем тестируемый метод
            result = report_generator.generate_attendance_excel(sample_data, "test_report.xlsx")
            
            # Assert - проверяем результаты
            assert result is False  # Проверяем, что метод вернул False (неуспешное выполнение)