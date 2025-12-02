from sqlalchemy import Column, Integer, ForeignKey, String, CheckConstraint, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from models import Base


class Attendance(Base):
    __tablename__ = 'attendance'

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), primary_key=True)
    status = Column(String(20),
                    CheckConstraint("status IN ('present', 'absent', 'late', 'sick')")) 

    student = relationship("Student", back_populates="attendance")
    lesson = relationship("Lesson", back_populates="attendance")

    def __repr__(self):
        return (f"<Attendance(student_id={self.student_id}, lesson_id={self.lesson_id}, status='{self.status}'")


class AttendanceReport(Base):
    __tablename__ = 'attendance_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), nullable=False)
    report_date = Column(TIMESTAMP, default=TIMESTAMP)
    status = Column(String(20),
                    CheckConstraint("status IN ('present', 'absent', 'late', 'sick')"))

    student = relationship("Student")
    lesson = relationship("Lesson")

    def __repr__(self):
        return f"<AttendanceReport(id={self.id}, student_id={self.student_id}, lesson_id={self.lesson_id}, report_date={self.report_date}, status='{self.status}')>"




