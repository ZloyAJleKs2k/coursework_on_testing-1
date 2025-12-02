from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import openpyxl
from config import Config
from PyQt5.QtCore import QObject, pyqtSignal
import os


class ReportGenerator(QObject):
    progress_updated = pyqtSignal(int)  # Для отслеживания прогресса
    
    def __init__(self):
        super().__init__()
        # Регистрируем шрифт с поддержкой кириллицы
        font_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')
        if not os.path.exists(font_path):
            os.makedirs(font_path)
            
        # Проверяем наличие шрифта DejaVuSans
        dejavu_path = os.path.join(font_path, 'DejaVuSans.ttf')
        if not os.path.exists(dejavu_path):
            # Если шрифта нет, используем Arial из системы Windows
            windows_font_path = os.path.join(os.environ['WINDIR'], 'Fonts', 'arial.ttf')
            if os.path.exists(windows_font_path):
                pdfmetrics.registerFont(TTFont('CustomFont', windows_font_path))
            else:
                # Если Arial не найден, используем стандартный Helvetica
                pass
        else:
            pdfmetrics.registerFont(TTFont('CustomFont', dejavu_path))

    def generate_attendance_pdf(self, data: list, filename: str) -> bool:
        """Генерация PDF-отчета"""
        try:
            # Use the filename directly or create a path in the reports directory
            if ':' in filename or filename.startswith('/'):
                file_path = filename
            else:
                reports_dir = Config.BASE_DIR / "ОТчеты"
                reports_dir.mkdir(exist_ok=True, parents=True)
                file_path = f"{reports_dir}/{filename}"
                
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4
            )

            # Создание таблицы с динамическими заголовками
            if not data:
                return False
                
            # Получаем ключи из первого элемента данных, фильтруя метаданные
            keys = [key for key in data[0].keys() if not key.startswith('_')]
            # Получаем заголовки (значения) для каждого ключа - используем русские названия
            headers = [data[0].get(f'_header_{key}', key) for key in keys]
            
            # Создание таблицы с динамическими заголовками
            table_data = [headers]
            
            # Добавление данных
            for item in data:
                row = []
                for key in keys:
                    # Добавляем % к полю attendance, если оно существует
                    if key == 'attendance':
                        row.append(f"{item[key]}%")
                    else:
                        row.append(item[key])
                table_data.append(row)

            table = Table(table_data)
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'CustomFont'),
                ('FONTNAME', (0, 1), (-1, -1), 'CustomFont'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ENCODING', (0, 0), (-1, -1), 'utf-8')
            ])

            table.setStyle(style)
            doc.build([table])
            return True
        except Exception as e:
            print(f"PDF generation error: {str(e)}")
            return False

    def generate_attendance_excel(self, data: list, filename: str) -> bool:
        """Генерация Excel-отчета"""
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Отчет"

            if not data:
                return False
                
            # Получаем ключи из первого элемента данных, фильтруя метаданные
            keys = [key for key in data[0].keys() if not key.startswith('_')]
            
            # Заголовки (используем русские названия как заголовки)
            headers = [data[0].get(f'_header_{key}', key) for key in keys]
            ws.append(headers)

            # Данные
            for item in data:
                row = [item[key] for key in keys]
                ws.append(row)
                
            # Use the filename directly or create a path in the reports directory
            if ':' in filename or filename.startswith('/'):
                file_path = filename
            else:
                reports_dir = Config.BASE_DIR / "ОТчеты"
                reports_dir.mkdir(exist_ok=True, parents=True)
                file_path = f"{reports_dir}/{filename}"
                
            wb.save(file_path)
            return True
        except Exception as e:
            print(f"Excel generation error: {str(e)}")
            return False

