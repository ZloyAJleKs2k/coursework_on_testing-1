from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from models import Base


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)

    # Обратное отношение
    group = relationship("Group", back_populates="students")
    attendance = relationship("Attendance", back_populates="student")  # Добавлено обратное отношение

    def __repr__(self):
        return f"<Student(id={self.id}, full_name='{self.full_name}')>"


