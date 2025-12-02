from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

    # Обратное отношение
    students = relationship("Student", back_populates="group")

    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}', description='{self.description}')>"