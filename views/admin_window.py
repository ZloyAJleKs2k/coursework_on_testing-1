from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QDialog, QFormLayout, QLineEdit, QMessageBox,
                             QHeaderView, QComboBox, QLabel, QCheckBox)
from PyQt5.QtCore import Qt

from database import get_session
from models import User, Student, Teacher, Group, Subject, Lesson, TeacherSubject
from utils import show_error, show_info, handle_exceptions
from utils import get_logger
from datetime import datetime

logger = get_logger()


class EditDialog(QDialog):
    def __init__(self, model_class, item=None, parent=None):
        super().__init__(parent)
        self.model_class = model_class
        self.item = item
        self.fields = {}
        self.subject_checkboxes = []
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        
        # Define fields based on model class
        if self.model_class == User:
            fields = ['login', 'password', 'role', 'email']
        elif self.model_class == Student:
            fields = ['full_name', 'group_id']
        elif self.model_class == Teacher:
            fields = ['first_name', 'last_name', 'patronymic', 'user_id', 'phone']
            # Add subjects selection for teachers
            self.add_subject_selection(layout)
        elif self.model_class == Group:
            fields = ['id', 'name', 'description']
        elif self.model_class == Subject:
            fields = ['name', 'description']
        elif self.model_class == Lesson:
            fields = ['subject_id', 'date_time', 'teacher_id', 'group_id', 'location']
        
        # Create input fields
        for field in fields:
            if field == 'role':
                self.fields[field] = QComboBox()
                self.fields[field].addItems(['student', 'teacher', 'admin'])
            elif field == 'group_id':
                self.fields[field] = QComboBox()
                self.load_groups()
            elif field == 'teacher_id':
                self.fields[field] = QComboBox()
                self.load_teachers()
            elif field == 'subject_id':
                self.fields[field] = QComboBox()
                self.load_subjects()
            elif field == 'date_time':
                self.fields[field] = QLineEdit()
                self.fields[field].setPlaceholderText('YYYY-MM-DD HH:MM')
            else:
                self.fields[field] = QLineEdit()
            
            # Set existing values if editing
            if self.item:
                if isinstance(self.fields[field], QComboBox):
                    if field == 'teacher_id':
                        for i in range(self.fields[field].count()):
                            if str(self.fields[field].itemData(i)) == str(getattr(self.item, field, '')):
                                self.fields[field].setCurrentIndex(i)
                                break
                    elif field == 'subject_id':
                        for i in range(self.fields[field].count()):
                            if str(self.fields[field].itemData(i)) == str(getattr(self.item, field, '')):
                                self.fields[field].setCurrentIndex(i)
                                break
                    elif field == 'group_id':
                        self.fields[field].setCurrentText(str(getattr(self.item, field, '')))
                    else:
                        self.fields[field].setCurrentText(str(getattr(self.item, field, '')))
                else:
                    self.fields[field].setText(str(getattr(self.item, field, '')))
            
            layout.addRow(field.replace('_', ' ').title() + ':', self.fields[field])
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton('Save')
        cancel_button = QPushButton('Cancel')
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addRow(buttons_layout)
        
        self.setLayout(layout)
    
    def load_teachers(self):
        try:
            with get_session() as db:
                teachers = db.query(Teacher).all()
                self.fields['teacher_id'].clear()
                for teacher in teachers:
                    display_name = f"{teacher.last_name} {teacher.first_name}"
                    self.fields['teacher_id'].addItem(display_name, teacher.id)
        except Exception as e:
            logger.error(f"Error loading teachers: {str(e)}")
            show_error("Error", "Failed to load teachers")

    def load_subjects(self):
        try:
            with get_session() as db:
                subjects = db.query(Subject).all()
                self.fields['subject_id'].clear()
                for subject in subjects:
                    self.fields['subject_id'].addItem(subject.name, str(subject.id))
        except Exception as e:
            logger.error(f"Error loading subjects: {str(e)}")
            show_error("Error", "Failed to load subjects")

    def load_groups(self):
        try:
            with get_session() as db:
                groups = db.query(Group).all()
                self.fields['group_id'].clear()
                for group in groups:
                    self.fields['group_id'].addItem(str(group.id), group.id)  # Store ID as item data
        except Exception as e:
            logger.error(f"Error loading groups: {str(e)}")
            show_error("Error", "Failed to load groups")
    
    def add_subject_selection(self, layout):
        if self.model_class == Teacher:
            try:
                with get_session() as db:
                    subjects = db.query(Subject).all()
                    if subjects:
                        layout.addRow(QLabel("Subjects:"))
                        for subject in subjects:
                            checkbox = QCheckBox(subject.name)
                            if self.item:
                                # Check if teacher teaches this subject
                                teacher_subject = db.query(TeacherSubject).filter_by(
                                    teacher_id=self.item.id,
                                    subject_id=subject.id
                                ).first()
                                checkbox.setChecked(bool(teacher_subject))
                            checkbox.setProperty("subject_id", subject.id)
                            self.subject_checkboxes.append(checkbox)
                            layout.addRow("", checkbox)
            except Exception as e:
                logger.error(f"Error loading subjects: {str(e)}")
                show_error("Error", "Failed to load subjects")

    def get_data(self):
        data = {}
        for field, widget in self.fields.items():
            if isinstance(widget, QComboBox):
                if field in ['teacher_id', 'subject_id', 'group_id']:
                    data[field] = str(widget.currentData())
                else:
                    data[field] = widget.currentText()
            else:
                data[field] = widget.text()

        # Handle subject selections for teachers
        if self.model_class == Teacher and self.subject_checkboxes:
            data['selected_subjects'] = [
                checkbox.property("subject_id")
                for checkbox in self.subject_checkboxes
                if checkbox.isChecked()
            ]
        return data


