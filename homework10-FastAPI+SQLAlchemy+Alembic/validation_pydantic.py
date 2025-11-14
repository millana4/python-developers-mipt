from pydantic import BaseModel, Field
from typing import Optional
import uuid

# Базовые схемы
class StudentBase(BaseModel):
    surname: str = Field(..., min_length=1, max_length=50, description="Фамилия студента")
    name: str = Field(..., min_length=1, max_length=50, description="Имя студента")
    faculty: str = Field(..., min_length=1, max_length=50, description="Факультет")
    course: str = Field(..., min_length=1, max_length=50, description="Название предмета")
    grade: int = Field(..., ge=0, le=100, description="Оценка (0-100)")

# Схема для создания
class StudentCreate(StudentBase):
    pass

# Схема для обновления
class StudentUpdate(BaseModel):
    surname: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    faculty: Optional[str] = Field(None, min_length=1, max_length=50)
    course: Optional[str] = Field(None, min_length=1, max_length=50)
    grade: Optional[int] = Field(None, ge=0, le=100)

# Схема для ответа
class StudentResponse(StudentBase):
    uuid: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# Схемы для аналитических данных
class FacultyStats(BaseModel):
    faculty: str
    average_grade: float
    student_count: int

class CourseStats(BaseModel):
    course: str
    average_grade: float
    record_count: int