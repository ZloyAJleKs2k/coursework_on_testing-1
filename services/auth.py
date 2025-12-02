from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_session
from models import User
from sqlalchemy.exc import SQLAlchemyError

from utils import get_logger

logger = get_logger()


class AuthService:
    @staticmethod
    def register(username: str, password: str, role: str = "student", email: str = "") -> bool:
        try:
            with get_session() as db:
                # Проверка с учетом регистра и пробелов
                clean_login = username.strip().lower()
                existing_login = db.query(User).filter(
                    func.lower(User.login) == clean_login
                ).first()

                existing_email = db.query(User).filter(
                    func.lower(User.email) == email.strip().lower()
                ).first()

                if existing_login:
                    logger.error(f"Login conflict: {username} vs {existing_login.login}")
                    return False

                if existing_email:
                    logger.error(f"Email conflict: {email} vs {existing_email.email}")
                    return False

                new_user = User(
                    login=username.strip(),
                    password=generate_password_hash(password),
                    role=role,
                    email=email.strip()
                )

                db.add(new_user)
                db.commit()  # Явный коммит
                return True

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def login(username: str, password: str) -> tuple[bool, str, int]:
        """Authenticate user and return success status, role and user id"""
        try:
            with get_session() as db:
                user = db.query(User).filter(User.login == username).first()
                if user and check_password_hash(user.password, password):
                    return True, user.role, user.id
                return False, '', 0
        except SQLAlchemyError as e:
            logger.error(f"Login error: {str(e)}")
            return False, '', 0
