from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from models import Base


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    date_time = Column(TIMESTAMP, default=TIMESTAMP)
    teacher_id = Column(Integer, ForeignKey('teachers.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    location = Column(String(100))

    subject = relationship("Subject")
    teacher = relationship("Teacher", back_populates="lessons")
    attendance = relationship("Attendance", back_populates="lesson")  # Добавлено обратное отношение
    group = relationship("Group")

    def __repr__(self):
        return (f"<Lesson(id={self.id}, subject_id={self.subject_id}, date_time={self.date_time},"
                f" location='{self.location}')>")







