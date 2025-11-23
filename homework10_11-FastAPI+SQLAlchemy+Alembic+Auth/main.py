import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List

from db_service import DBManager
from validation_pydantic import StudentCreate, StudentUpdate, StudentResponse, FacultyStats, CourseStats, UserRegister, UserLogin, Token
from auth import AuthService
from dep import get_db, get_current_user
from models import User

app = FastAPI(
    title="Student Management API",
    description="API для управления записями студентов",
    version="1.0.0"
)

# Эндпоинты аутентификации
@app.post("/auth/register")
async def register(user_data: UserRegister, db=Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.create_user(user_data.username, user_data.password)
    return {"message": "User created successfully", "username": user.username}

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db=Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(user_data.username, user_data.password)
    access_token = auth_service.create_access_token(user.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

# Защищенные эндпоинты
@app.get("/")
async def root(current_user: User = Depends(get_current_user)):
    return {"message": "Student Management API", "version": "1.0.0"}

@app.post("/students/", response_model=StudentResponse, status_code=201)
async def create_student(
    student: StudentCreate,
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        new_student = db.create_student(
            surname=student.surname,
            name=student.name,
            faculty=student.faculty,
            course=student.course,
            grade=student.grade
        )
        return new_student
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/students/", response_model=List[StudentResponse])
async def get_all_students(
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.get_all_students()

@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: str,
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    student = db.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return student

@app.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: str,
    student_data: StudentUpdate,
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_data = {k: v for k, v in student_data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")
    updated_student = db.update_student(student_id, **update_data)
    if not updated_student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return updated_student

@app.delete("/students/{student_id}")
async def delete_student(
    student_id: str,
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = db.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Студент не найден")
    return {"message": "Запись студента успешно удалена"}

# Все остальные эндпоинты аналогично защищаем current_user
@app.get("/faculties/")
async def get_faculties(
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.get_unique_faculties()

@app.get("/courses/")
async def get_courses(
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.get_unique_courses()

@app.get("/faculties/{faculty_name}/stats")
async def get_faculty_stats(
    faculty_name: str,
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    students = db.get_students_by_faculty(faculty_name)
    if not students:
        raise HTTPException(status_code=404, detail="Факультет не найден")
    avg_grade = db.get_average_grade_by_faculty(faculty_name)
    return FacultyStats(
        faculty=faculty_name,
        average_grade=avg_grade,
        student_count=len(students)
    )

@app.get("/courses/{course_name}/stats")
async def get_course_stats(
    course_name: str,
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    avg_grade = db.get_average_grade_by_course(course_name)
    low_grades = db.get_students_low_grade_by_course(course_name)
    return CourseStats(
        course=course_name,
        average_grade=avg_grade,
        record_count=len(low_grades)
    )

@app.get("/faculties/{faculty_name}/students")
async def get_faculty_students(
    faculty_name: str,
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    students = db.get_students_by_faculty(faculty_name)
    if not students:
        raise HTTPException(status_code=404, detail="Факультет не найден")
    return students

@app.get("/courses/{course_name}/low-grades")
async def get_course_low_grades(
    course_name: str,
    max_grade: int = 30,
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    students = db.get_students_low_grade_by_course(course_name, max_grade)
    return students

@app.post("/load-csv/")
async def load_csv(
    db: DBManager = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db.load_from_csv("students.csv")
        return {"message": "Данные успешно загружены из CSV"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки: {str(e)}")

if __name__ == "__main__":
    # посмотреть http://127.0.0.1:8000/docs
    uvicorn.run(app, host="0.0.0.0", port=8000)