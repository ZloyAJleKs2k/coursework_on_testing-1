from sqlalchemy import Column, Integer, String, CheckConstraint
from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(256), nullable=False)  # Хранить хеш пароля
    role = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'teacher', 'student')"),
    )

    def __repr__(self):
        return f"<User  (id={self.id}, login='{self.login}', role='{self.role}', email='{self.email}')>"
