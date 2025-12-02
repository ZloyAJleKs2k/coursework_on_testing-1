from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QTabWidget, QComboBox, QHBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from database import get_session
from models import Student, Attendance, Group, Subject, Lesson
from utils import show_error
from sqlalchemy.sql import func, case
from datetime import datetime, timedelta


class StatsWidget(QWidget):
    months_ru = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.plot_data()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create separate widgets for each chart
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        
        # Set layouts for each tab
        self.tab1_layout = QVBoxLayout()
        self.tab2_layout = QVBoxLayout()
        self.tab3_layout = QVBoxLayout()
        
        # Create month selectors for each tab
        self.month_selector1 = self._create_month_selector()
        self.month_selector2 = self._create_month_selector()
        self.month_selector3 = self._create_month_selector()
        
        self.tab1_layout.addLayout(self.month_selector1)
        self.tab2_layout.addLayout(self.month_selector2)
        self.tab3_layout.addLayout(self.month_selector3)
        
        # Create figures and canvases
        self.figure1 = Figure(figsize=(10, 6))
        self.canvas1 = FigureCanvasQTAgg(self.figure1)
        
        self.figure2 = Figure(figsize=(10, 6))
        self.canvas2 = FigureCanvasQTAgg(self.figure2)
        
        self.figure3 = Figure(figsize=(10, 6))
        self.canvas3 = FigureCanvasQTAgg(self.figure3)
        
        # Add canvases to respective layouts
        self.tab1_layout.addWidget(self.canvas1)
        self.tab2_layout.addWidget(self.canvas2)
        self.tab3_layout.addWidget(self.canvas3)
        
        # Set layouts to tabs
        self.tab1.setLayout(self.tab1_layout)
        self.tab2.setLayout(self.tab2_layout)
        self.tab3.setLayout(self.tab3_layout)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.tab1, "Посещаемость по группам")
        self.tabs.addTab(self.tab2, "Посещаемость по предметам")
        self.tabs.addTab(self.tab3, "Количество занятий за месяц")
        
        # Кнопка обновления
        self.btn_refresh = QPushButton("Обновить данные")
        self.btn_refresh.clicked.connect(self.plot_data)
        
        # Add widgets to main layout
        layout.addWidget(self.tabs)
        layout.addWidget(self.btn_refresh)
        
        self.setLayout(layout)

    def _create_month_selector(self):
        layout = QHBoxLayout()
        month_selector = QComboBox()
        current_date = datetime.now()

        for i in range(12):
            month_delta = timedelta(days=30.44 * i)  # Average month length
            date = (current_date - month_delta).replace(day=1)
            month_name = self.months_ru[date.month - 1]
            month_selector.addItem(f"{month_name} {date.year}", date)

        month_selector.currentIndexChanged.connect(self.plot_data)
        layout.addWidget(QLabel("Выберите месяц:"))
        layout.addWidget(month_selector)
        layout.addStretch()
        return layout

    def plot_data(self):
        try:
            with get_session() as db:
                # Get selected dates for each tab
                selected_date1 = self.month_selector1.itemAt(1).widget().currentData()
                selected_date2 = self.month_selector2.itemAt(1).widget().currentData()
                selected_date3 = self.month_selector3.itemAt(1).widget().currentData()

                # Calculate date ranges for each tab
                start_date1 = selected_date1.replace(day=1)
                end_date1 = (start_date1 + timedelta(days=32)).replace(day=1) - timedelta(days=1)

                start_date2 = selected_date2.replace(day=1)
                end_date2 = (start_date2 + timedelta(days=32)).replace(day=1) - timedelta(days=1)

                start_date3 = selected_date3.replace(day=1)
                end_date3 = (start_date3 + timedelta(days=32)).replace(day=1) - timedelta(days=1)

                # 1. Посещаемость по группам
                attendance_by_group = db.query(
                    Student.group_id,
                    Group.name,
                    (100.0 * func.count(case((Attendance.status.in_(['present', 'late']), 1))).label('present_count') / 
                    func.count(Attendance.status)).label('attendance_rate')
                ).select_from(Student).join(Group, Student.group_id == Group.id)\
                 .join(Attendance, Attendance.student_id == Student.id)\
                 .join(Lesson, Lesson.id == Attendance.lesson_id)\
                 .filter(Lesson.date_time >= start_date1, Lesson.date_time <= end_date1)\
                 .group_by(Student.group_id, Group.name).all()

                # 2. Посещаемость по предметам
                attendance_by_subject = db.query(
                    Subject.id,
                    Subject.name,
                    (100.0 * func.count(case((Attendance.status == 'present', 1))).label('present_count') / func.count(Attendance.status)).label('attendance_rate')
                ).select_from(Subject).join(Lesson, Lesson.subject_id == Subject.id)\
                 .join(Attendance, Attendance.lesson_id == Lesson.id)\
                 .filter(Lesson.date_time >= start_date2, Lesson.date_time <= end_date2)\
                 .group_by(Subject.id, Subject.name).all()

                # 3. Количество предметов за месяц
                subjects_per_month = db.query(
                    Subject.name,
                    func.count(Lesson.id).label('lesson_count')
                ).join(Lesson).filter(
                    Lesson.date_time >= start_date3,
                    Lesson.date_time <= end_date3
                ).group_by(Subject.name).all()

            # Очистка и подготовка графиков
            self.figure1.clear()
            self.figure2.clear()
            self.figure3.clear()

            # График 1: Посещаемость по группам
            ax1 = self.figure1.add_subplot(111)
            groups = [f"Группа {g.name}" for g in attendance_by_group]
            rates = [g.attendance_rate or 0 for g in attendance_by_group]
            bars1 = ax1.bar(groups, rates)
            month_name1 = self.months_ru[selected_date1.month - 1]
            ax1.set_title(f"Средняя посещаемость по группам за {month_name1} {selected_date1.year}")
            ax1.set_ylabel("Посещаемость (%)")
            ax1.set_ylim(0, 100)
            ax1.tick_params(axis='x', rotation=45)
            self._add_value_labels(ax1, bars1)

            # График 2: Посещаемость по предметам
            ax2 = self.figure2.add_subplot(111)
            subjects = [s.name for s in attendance_by_subject]
            subject_rates = [s.attendance_rate or 0 for s in attendance_by_subject]
            bars2 = ax2.bar(subjects, subject_rates)
            month_name2 = self.months_ru[selected_date2.month - 1]
            ax2.set_title(f"Средняя посещаемость по предметам за {month_name2} {selected_date2.year}")
            ax2.set_ylabel("Посещаемость (%)")
            ax2.set_ylim(0, 100)
            ax2.tick_params(axis='x', rotation=45)
            self._add_value_labels(ax2, bars2)

            # График 3: Количество занятий по предметам за месяц
            ax3 = self.figure3.add_subplot(111)
            monthly_subjects = [s.name for s in subjects_per_month]
            lesson_counts = [s.lesson_count for s in subjects_per_month]
            bars3 = ax3.bar(monthly_subjects, lesson_counts)
            month_name3 = self.months_ru[selected_date3.month - 1]
            ax3.set_title(f"Количество занятий по предметам за {month_name3} {selected_date3.year}")
            ax3.set_ylabel("Количество занятий")
            ax3.tick_params(axis='x', rotation=45)
            self._add_value_labels(ax3, bars3)

            # Автоматическая настройка макета
            self.figure1.tight_layout()
            self.figure2.tight_layout()
            self.figure3.tight_layout()

            # Обновление холстов
            self.canvas1.draw()
            self.canvas2.draw()
            self.canvas3.draw()

        except Exception as e:
            show_error("Ошибка", f"Не удалось построить график: {str(e)}")
            print(show_error("Ошибка", f"Не удалось построить график: {str(e)}"))

    def _add_value_labels(self, ax, bars):
        for bar in bars:
            height = bar.get_height()
            # Format all values as integers for better readability
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')