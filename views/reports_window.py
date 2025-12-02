from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QComboBox, QLabel, QDateEdit, QFileDialog,
                             QHeaderView, QMessageBox, QGroupBox, QRadioButton)
from PyQt5.QtCore import Qt, QDate
from database import get_session
from models import Student, Attendance, Lesson, Teacher, Subject, Group
from utils import show_error, show_info, handle_exceptions, get_logger, export_report
from services.report_generator import ReportGenerator
from sqlalchemy.sql import func, case
from datetime import datetime, timedelta

logger = get_logger()


class ReportsWindow(QWidget):
    def __init__(self, role='student', user_id=None):
        super().__init__()
        self.role = role
        self.user_id = user_id
        self.report_generator = ReportGenerator()
        self.init_ui()

    @handle_exceptions
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget for different report types
        self.tabs = QTabWidget()
        
        # Create tabs for each report type
        self.student_attendance_tab = self.create_student_attendance_tab()
        self.group_attendance_tab = self.create_group_attendance_tab()
        self.teacher_lessons_tab = self.create_teacher_lessons_tab()
        self.group_size_tab = self.create_group_size_tab()
        self.date_attendance_tab = self.create_date_attendance_tab()
        
        # Add tabs to the tab widget
        self.tabs.addTab(self.student_attendance_tab, "Посещаемость студента")
        self.tabs.addTab(self.group_attendance_tab, "Посещаемость по группам")
        self.tabs.addTab(self.teacher_lessons_tab, "Уроки преподавателя")
        self.tabs.addTab(self.group_size_tab, "Количество студентов в группах")
        self.tabs.addTab(self.date_attendance_tab, "Посещаемость по датам")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)
    
    def create_student_attendance_tab(self):
        """Создает вкладку для отчета о посещаемости студента по урокам"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Filters
        filter_layout = QHBoxLayout()
        
        # Student filter
        self.student_filter = QComboBox()
        self.student_filter.addItem("Все студенты", None)
        
        # Subject filter
        self.student_subject_filter = QComboBox()
        self.student_subject_filter.addItem("Все предметы", None)
        
        # Date range
        self.student_start_date = QDateEdit()
        self.student_start_date.setCalendarPopup(True)
        self.student_start_date.setDate(QDate.currentDate().addDays(-30))
        
        self.student_end_date = QDateEdit()
        self.student_end_date.setCalendarPopup(True)
        self.student_end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel("Студент:"))
        filter_layout.addWidget(self.student_filter)
        filter_layout.addWidget(QLabel("Предмет:"))
        filter_layout.addWidget(self.student_subject_filter)
        filter_layout.addWidget(QLabel("С:"))
        filter_layout.addWidget(self.student_start_date)
        filter_layout.addWidget(QLabel("По:"))
        filter_layout.addWidget(self.student_end_date)
        
        # Table
        self.student_attendance_table = QTableWidget()
        self.student_attendance_table.setColumnCount(5)
        self.student_attendance_table.setHorizontalHeaderLabels(["Студент", "Предмет", "Дата", "Статус", "Преподаватель"])
        self.student_attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Export options
        export_layout = QHBoxLayout()
        
        # Format selection
        format_group = QGroupBox("Формат экспорта")
        format_layout = QHBoxLayout()
        self.student_pdf_radio = QRadioButton("PDF")
        self.student_excel_radio = QRadioButton("Excel")
        self.student_pdf_radio.setChecked(True)
        format_layout.addWidget(self.student_pdf_radio)
        format_layout.addWidget(self.student_excel_radio)
        format_group.setLayout(format_layout)
        
        # Export button
        self.student_export_btn = QPushButton("Экспорт отчета")
        self.student_export_btn.clicked.connect(self.export_student_attendance_report)
        
        # Generate report button
        self.student_generate_btn = QPushButton("Сформировать отчет")
        self.student_generate_btn.clicked.connect(self.generate_student_attendance_report)
        
        export_layout.addWidget(format_group)
        export_layout.addWidget(self.student_export_btn)
        export_layout.addWidget(self.student_generate_btn)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.student_attendance_table)
        layout.addLayout(export_layout)
        
        tab.setLayout(layout)
        
        # Connect signals
        self.student_filter.currentIndexChanged.connect(self.load_student_subjects)
        
        # Load initial data
        self.load_students()
        
        return tab
    
    def create_group_attendance_tab(self):
        """Создает вкладку для отчета о посещаемости по группам"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Filters
        filter_layout = QHBoxLayout()
        
        # Group filter
        self.group_filter = QComboBox()
        self.group_filter.addItem("Все группы", None)
        
        # Subject filter
        self.group_subject_filter = QComboBox()
        self.group_subject_filter.addItem("Все предметы", None)
        
        # Date range
        self.group_start_date = QDateEdit()
        self.group_start_date.setCalendarPopup(True)
        self.group_start_date.setDate(QDate.currentDate().addDays(-30))
        
        self.group_end_date = QDateEdit()
        self.group_end_date.setCalendarPopup(True)
        self.group_end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel("Группа:"))
        filter_layout.addWidget(self.group_filter)
        filter_layout.addWidget(QLabel("Предмет:"))
        filter_layout.addWidget(self.group_subject_filter)
        filter_layout.addWidget(QLabel("С:"))
        filter_layout.addWidget(self.group_start_date)
        filter_layout.addWidget(QLabel("По:"))
        filter_layout.addWidget(self.group_end_date)
        
        # Table
        self.group_attendance_table = QTableWidget()
        self.group_attendance_table.setColumnCount(4)
        self.group_attendance_table.setHorizontalHeaderLabels(["Группа", "Предмет", "Всего занятий", "Средняя посещаемость (%)"])
        self.group_attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Export options
        export_layout = QHBoxLayout()
        
        # Format selection
        format_group = QGroupBox("Формат экспорта")
        format_layout = QHBoxLayout()
        self.group_pdf_radio = QRadioButton("PDF")
        self.group_excel_radio = QRadioButton("Excel")
        self.group_pdf_radio.setChecked(True)
        format_layout.addWidget(self.group_pdf_radio)
        format_layout.addWidget(self.group_excel_radio)
        format_group.setLayout(format_layout)
        
        # Export button
        self.group_export_btn = QPushButton("Экспорт отчета")
        self.group_export_btn.clicked.connect(self.export_group_attendance_report)
        
        # Generate report button
        self.group_generate_btn = QPushButton("Сформировать отчет")
        self.group_generate_btn.clicked.connect(self.generate_group_attendance_report)
        
        export_layout.addWidget(format_group)
        export_layout.addWidget(self.group_export_btn)
        export_layout.addWidget(self.group_generate_btn)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.group_attendance_table)
        layout.addLayout(export_layout)
        
        tab.setLayout(layout)
        
        # Load initial data
        self.load_groups()
        self.load_subjects()
        
        return tab
    
    def create_teacher_lessons_tab(self):
        """Создает вкладку для отчета о уроках, проведенных учителем"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Filters
        filter_layout = QHBoxLayout()
        
        # Teacher filter
        self.teacher_filter = QComboBox()
        self.teacher_filter.addItem("Все преподаватели", None)
        
        # Date range
        self.teacher_start_date = QDateEdit()
        self.teacher_start_date.setCalendarPopup(True)
        self.teacher_start_date.setDate(QDate.currentDate().addDays(-30))
        
        self.teacher_end_date = QDateEdit()
        self.teacher_end_date.setCalendarPopup(True)
        self.teacher_end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel("Преподаватель:"))
        filter_layout.addWidget(self.teacher_filter)
        filter_layout.addWidget(QLabel("С:"))
        filter_layout.addWidget(self.teacher_start_date)
        filter_layout.addWidget(QLabel("По:"))
        filter_layout.addWidget(self.teacher_end_date)
        
        # Table
        self.teacher_lessons_table = QTableWidget()
        self.teacher_lessons_table.setColumnCount(5)
        self.teacher_lessons_table.setHorizontalHeaderLabels(["Преподаватель", "Предмет", "Группа", "Дата", "Локация"])
        self.teacher_lessons_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Export options
        export_layout = QHBoxLayout()
        
        # Format selection
        format_group = QGroupBox("Формат экспорта")
        format_layout = QHBoxLayout()
        self.teacher_pdf_radio = QRadioButton("PDF")
        self.teacher_excel_radio = QRadioButton("Excel")
        self.teacher_pdf_radio.setChecked(True)
        format_layout.addWidget(self.teacher_pdf_radio)
        format_layout.addWidget(self.teacher_excel_radio)
        format_group.setLayout(format_layout)
        
        # Export button
        self.teacher_export_btn = QPushButton("Экспорт отчета")
        self.teacher_export_btn.clicked.connect(self.export_teacher_lessons_report)
        
        # Generate report button
        self.teacher_generate_btn = QPushButton("Сформировать отчет")
        self.teacher_generate_btn.clicked.connect(self.generate_teacher_lessons_report)
        
        export_layout.addWidget(format_group)
        export_layout.addWidget(self.teacher_export_btn)
        export_layout.addWidget(self.teacher_generate_btn)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.teacher_lessons_table)
        layout.addLayout(export_layout)
        
        tab.setLayout(layout)
        
        # Load initial data
        self.load_teachers()
        
        return tab
    
    def create_group_size_tab(self):
        """Создает вкладку для отчета о количестве студентов в каждой группе"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Table
        self.group_size_table = QTableWidget()
        self.group_size_table.setColumnCount(3)
        self.group_size_table.setHorizontalHeaderLabels(["Группа", "Количество студентов", "Описание"])
        self.group_size_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Export options
        export_layout = QHBoxLayout()
        
        # Format selection
        format_group = QGroupBox("Формат экспорта")
        format_layout = QHBoxLayout()
        self.group_size_pdf_radio = QRadioButton("PDF")
        self.group_size_excel_radio = QRadioButton("Excel")
        self.group_size_pdf_radio.setChecked(True)
        format_layout.addWidget(self.group_size_pdf_radio)
        format_layout.addWidget(self.group_size_excel_radio)
        format_group.setLayout(format_layout)
        
        # Export button
        self.group_size_export_btn = QPushButton("Экспорт отчета")
        self.group_size_export_btn.clicked.connect(self.export_group_size_report)
        
        # Generate report button
        self.group_size_generate_btn = QPushButton("Сформировать отчет")
        self.group_size_generate_btn.clicked.connect(self.generate_group_size_report)
        
        export_layout.addWidget(format_group)
        export_layout.addWidget(self.group_size_export_btn)
        export_layout.addWidget(self.group_size_generate_btn)
        
        layout.addWidget(self.group_size_table)
        layout.addLayout(export_layout)
        
        tab.setLayout(layout)
        
        # Load initial data
        self.generate_group_size_report()
        
        return tab
    
    def create_date_attendance_tab(self):
        """Создает вкладку для отчета о посещаемости по датам"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Filters
        filter_layout = QHBoxLayout()
        
        # Date range
        self.date_start_date = QDateEdit()
        self.date_start_date.setCalendarPopup(True)
        self.date_start_date.setDate(QDate.currentDate().addDays(-30))
        
        self.date_end_date = QDateEdit()
        self.date_end_date.setCalendarPopup(True)
        self.date_end_date.setDate(QDate.currentDate())
        
        filter_layout.addWidget(QLabel("С:"))
        filter_layout.addWidget(self.date_start_date)
        filter_layout.addWidget(QLabel("По:"))
        filter_layout.addWidget(self.date_end_date)
        
        # Table
        self.date_attendance_table = QTableWidget()
        self.date_attendance_table.setColumnCount(3)
        self.date_attendance_table.setHorizontalHeaderLabels(["Дата", "Всего занятий", "Средняя посещаемость (%)"])
        self.date_attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Export options
        export_layout = QHBoxLayout()
        
        # Format selection
        format_group = QGroupBox("Формат экспорта")
        format_layout = QHBoxLayout()
        self.date_pdf_radio = QRadioButton("PDF")
        self.date_excel_radio = QRadioButton("Excel")
        self.date_pdf_radio.setChecked(True)
        format_layout.addWidget(self.date_pdf_radio)
        format_layout.addWidget(self.date_excel_radio)
        format_group.setLayout(format_layout)
        
        # Export button
        self.date_export_btn = QPushButton("Экспорт отчета")
        self.date_export_btn.clicked.connect(self.export_date_attendance_report)
        
        # Generate report button
        self.date_generate_btn = QPushButton("Сформировать отчет")
        self.date_generate_btn.clicked.connect(self.generate_date_attendance_report)
        
        export_layout.addWidget(format_group)
        export_layout.addWidget(self.date_export_btn)
        export_layout.addWidget(self.date_generate_btn)
        
        layout.addLayout(filter_layout)
        layout.addWidget(self.date_attendance_table)
        layout.addLayout(export_layout)
        
        tab.setLayout(layout)
        
        # Connect signals
        self.date_start_date.dateChanged.connect(self.generate_date_attendance_report)
        self.date_end_date.dateChanged.connect(self.generate_date_attendance_report)
        
        return tab
    
    @handle_exceptions
    def load_students(self):
        """Загружает список студентов в фильтр"""
        try:
            with get_session() as db:
                students = db.query(Student).all()
                for student in students:
                    self.student_filter.addItem(student.full_name, student.id)
        except Exception as e:
            logger.error(f"Ошибка загрузки студентов: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить список студентов")
    
    @handle_exceptions
    def load_student_subjects(self, index=None):
        """Загружает предметы для выбранного студента"""
        try:
            student_id = self.student_filter.currentData()
            if not student_id:
                return
                
            self.student_subject_filter.clear()
            self.student_subject_filter.addItem("Все предметы", None)
            
            with get_session() as db:
                # Получаем группу студента
                student = db.query(Student).get(student_id)
                if not student:
                    return
                    
                # Получаем предметы для группы студента
                subjects = db.query(Subject).join(Lesson, Subject.id == Lesson.subject_id)\
                    .filter(Lesson.group_id == student.group_id).distinct().all()
                    
                for subject in subjects:
                    self.student_subject_filter.addItem(subject.name, subject.id)
        except Exception as e:
            logger.error(f"Ошибка загрузки предметов для студента: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить список предметов")
    
    @handle_exceptions
    def load_groups(self):
        """Загружает список групп в фильтр"""
        try:
            with get_session() as db:
                groups = db.query(Group).all()
                for group in groups:
                    self.group_filter.addItem(f"Группа {group.name}", group.id)
        except Exception as e:
            logger.error(f"Ошибка загрузки групп: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить список групп")
    
    @handle_exceptions
    def load_subjects(self):
        """Загружает список предметов в фильтр"""
        try:
            with get_session() as db:
                subjects = db.query(Subject).all()
                for subject in subjects:
                    self.group_subject_filter.addItem(subject.name, subject.id)
        except Exception as e:
            logger.error(f"Ошибка загрузки предметов: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить список предметов")
    
    @handle_exceptions
    def load_teachers(self):
        """Загружает список преподавателей в фильтр"""
        try:
            with get_session() as db:
                teachers = db.query(Teacher).all()
                for teacher in teachers:
                    full_name = f"{teacher.last_name} {teacher.first_name} {teacher.patronymic or ''}".strip()
                    self.teacher_filter.addItem(full_name, teacher.id)
        except Exception as e:
            logger.error(f"Ошибка загрузки преподавателей: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить список преподавателей")
    
    @handle_exceptions
    def generate_student_attendance_report(self, checked=None):
        """Генерирует отчет о посещаемости студента"""
        # The 'checked' parameter is for signal compatibility
        try:
            student_id = self.student_filter.currentData()
            subject_id = self.student_subject_filter.currentData()
            start_date = self.student_start_date.date().toPyDate()
            end_date = self.student_end_date.date().toPyDate()
            
            with get_session() as db:
                query = db.query(
                    Student.full_name,
                    Subject.name.label('subject_name'),
                    Lesson.date_time,
                    Attendance.status,
                    Teacher.last_name,
                    Teacher.first_name,
                    Teacher.patronymic
                ).join(Attendance, Student.id == Attendance.student_id)\
                 .join(Lesson, Lesson.id == Attendance.lesson_id)\
                 .join(Subject, Subject.id == Lesson.subject_id)\
                 .join(Teacher, Teacher.id == Lesson.teacher_id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))
                
                if student_id:
                    query = query.filter(Student.id == student_id)
                if subject_id:
                    query = query.filter(Subject.id == subject_id)
                
                results = query.all()
                
                self.student_attendance_table.setRowCount(len(results))
                for row, (student_name, subject_name, date_time, status, last_name, first_name, patronymic) in enumerate(results):
                    teacher_name = f"{last_name} {first_name} {patronymic or ''}".strip()
                    status_text = "Присутствовал" if status == 'present' else "Отсутствовал" if status == 'absent' else "Опоздал" if status == 'late' else "Болеет" if status == 'sick' else "Не отмечено"
                    
                    self.student_attendance_table.setItem(row, 0, QTableWidgetItem(student_name))
                    self.student_attendance_table.setItem(row, 1, QTableWidgetItem(subject_name))
                    self.student_attendance_table.setItem(row, 2, QTableWidgetItem(date_time.strftime("%d.%m.%Y %H:%M")))
                    self.student_attendance_table.setItem(row, 3, QTableWidgetItem(status_text))
                    self.student_attendance_table.setItem(row, 4, QTableWidgetItem(teacher_name))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о посещаемости студента: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_student_attendance_report(self, checked=None):
        """Экспортирует отчет о посещаемости студента"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'student': 'Студент',
            'subject': 'Предмет',
            'date': 'Дата',
            'status': 'Статус',
            'teacher': 'Преподаватель'
        }
        export_report(self, self.student_attendance_table, columns, self.report_generator, self.student_pdf_radio)
    
    @handle_exceptions
    def generate_date_attendance_report(self, checked=None):
        """Генерирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        try:
            start_date = self.date_start_date.date().toPyDate()
            end_date = self.date_end_date.date().toPyDate()
            
            with get_session() as db:
                # Подзапрос для подсчета занятий по датам
                query = db.query(
                    func.date(Lesson.date_time).label('lesson_date'),
                    func.count(Lesson.id).label('lesson_count'),
                    func.avg(case((Attendance.status == 'present', 100.0), else_=0)).label('attendance_percent')
                ).outerjoin(Attendance, Attendance.lesson_id == Lesson.id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))\
                 .group_by(func.date(Lesson.date_time))\
                 .order_by(func.date(Lesson.date_time))
                
                results = query.all()
                
                self.date_attendance_table.setRowCount(len(results))
                for row, (lesson_date, lesson_count, attendance_percent) in enumerate(results):
                    self.date_attendance_table.setItem(row, 0, QTableWidgetItem(lesson_date.strftime("%d.%m.%Y")))
                    self.date_attendance_table.setItem(row, 1, QTableWidgetItem(str(lesson_count)))
                    self.date_attendance_table.setItem(row, 2, QTableWidgetItem(f"{attendance_percent:.2f}%"))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о посещаемости по датам: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_date_attendance_report(self, checked=None):
        """Экспортирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'date': 'Дата',
            'lesson_count': 'Количество занятий',
            'attendance': 'Посещаемость (%)'
        }
        export_report(self, self.date_attendance_table, columns, self.report_generator, self.date_pdf_radio)
    
    @handle_exceptions
    def generate_group_attendance_report(self, checked=None):
        """Генерирует отчет о посещаемости по группам"""
        # The 'checked' parameter is for signal compatibility
        try:
            group_id = self.group_filter.currentData()
            subject_id = self.group_subject_filter.currentData()
            start_date = self.group_start_date.date().toPyDate()
            end_date = self.group_end_date.date().toPyDate()
            
            with get_session() as db:
                # Подзапрос для подсчета общего количества занятий
                lessons_subquery = db.query(
                    Group.id.label('group_id'),
                    Subject.id.label('subject_id'),
                    func.count(Lesson.id).label('lesson_count')
                ).join(Lesson, Lesson.group_id == Group.id)\
                 .join(Subject, Subject.id == Lesson.subject_id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))
                
                if group_id:
                    lessons_subquery = lessons_subquery.filter(Group.id == group_id)
                if subject_id:
                    lessons_subquery = lessons_subquery.filter(Subject.id == subject_id)
                    
                lessons_subquery = lessons_subquery.group_by(Group.id, Subject.id).subquery()
                
                # Подзапрос для подсчета посещаемости
                attendance_subquery = db.query(
                    Group.id.label('group_id'),
                    Subject.id.label('subject_id'),
                    func.count(Attendance.student_id).label('attendance_count'),
                    func.count(Student.id).label('student_count')
                ).join(Student, Student.group_id == Group.id)\
                 .join(Lesson, Lesson.group_id == Group.id)\
                 .join(Subject, Subject.id == Lesson.subject_id)\
                 .outerjoin(Attendance, (Attendance.student_id == Student.id) & 
                                        (Attendance.lesson_id == Lesson.id) & 
                                        (Attendance.status == 'present'))\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))
                
                if group_id:
                    attendance_subquery = attendance_subquery.filter(Group.id == group_id)
                if subject_id:
                    attendance_subquery = attendance_subquery.filter(Subject.id == subject_id)
                    
                attendance_subquery = attendance_subquery.group_by(Group.id, Subject.id).subquery()
                
                # Объединение результатов
                results = db.query(
                    Group.name.label('group_name'),
                    Subject.name.label('subject_name'),
                    lessons_subquery.c.lesson_count,
                    func.round(func.coalesce(attendance_subquery.c.attendance_count, 0) * 100.0 / 
                              (func.coalesce(attendance_subquery.c.student_count, 0) * lessons_subquery.c.lesson_count), 2).label('attendance_percent')
                ).join(lessons_subquery, Group.id == lessons_subquery.c.group_id)\
                 .join(Subject, Subject.id == lessons_subquery.c.subject_id)\
                 .join(attendance_subquery, (Group.id == attendance_subquery.c.group_id) & 
                                           (Subject.id == attendance_subquery.c.subject_id))
                
                results = results.all()
                
                self.group_attendance_table.setRowCount(len(results))
                for row, (group_name, subject_name, lesson_count, attendance_percent) in enumerate(results):
                    self.group_attendance_table.setItem(row, 0, QTableWidgetItem(group_name))
                    self.group_attendance_table.setItem(row, 1, QTableWidgetItem(subject_name))
                    self.group_attendance_table.setItem(row, 2, QTableWidgetItem(str(lesson_count)))
                    self.group_attendance_table.setItem(row, 3, QTableWidgetItem(f"{attendance_percent}%"))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о посещаемости по группам: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_group_attendance_report(self, checked=None):
        """Экспортирует отчет о посещаемости по группам"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'group': 'Группа',
            'subject': 'Предмет',
            'lessons': 'Всего занятий',
            'attendance': 'Средняя посещаемость (%)'
        }
        export_report(self, self.group_attendance_table, columns, self.report_generator, self.group_pdf_radio)
    
    @handle_exceptions
    def generate_date_attendance_report(self, checked=None):
        """Генерирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        try:
            start_date = self.date_start_date.date().toPyDate()
            end_date = self.date_end_date.date().toPyDate()
            
            with get_session() as db:
                # Подзапрос для подсчета занятий по датам
                query = db.query(
                    func.date(Lesson.date_time).label('lesson_date'),
                    func.count(Lesson.id).label('lesson_count'),
                    func.avg(case((Attendance.status == 'present', 100.0), else_=0)).label('attendance_percent')
                ).outerjoin(Attendance, Attendance.lesson_id == Lesson.id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))\
                 .group_by(func.date(Lesson.date_time))\
                 .order_by(func.date(Lesson.date_time))
                
                results = query.all()
                
                self.date_attendance_table.setRowCount(len(results))
                for row, (lesson_date, lesson_count, attendance_percent) in enumerate(results):
                    self.date_attendance_table.setItem(row, 0, QTableWidgetItem(lesson_date.strftime("%d.%m.%Y")))
                    self.date_attendance_table.setItem(row, 1, QTableWidgetItem(str(lesson_count)))
                    self.date_attendance_table.setItem(row, 2, QTableWidgetItem(f"{attendance_percent:.2f}%"))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о посещаемости по датам: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_date_attendance_report(self, checked=None):
        """Экспортирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'date': 'Дата',
            'lesson_count': 'Количество занятий',
            'attendance': 'Посещаемость (%)'
        }
        export_report(self, self.date_attendance_table, columns, self.report_generator, self.date_pdf_radio)
    
    @handle_exceptions
    def generate_teacher_lessons_report(self, checked=None):
        """Генерирует отчет о уроках, проведенных учителем"""
        # The 'checked' parameter is for signal compatibility
        try:
            teacher_id = self.teacher_filter.currentData()
            start_date = self.teacher_start_date.date().toPyDate()
            end_date = self.teacher_end_date.date().toPyDate()
            
            with get_session() as db:
                query = db.query(
                    Teacher.last_name,
                    Teacher.first_name,
                    Teacher.patronymic,
                    Subject.name.label('subject_name'),
                    Group.name.label('group_name'),
                    Lesson.date_time,
                    Lesson.location
                ).join(Lesson, Lesson.teacher_id == Teacher.id)\
                 .join(Subject, Subject.id == Lesson.subject_id)\
                 .join(Group, Group.id == Lesson.group_id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))
                
                if teacher_id:
                    query = query.filter(Teacher.id == teacher_id)
                
                results = query.all()
                
                self.teacher_lessons_table.setRowCount(len(results))
                for row, (last_name, first_name, patronymic, subject_name, group_name, date_time, location) in enumerate(results):
                    teacher_name = f"{last_name} {first_name} {patronymic or ''}".strip()
                    
                    self.teacher_lessons_table.setItem(row, 0, QTableWidgetItem(teacher_name))
                    self.teacher_lessons_table.setItem(row, 1, QTableWidgetItem(subject_name))
                    self.teacher_lessons_table.setItem(row, 2, QTableWidgetItem(group_name))
                    self.teacher_lessons_table.setItem(row, 3, QTableWidgetItem(date_time.strftime("%d.%m.%Y %H:%M")))
                    self.teacher_lessons_table.setItem(row, 4, QTableWidgetItem(location or ""))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о уроках преподавателя: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_teacher_lessons_report(self, checked=None):
        """Экспортирует отчет о уроках, проведенных учителем"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'teacher': 'Преподаватель',
            'subject': 'Предмет',
            'group': 'Группа',
            'date': 'Дата',
            'location': 'Место проведения'
        }
        export_report(self, self.teacher_lessons_table, columns, self.report_generator, self.teacher_pdf_radio)
    
    @handle_exceptions
    def generate_date_attendance_report(self, checked=None):
        """Генерирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        try:
            start_date = self.date_start_date.date().toPyDate()
            end_date = self.date_end_date.date().toPyDate()
            
            with get_session() as db:
                # Подзапрос для подсчета занятий по датам
                query = db.query(
                    func.date(Lesson.date_time).label('lesson_date'),
                    func.count(Lesson.id).label('lesson_count'),
                    func.avg(case((Attendance.status == 'present', 100.0), else_=0)).label('attendance_percent')
                ).outerjoin(Attendance, Attendance.lesson_id == Lesson.id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))\
                 .group_by(func.date(Lesson.date_time))\
                 .order_by(func.date(Lesson.date_time))
                
                results = query.all()
                
                self.date_attendance_table.setRowCount(len(results))
                for row, (lesson_date, lesson_count, attendance_percent) in enumerate(results):
                    self.date_attendance_table.setItem(row, 0, QTableWidgetItem(lesson_date.strftime("%d.%m.%Y")))
                    self.date_attendance_table.setItem(row, 1, QTableWidgetItem(str(lesson_count)))
                    self.date_attendance_table.setItem(row, 2, QTableWidgetItem(f"{attendance_percent:.2f}%"))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о посещаемости по датам: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_date_attendance_report(self, checked=None):
        """Экспортирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'date': 'Дата',
            'lesson_count': 'Количество занятий',
            'attendance': 'Посещаемость (%)'
        }
        export_report(self, self.date_attendance_table, columns, self.report_generator, self.date_pdf_radio)
    
    @handle_exceptions
    def generate_group_size_report(self, checked=None):
        """Генерирует отчет о количестве студентов в каждой группе"""
        # The 'checked' parameter is for signal compatibility
        try:
            with get_session() as db:
                query = db.query(
                    Group.name,
                    func.count(Student.id).label('student_count'),
                    Group.description
                ).outerjoin(Student, Student.group_id == Group.id)\
                 .group_by(Group.id)
                
                results = query.all()
                
                self.group_size_table.setRowCount(len(results))
                for row, (group_name, student_count, description) in enumerate(results):
                    self.group_size_table.setItem(row, 0, QTableWidgetItem(group_name))
                    self.group_size_table.setItem(row, 1, QTableWidgetItem(str(student_count)))
                    self.group_size_table.setItem(row, 2, QTableWidgetItem(description or ""))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о количестве студентов в группах: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_group_size_report(self, checked=None):
        """Экспортирует отчет о количестве студентов в каждой группе"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'group': 'Группа',
            'student_count': 'Количество студентов',
            'description': 'Описание'
        }
        export_report(self, self.group_size_table, columns, self.report_generator, self.group_size_pdf_radio)
    
    @handle_exceptions
    def generate_date_attendance_report(self, checked=None):
        """Генерирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        try:
            start_date = self.date_start_date.date().toPyDate()
            end_date = self.date_end_date.date().toPyDate()
            
            with get_session() as db:
                # Подзапрос для подсчета занятий по датам
                query = db.query(
                    func.date(Lesson.date_time).label('lesson_date'),
                    func.count(Lesson.id).label('lesson_count'),
                    func.avg(case((Attendance.status == 'present', 100.0), else_=0)).label('attendance_percent')
                ).outerjoin(Attendance, Attendance.lesson_id == Lesson.id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))\
                 .group_by(func.date(Lesson.date_time))\
                 .order_by(func.date(Lesson.date_time))
                
                results = query.all()
                
                self.date_attendance_table.setRowCount(len(results))
                for row, (lesson_date, lesson_count, attendance_percent) in enumerate(results):
                    self.date_attendance_table.setItem(row, 0, QTableWidgetItem(lesson_date.strftime("%d.%m.%Y")))
                    self.date_attendance_table.setItem(row, 1, QTableWidgetItem(str(lesson_count)))
                    self.date_attendance_table.setItem(row, 2, QTableWidgetItem(f"{attendance_percent:.2f}%"))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о посещаемости по датам: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_date_attendance_report(self, checked=None):
        """Экспортирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'date': 'Дата',
            'lesson_count': 'Количество занятий',
            'attendance': 'Посещаемость (%)'
        }
        export_report(self, self.date_attendance_table, columns, self.report_generator, self.date_pdf_radio)
    
    @handle_exceptions
    def generate_teacher_lessons_report(self, checked=None):
        """Генерирует отчет о уроках, проведенных учителем"""
        # The 'checked' parameter is for signal compatibility
        try:
            teacher_id = self.teacher_filter.currentData()
            start_date = self.teacher_start_date.date().toPyDate()
            end_date = self.teacher_end_date.date().toPyDate()
            
            with get_session() as db:
                query = db.query(
                    Teacher.last_name,
                    Teacher.first_name,
                    Teacher.patronymic,
                    Subject.name.label('subject_name'),
                    Group.name.label('group_name'),
                    Lesson.date_time,
                    Lesson.location
                ).join(Lesson, Lesson.teacher_id == Teacher.id)\
                 .join(Subject, Subject.id == Lesson.subject_id)\
                 .join(Group, Group.id == Lesson.group_id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))
                
                if teacher_id:
                    query = query.filter(Teacher.id == teacher_id)
                
                results = query.all()
                
                self.teacher_lessons_table.setRowCount(len(results))
                for row, (last_name, first_name, patronymic, subject_name, group_name, date_time, location) in enumerate(results):
                    teacher_name = f"{last_name} {first_name} {patronymic or ''}".strip()
                    
                    self.teacher_lessons_table.setItem(row, 0, QTableWidgetItem(teacher_name))
                    self.teacher_lessons_table.setItem(row, 1, QTableWidgetItem(subject_name))
                    self.teacher_lessons_table.setItem(row, 2, QTableWidgetItem(group_name))
                    self.teacher_lessons_table.setItem(row, 3, QTableWidgetItem(date_time.strftime("%d.%m.%Y %H:%M")))
                    self.teacher_lessons_table.setItem(row, 4, QTableWidgetItem(location or ""))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о уроках преподавателя: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_teacher_lessons_report(self, checked=None):
        """Экспортирует отчет о уроках, проведенных учителем"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'teacher': 'Преподаватель',
            'subject': 'Предмет',
            'group': 'Группа',
            'date': 'Дата',
            'location': 'Место проведения'
        }
        export_report(self, self.teacher_lessons_table, columns, self.report_generator, self.teacher_pdf_radio)
    
    @handle_exceptions
    def generate_date_attendance_report(self, checked=None):
        """Генерирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        try:
            start_date = self.date_start_date.date().toPyDate()
            end_date = self.date_end_date.date().toPyDate()
            
            with get_session() as db:
                # Подзапрос для подсчета занятий по датам
                query = db.query(
                    func.date(Lesson.date_time).label('lesson_date'),
                    func.count(Lesson.id).label('lesson_count'),
                    func.avg(case((Attendance.status == 'present', 100.0), else_=0)).label('attendance_percent')
                ).outerjoin(Attendance, Attendance.lesson_id == Lesson.id)\
                 .filter(Lesson.date_time.between(start_date, end_date + timedelta(days=1)))\
                 .group_by(func.date(Lesson.date_time))\
                 .order_by(func.date(Lesson.date_time))
                
                results = query.all()
                
                self.date_attendance_table.setRowCount(len(results))
                for row, (lesson_date, lesson_count, attendance_percent) in enumerate(results):
                    self.date_attendance_table.setItem(row, 0, QTableWidgetItem(lesson_date.strftime("%d.%m.%Y")))
                    self.date_attendance_table.setItem(row, 1, QTableWidgetItem(str(lesson_count)))
                    self.date_attendance_table.setItem(row, 2, QTableWidgetItem(f"{attendance_percent:.2f}%"))
        except Exception as e:
            logger.error(f"Ошибка генерации отчета о посещаемости по датам: {str(e)}")
            show_error("Ошибка", "Не удалось сформировать отчет")
    
    @handle_exceptions
    def export_date_attendance_report(self, checked=None):
        """Экспортирует отчет о посещаемости по датам"""
        # The 'checked' parameter is for signal compatibility
        columns = {
            'date': 'Дата',
            'lesson_count': 'Количество занятий',
            'attendance': 'Посещаемость (%)'
        }
        export_report(self, self.date_attendance_table, columns, self.report_generator, self.date_pdf_radio)
    
    # @handle_exceptions
    # def generate_group_size_report(self):
    #     """Генерирует отчет о количестве студентов в каждой группе"""
    #     try:
    #         with get_session() as db:
    #             query = db.query(
    #                 Group.name,
    #                 func.count(Student.id).label('student_count'),
    #                 Group.description
    #             ).outerjoin(Student, Student.group_id == Group.id)\
    #              .group_by(Group.id)
                
    #             results = query.all()
                
    #             self.group_size_table.setRowCount(len(results))
    #             for row, (group_name, student_count, description) in enumerate(results):
    #                 self.group_size_table.setItem(row, 0, QTableWidgetItem(group_name))
    #                 self.group_size_table.setItem(row, 1, QTableWidgetItem(str(student_count)))
    #                 self.group_size_table.setItem(row, 2