from PyQt5.QtWidgets import QFileDialog
from utils import show_error, show_info, get_logger

logger = get_logger()

def export_report(parent, table, columns, report_generator, pdf_radio):
    """
    Универсальная функция для экспорта отчетов
    
    Args:
        parent: Родительский виджет для диалога сохранения
        table: Таблица с данными для экспорта
        columns: Словарь с названиями колонок и их ключами для экспорта
        report_generator: Экземпляр класса ReportGenerator
        pdf_radio: Радиокнопка для выбора PDF формата
        
    Returns:
        bool: Успешность экспорта
    """
    try:
        # Подготовка данных для экспорта
        data = []
        for row in range(table.rowCount()):
            row_data = {}
            for col_idx, (key, header) in enumerate(columns.items()):
                row_data[key] = table.item(row, col_idx).text()
                # Добавляем русское название колонки как метаданные
                row_data[f'_header_{key}'] = header
            data.append(row_data)
        
        if not data:
            show_error("Ошибка", "Нет данных для экспорта")
            return False
        
        # Выбор формата и экспорт
        file_format = "pdf" if pdf_radio.isChecked() else "xlsx"
        filename, _ = QFileDialog.getSaveFileName(
            parent, "Сохранить отчет", "", 
            f"PDF Files (*.pdf);;Excel Files (*.xlsx)" if file_format == "pdf" else "Excel Files (*.xlsx);;PDF Files (*.pdf)"
        )
        
        if not filename:
            return False
            
        if file_format == "pdf" and not filename.endswith(".pdf"):
            filename += ".pdf"
        elif file_format == "xlsx" and not filename.endswith(".xlsx"):
            filename += ".xlsx"
        
        # Экспорт в выбранный формат
        if file_format == "pdf":
            success = report_generator.generate_attendance_pdf(data, filename)
        else:
            success = report_generator.generate_attendance_excel(data, filename)
            
        if success:
            show_info("Успех", "Отчет успешно экспортирован")
        else:
            show_error("Ошибка", "Не удалось экспортировать отчет")
            
        return success
    except Exception as e:
        logger.error(f"Ошибка экспорта отчета: {str(e)}")
        show_error("Ошибка", "Не удалось экспортировать отчет")
        return False