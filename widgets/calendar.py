# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QTableWidget, QTableWidgetItem, QHeaderView
# from PyQt5.QtCore import QDate, Qt

# from database import get_session
# from models import Lesson
# from models import User
# from utils import show_error


# class CalendarWidget(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.init_ui()
#         self.load_lessons(QDate.currentDate())

#     def init_ui(self):
#         self.layout = QVBoxLayout()

#         # Календарь
#         self.calendar = QCalendarWidget()
#         self.calendar.setGridVisible(True)
#         self.calendar.clicked.connect(self.on_date_selected)

#         # Таблица занятий
#         self.lessons_table = QTableWidget()
#         self.lessons_table.setColumnCount(3)
#         self.lessons_table.setHorizontalHeaderLabels(["Время", "Предмет", "Преподаватель"])
#         self.lessons_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

#         self.layout.addWidget(self.calendar)
#         self.layout.addWidget(self.lessons_table)
#         self.setLayout(self.layout)

#     def on_date_selected(self, date: QDate):
#         self.load_lessons(date)

#     def load_lessons(self, date: QDate):
#         try:
#             with get_session() as db:
#                 selected_date = date.toPyDate()

#                 lessons = db.query(Lesson).filter(
#                     Lesson.date_time >= selected_date,
#                     Lesson.date_time < selected_date.replace(day=selected_date.day + 1)
#                 ).join(User).all()

#                 self.lessons_table.setRowCount(len(lessons))
#                 for row, lesson in enumerate(lessons):
#                     self.lessons_table.setItem(row, 0, QTableWidgetItem(lesson.date_time.strftime("%H:%M")))
#                     self.lessons_table.setItem(row, 1, QTableWidgetItem(lesson.subject))
#                     self.lessons_table.setItem(row, 2, QTableWidgetItem(lesson.teacher.login))
#         except Exception as e:
#             show_error("Ошибка", f"Не удалось загрузить занятия: {str(e)}")