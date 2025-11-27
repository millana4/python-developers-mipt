from sqlalchemy import Column, Integer, String, Boolean
from base import Base, BaseModelMixin


class Student(Base, BaseModelMixin):
    __tablename__ = 'students'

    surname = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    faculty = Column(String(50), nullable=False)
    course = Column(String(50), nullable=False)
    grade = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Student(name='{self.name}', surname='{self.surname}')>"


class User(Base, BaseModelMixin):
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)