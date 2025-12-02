from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QHeaderView, QCheckBox, QPushButton, QTableWidgetItem, \
    QHBoxLayout, QLabel, QComboBox, QDateEdit
from PyQt5.QtCore import Qt, QDate
from database import get_session
from models import Student, Attendance, Lesson, Teacher, Subject, Group
from utils import show_info, show_error, get_logger, handle_exceptions
from sqlalchemy.sql import func

logger = get_logger()


class AttendanceWindow(QWidget):
    def __init__(self, role='student', user_id=None):
        super().__init__()
        self.role = role
        self.user_id = user_id
        self.current_lesson_id = None
        self.is_editing = False
        self.init_ui()

    @handle_exceptions
    def init_ui(self):
        layout = QVBoxLayout()
        self.filter_layout = QHBoxLayout()
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        self.subject_filter = QComboBox()
        self.subject_filter.addItem("Все предметы", None)
        self.group_filter = QComboBox()
        self.group_filter.addItem("Все группы", None)

        self.filter_layout.addWidget(QLabel("Дата:"))
        self.filter_layout.addWidget(self.date_filter)
        self.filter_layout.addWidget(QLabel("Предмет:"))
        self.filter_layout.addWidget(self.subject_filter)
        self.filter_layout.addWidget(QLabel("Группа:"))
        self.filter_layout.addWidget(self.group_filter)

        if self.role == 'student':
            self.teacher_filter = QComboBox()
            self.teacher_filter.addItem("Все учителя", None)
            self.filter_layout.addWidget(QLabel("Учитель:"))
            self.filter_layout.addWidget(self.teacher_filter)

        if self.role in ['teacher', 'admin']:
            self.btn_edit = QPushButton("Изменить присутствие")
            self.btn_edit.clicked.connect(self.toggle_editing)
            self.btn_save = QPushButton("Сохранить")
            self.btn_save.clicked.connect(lambda checked: self.save_attendance())
            self.btn_save.setVisible(False)
            self.btn_save.setEnabled(False)

        self.table = QTableWidget()
        self.table.setColumnCount(5)  # Changed from 4 to 5 columns
        self.table.setHorizontalHeaderLabels(["Студент", "Группа", "Предмет", "Дата", "Присутствие"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # Allow manual column resizing
        
        # Set specific column widths
        self.table.setColumnWidth(0, 200)  # Student name
        self.table.setColumnWidth(1, 100)  # Group
        self.table.setColumnWidth(2, 150)  # Subject
        self.table.setColumnWidth(3, 150)  # Date
        self.table.setColumnWidth(4, 150)  # Attendance

        layout.addLayout(self.filter_layout)
        if self.role in ['teacher', 'admin']:
            layout.addWidget(self.btn_edit)
            layout.addWidget(self.btn_save)
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.date_filter.dateChanged.connect(self.load_data)
        self.subject_filter.currentIndexChanged.connect(self.load_data)
        self.group_filter.currentIndexChanged.connect(self.load_data)
        if self.role == 'student':
            self.teacher_filter.currentIndexChanged.connect(self.load_data)

        self.load_filters()
        self.load_data()

    @handle_exceptions
    def load_filters(self):
        try:
            with get_session() as db:
                # Предметы (все доступные предметы)
                subjects = db.query(Subject).distinct().all()
                for subject in subjects:
                    self.subject_filter.addItem(subject.name, subject.id)

                # Группы (все доступные группы)
                groups = db.query(Group.id).distinct().all()  
                for group in groups:
                    self.group_filter.addItem(f"Группа {group[0]}", group[0])

                # Учителя для роли student (все учителя)
                if self.role == 'student':
                    teachers = db.query(Teacher.id, Teacher.last_name, Teacher.first_name, Teacher.patronymic).distinct().all()
                    for teacher_id, last_name, first_name, patronymic in teachers:
                        full_name = f"{last_name} {first_name} {patronymic or ''}".strip()
                        self.teacher_filter.addItem(full_name, teacher_id)

        except Exception as e:
            logger.error(f"Ошибка загрузки фильтров: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить фильтры")

    @handle_exceptions
    def load_data(self, index=None):
        try:
            with (get_session() as db):
                # Базовый запрос для всех студентов и уроков
                query = db.query(
                    Student.id, Student.full_name, Student.group_id, Group.name.label('group_name'),
                    Subject.name.label('subject_name'),
                    Lesson.date_time, Attendance.status
                ).join(Group, Group.id == Student.group_id)\
                 .join(Lesson, Lesson.group_id == Student.group_id)\
                 .join(Subject, Subject.id == Lesson.subject_id)\
                 .outerjoin(Attendance, (Attendance.student_id == Student.id) & (Attendance.lesson_id == Lesson.id))

                # Фильтр по дате
                selected_date = self.date_filter.date().toPyDate()
                query = query.filter(func.date(Lesson.date_time) == selected_date)

                # Фильтр по предмету
                selected_subject = self.subject_filter.currentData()
                if selected_subject:
                    query = query.filter(Lesson.subject_id == selected_subject)  # Changed to use subject_id

                # Фильтр по группе
                selected_group = self.group_filter.currentData()
                if selected_group:
                    query = query.filter(Student.group_id == selected_group)

                # Фильтр по учителю только для студента
                if self.role == 'student':
                    selected_teacher = self.teacher_filter.currentData()
                    if selected_teacher:
                        query = query.filter(Lesson.teacher_id == selected_teacher)

                results = query.all()
                logger.info(f"Найдено записей: {len(results)}")

                self.table.setRowCount(len(results))
                for row, (student_id, full_name, group_id, group_name, subject_name, date_time, status) in enumerate(results):
                    self.table.setItem(row, 0, QTableWidgetItem(full_name))
                    self.table.setItem(row, 1, QTableWidgetItem(f"Группа {group_name}"))
                    self.table.setItem(row, 2, QTableWidgetItem(subject_name))
                    self.table.setItem(row, 3, QTableWidgetItem(date_time.strftime("%d.%m.%Y %H:%M")))

                    if self.role == 'student':
                        status_text = "Присутствовал" if status == 'present' else "Отсутствовал" if status == 'absent' else "Опоздал" if status == 'late' else "Болеет" if status == 'sick' else "Не отмечено"
                        status_item = QTableWidgetItem(status_text)
                        status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(row, 4, status_item)  # Changed from column 3 to 4
                    else:
                        cell_widget = QWidget()
                        layout = QHBoxLayout(cell_widget)
                        layout.setContentsMargins(2, 2, 2, 2)  # Reduced margins
                        layout.setAlignment(Qt.AlignCenter)

                        combo = QComboBox()
                        combo.addItems(["", "Присутствовал", "Отсутствовал", "Опоздал", "Болеет"])
                        if status == 'present':
                            combo.setCurrentIndex(1)
                        elif status == 'absent':
                            combo.setCurrentIndex(2)
                        elif status == 'late':
                            combo.setCurrentIndex(3)
                        elif status == 'sick':
                            combo.setCurrentIndex(4)
                        else:
                            combo.setCurrentIndex(0)
                        combo.setEnabled(self.is_editing)
                        combo.setFixedWidth(120)  # Set fixed width for combo box

                        layout.addWidget(combo)
                        cell_widget.setLayout(layout)
                        self.table.setCellWidget(row, 4, cell_widget)  # Changed from column 3 to 4
                        combo.currentIndexChanged.connect(lambda index, r=row: self.on_attendance_changed(r))

                        # Поиск урока для сохранения
                        lesson = db.query(Lesson).filter(
                            func.date(Lesson.date_time) == selected_date,
                            Lesson.group_id == group_id,
                            Lesson.subject_id == (selected_subject if selected_subject else Lesson.subject_id)
                        ).first()
                        self.table.item(row, 0).setData(Qt.UserRole, (student_id, lesson.id if lesson else None))

        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить данные")

    def toggle_editing(self):
        self.is_editing = not self.is_editing
        self.btn_save.setVisible(self.is_editing)
        self.btn_save.setEnabled(False)
        self.btn_edit.setText("Завершить редактирование" if self.is_editing else "Изменить присутствие")
        self.load_data()

    def on_attendance_changed(self, row):
        if self.is_editing and self.role in ['teacher', 'admin']:
            self.btn_save.setEnabled(True)

    @handle_exceptions
    def save_attendance(self):
        if self.role == 'student' or not self.is_editing:
            return

        try:
            with get_session() as db:
                for row in range(self.table.rowCount()):
                    student_data = self.table.item(row, 0).data(Qt.UserRole)
                    if not student_data:
                        continue
                    student_id, lesson_id = student_data
                    if not lesson_id:
                        logger.warning(f"Lesson ID не найден для строки {row}")
                        continue

                    combo = self.table.cellWidget(row, 4).findChild(QComboBox)
                    state = combo.currentIndex()

                    attendance = db.query(Attendance).filter(
                        Attendance.student_id == student_id,
                        Attendance.lesson_id == lesson_id
                    ).first()

                    if state == 0:  # Empty selection
                        if attendance:
                            db.delete(attendance)
                    else:
                        status_map = {1: 'present', 2: 'absent', 3: 'late', 4: 'sick'}
                        status = status_map[state]
                        
                        if attendance:
                            attendance.status = status
                        else:
                            db.add(Attendance(student_id=student_id, lesson_id=lesson_id, status=status))

                db.commit()
                show_info("Успех", "Посещаемость сохранена")
                self.is_editing = False
                self.btn_save.setVisible(False)
                self.btn_edit.setText("Изменить присутствие")
                self.load_data()

        except Exception as e:
            logger.error(f"Ошибка сохранения: {str(e)}")
            show_error("Ошибка", "Не удалось сохранить данные")