class ModelTab(QWidget):
    def __init__(self, model_class, headers):
        super().__init__()
        self.model_class = model_class
        self.headers = headers
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton('Добавить')
        self.edit_button = QPushButton('Редактировать')
        self.delete_button = QPushButton('Удалить')
        
        self.add_button.clicked.connect(self.add_item)
        self.edit_button.clicked.connect(self.edit_item)
        self.delete_button.clicked.connect(self.delete_item)
        
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.delete_button)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        layout.addLayout(buttons_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
    
    @handle_exceptions
    def load_data(self):
        try:
            with get_session() as db:
                items = db.query(self.model_class).all()
                self.table.setRowCount(len(items))
                
                # Define header to field mapping
                header_mapping = {
                    'Логин': 'login',
                    'Роль': 'role',
                    'Email': 'email',
                    'Полное имя': 'full_name',
                    'ID Группы': 'group_id',
                    'Имя': 'first_name',
                    'Фамилия': 'last_name',
                    'Отчество': 'patronymic',
                    'ID Пользваотеля': 'user_id',
                    'Телефон': 'phone',
                    'ID': 'id',
                    'Название': 'name',
                    'Описание': 'description',
                    'ID Предмета': 'subject_id',
                    'Дата': 'date_time',
                    'ID Учителя': 'teacher_id',
                    'Локация': 'location'
                }
                
                for row, item in enumerate(items):
                    for col, header in enumerate(self.headers):
                        field = header_mapping.get(header, header.lower().replace(' ', '_'))
                        value = str(getattr(item, field, ''))
                        
                        if field == 'date_time' and value:
                            try:
                                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                                value = dt.strftime('%d.%m.%Y %H:%M')
                            except:
                                pass
                                
                        self.table.setItem(row, col, QTableWidgetItem(value))
                    self.table.item(row, 0).setData(Qt.UserRole, item.id)
                    
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            show_error("Error", "Failed to load data")
    
    def add_item(self):
        dialog = EditDialog(self.model_class, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                with get_session() as db:
                    data = dialog.get_data()
                    selected_subjects = data.pop('selected_subjects', [])
                    
                    # Hash password for User model
                    if self.model_class == User and 'password' in data:
                        from werkzeug.security import generate_password_hash
                        data['password'] = generate_password_hash(data['password'])
                    
                    new_item = self.model_class(**data)
                    db.add(new_item)
                    db.flush()

                    # Handle teacher-subject relationships
                    if self.model_class == Teacher and selected_subjects:
                        for subject_id in selected_subjects:
                            teacher_subject = TeacherSubject(
                                teacher_id=new_item.id,
                                subject_id=subject_id
                            )
                            db.add(teacher_subject)

                    db.commit()
                    show_info("Success", "Item added successfully")
                    self.load_data()
            except Exception as e:
                logger.error(f"Error adding item: {str(e)}")
                show_error("Error", "Failed to add item")
    
    def edit_item(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            show_error("Error", "Please select an item to edit")
            return
        
        item_id = self.table.item(selected_items[0].row(), 0).data(Qt.UserRole)
        try:
            with get_session() as db:
                item = db.query(self.model_class).get(item_id)
                if not item:
                    show_error("Error", "Item not found")
                    return
                
                dialog = EditDialog(self.model_class, item, parent=self)
                if dialog.exec_() == QDialog.Accepted:
                    data = dialog.get_data()
                    selected_subjects = data.pop('selected_subjects', [])
                    
                    # Hash password for User model if password was changed
                    if self.model_class == User and 'password' in data and data['password']:
                        from werkzeug.security import generate_password_hash
                        data['password'] = generate_password_hash(data['password'])
                    elif self.model_class == User and 'password' in data and not data['password']:
                        # If password field is empty during edit, remove it to keep the existing password
                        del data['password']

                    for key, value in data.items():
                        setattr(item, key, value)

                    # Update teacher-subject relationships
                    if self.model_class == Teacher:
                        # Remove existing relationships
                        db.query(TeacherSubject).filter_by(teacher_id=item.id).delete()
                        # Add new relationships
                        for subject_id in selected_subjects:
                            teacher_subject = TeacherSubject(
                                teacher_id=item.id,
                                subject_id=subject_id
                            )
                            db.add(teacher_subject)

                    db.commit()
                    show_info("Success", "Item updated successfully")
                    self.load_data()
        except Exception as e:
            logger.error(f"Error editing item: {str(e)}")
            show_error("Error", "Failed to edit item")
    
    def delete_item(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            show_error("Error", "Please select an item to delete")
            return
        
        confirm = QMessageBox.question(
            self, 'Confirm Deletion',
            'Are you sure you want to delete this item?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            item_id = self.table.item(selected_items[0].row(), 0).data(Qt.UserRole)
            try:
                with get_session() as db:
                    item = db.query(self.model_class).get(item_id)
                    if item:
                        db.delete(item)
                        db.commit()
                        show_info("Success", "Item deleted successfully")
                        self.load_data()
                    else:
                        show_error("Error", "Item not found")
            except Exception as e:
                logger.error(f"Error deleting item: {str(e)}")
                show_error("Error", "Failed to delete item")


class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Админ Панель")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Add refresh button at the top
        refresh_button = QPushButton('Обновить данные')
        refresh_button.clicked.connect(self.refresh_all_tabs)
        layout.addWidget(refresh_button)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Users tab
        users_tab = ModelTab(User, ['Логин', 'Роль', 'Email'])
        tabs.addTab(users_tab, "Пользователи")
        
        # Students tab
        students_tab = ModelTab(Student, ['Полное имя', 'ID Группы'])
        tabs.addTab(students_tab, "Студенты")
        
        # Teachers tab
        teachers_tab = ModelTab(Teacher, ['Имя', 'Фамилия', 'Отчество', 'ID Пользваотеля', 'Телефон'])
        tabs.addTab(teachers_tab, "Учителя")
        
        # Groups tab
        groups_tab = ModelTab(Group, ['ID', 'Название', 'Описание'])
        tabs.addTab(groups_tab, "Группы")

        # Subjects tab
        subjects_tab = ModelTab(Subject, ['Название', 'Описание'])
        tabs.addTab(subjects_tab, "Предметы")

        # Lessons tab
        lessons_tab = ModelTab(Lesson, ['ID Предмета', 'Дата', 'ID Учителя', 'ID Группы', 'Локация'])
        tabs.addTab(lessons_tab, "Занятия")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Store tabs for refresh functionality
        self.tabs = tabs
    
    def refresh_all_tabs(self):
        # Refresh data in all tabs
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if isinstance(tab, ModelTab):
                tab.load_data()

