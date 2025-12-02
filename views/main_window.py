from PyQt5.QtWidgets import QMainWindow, QTabWidget, QStatusBar
# from widgets.calendar import CalendarWidget
from widgets.stats import StatsWidget
from .schedule_window import ScheduleWindow
from .attendance_window import AttendanceWindow
from .admin_window import AdminWindow
from .reports_window import ReportsWindow
from utils import admin_required, handle_exceptions
from utils import get_logger

logger = get_logger()


class MainWindow(QMainWindow):
    def __init__(self, role: str, user_id: int):
        super().__init__()
        self.role = role
        self.current_user_id = user_id
        self.setWindowTitle("Система учета посещаемости")
        self.setMinimumSize(800, 600)
        self.init_ui()
        logger.info(f"Создано главное окно для роли: {role}")

    @handle_exceptions
    def init_ui(self):
        # Создание вкладок
        self.tabs = QTabWidget()

        # Основные вкладки
        self.tabs.addTab(ScheduleWindow(role=self.role), "Расписание")
        self.tabs.addTab(AttendanceWindow(role=self.role, user_id=self.current_user_id), "Посещаемость")

        # Виджеты для администратора
        if self.role == 'admin':
            self.tabs.addTab(AdminWindow(), "Управление")
            # self.tabs.addTab(CalendarWidget(), "Календарь")
            self.tabs.addTab(StatsWidget(), "Статистика")
            self.tabs.addTab(ReportsWindow(role=self.role, user_id=self.current_user_id), "Отчеты")
        
        # Добавляем вкладку статистики и отчетов для учителей
        elif self.role == 'teacher':
            self.tabs.addTab(StatsWidget(), "Статистика")
            self.tabs.addTab(ReportsWindow(role=self.role, user_id=self.current_user_id), "Отчеты")

        self.setCentralWidget(self.tabs)

        # Статус бар
        self.statusBar().showMessage(f"Вы вошли как: {self.role.capitalize()}")

        # Меню
        self.init_menu()

    @admin_required
    @handle_exceptions
    def init_menu(self):
        menu = self.menuBar()

        # Меню Файл
        file_menu = menu.addMenu("Файл")
        exit_action = file_menu.addAction("Выход")
        exit_action.triggered.connect(self.close)

        # # Меню Админ (только для администраторов)
        # if self.role == 'admin':
        #     admin_menu = menu.addMenu("Администрирование")

