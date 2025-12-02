from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from models import Base



class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    def __repr__(self):
        return f"<Subject(id={self.id}, name='{self.name}', description='{self.description}')>"


class Teacher(Base):
    __tablename__ = 'teachers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    patronymic = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    phone = Column(String(15))

    user = relationship("User", backref="teacher_profile")
    lessons = relationship("Lesson", back_populates="teacher")  # Добавлено обратное отношение

    def __repr__(self):
        return f"<Teacher(id={self.id}, name='{self.last_name} {self.first_name}', phone='{self.phone}')>"


class TeacherSubject(Base):
    __tablename__ = 'teacher_subjects'

    teacher_id = Column(Integer, ForeignKey('teachers.id'), primary_key=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), primary_key=True)

    teacher = relationship("Teacher", backref="teacher_subjects")
    subject = relationship("Subject", backref="teacher_subjects")


class TeacherGroup(Base):
    __tablename__ = 'teacher_groups'

    teacher_id = Column(Integer, ForeignKey('teachers.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)

    teacher = relationship("Teacher", backref="teacher_groups")
    group = relationship("Group", backref="teacher_groups")



