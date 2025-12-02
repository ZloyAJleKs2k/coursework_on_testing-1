from PyQt5.QtWidgets import (QWidget, QVBoxLayout,
                             QTableWidget, QHeaderView,
                             QComboBox, QTableWidgetItem, QHBoxLayout)

from database import get_session
from models import Lesson, Group, Subject,Teacher,User

from utils import show_error, handle_exceptions
from utils import get_logger

logger = get_logger()


class ScheduleWindow(QWidget):
    def __init__(self, role='student'):
        super().__init__()
        self.table = None
        self.subject_filter = None
        self.group_filter = None
        self.filter_layout = None
        self.role = role
        self.init_ui()
        self.load_filters()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Фильтры
        self.filter_layout = QHBoxLayout()

        self.group_filter = QComboBox()
        self.group_filter.addItem("Все группы", None)

        self.subject_filter = QComboBox()
        self.subject_filter.addItem("Все предметы", None)

        self.filter_layout.addWidget(self.group_filter)
        self.filter_layout.addWidget(self.subject_filter)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Дата", "Предмет", "Преподаватель", "Группа"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(self.filter_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        # Сигналы
        self.group_filter.currentIndexChanged.connect(self.load_data)
        self.subject_filter.currentIndexChanged.connect(self.load_data)

    @handle_exceptions
    def load_filters(self):
        try:
            with get_session() as db:
                # Загрузка групп
                groups = db.query(Group).all()
                for group in groups:
                    self.group_filter.addItem(group.name, group.id)

                # Загрузка предметов
                subjects = db.query(Subject).all()
                for subject in subjects:
                    self.subject_filter.addItem(subject.name, subject.id)
        except Exception as e:
            logger.error(f"Ошибка загрузки фильтров: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить фильтры")

    @handle_exceptions
    def load_data(self, index=None):
        try:
            with get_session() as db:
                query = db.query(Lesson).join(Teacher).join(Group, Lesson.group_id == Group.id)

                # Применение фильтров
                selected_group = self.group_filter.currentData()
                if selected_group is not None:
                    query = query.filter(Lesson.group_id == selected_group)

                selected_subject = self.subject_filter.currentData()
                if selected_subject is not None:
                    query = query.filter(Lesson.subject_id == selected_subject)

                lessons = query.all()

                # Заполнение таблицы
                self.table.setRowCount(len(lessons))
                for row, lesson in enumerate(lessons):
                    teacher = lesson.teacher
                    teacher_full_name = f"{teacher.last_name} {teacher.first_name} {teacher.patronymic or ''}".strip()
                    self.table.setItem(row, 0, QTableWidgetItem(lesson.date_time.strftime("%d.%m.%Y %H:%M")))
                    self.table.setItem(row, 1, QTableWidgetItem(lesson.subject.name))
                    self.table.setItem(row, 2, QTableWidgetItem(teacher_full_name))
                    self.table.setItem(row, 3, QTableWidgetItem(lesson.group.name))
        except Exception as e:
            logger.error(f"Ошибка загрузки расписания: {str(e)}")
            show_error("Ошибка", "Не удалось загрузить расписание")


