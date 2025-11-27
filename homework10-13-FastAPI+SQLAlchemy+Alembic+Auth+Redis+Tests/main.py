import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
import uuid

from db_service import DBManager
from validation_pydantic import StudentCreate, StudentUpdate, StudentResponse, FacultyStats, CourseStats, UserRegister, \
    UserLogin, Token
from auth import AuthService
from dep import get_db, get_current_user
from cache_service import cache
from models import User

app = FastAPI(
    title="Student Management API",
    description="API для управления записями студентов с кешированием и фоновыми задачами",
    version="2.0.0"
)


# Фоновая задача для загрузки CSV
async def load_csv_background(filename: str):
    """Фоновая задача загрузки данных из CSV"""
    db = DBManager()
    try:
        result = db.load_from_csv(filename)
        print(f"Фоновая задача завершена: {result}")
    finally:
        db.close()


# Фоновая задача для удаления записей
async def delete_students_background(student_ids: List[str]):
    """Фоновая задача удаления записей"""
    db = DBManager()
    try:
        result = db.delete_students_by_ids(student_ids)
        # Инвалидируем кеш после удаления
        cache.delete_pattern("students:*")
        cache.delete_pattern("faculties:*")
        cache.delete_pattern("courses:*")
        print(f"Фоновая задача удаления завершена: {result}")
    finally:
        db.close()


# Эндпоинты аутентификации (без кеширования)
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


# Защищенные эндпоинты с кешированием
@app.get("/")
async def root(current_user: User = Depends(get_current_user)):
    return {"message": "Student Management API", "version": "2.0.0"}


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
        # Инвалидируем кеш после создания новой записи
        cache.delete_pattern("students:*")
        cache.delete_pattern("faculties:*")
        cache.delete_pattern("courses:*")
        return new_student
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/students/", response_model=List[StudentResponse])
async def get_all_students(
        db: DBManager = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cache_key = "students:all"

    # Пробуем получить из кеша
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    # Если нет в кеше, получаем из БД и кешируем
    students = db.get_all_students()
    cache.set(cache_key, students)
    return students


@app.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(
        student_id: str,
        db: DBManager = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cache_key = f"students:{student_id}"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    student = db.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    cache.set(cache_key, student)
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

    # Инвалидируем кеш
    cache.delete(f"students:{student_id}")
    cache.delete_pattern("students:*")
    cache.delete_pattern("faculties:*")
    cache.delete_pattern("courses:*")

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

    # Инвалидируем кеш
    cache.delete(f"students:{student_id}")
    cache.delete_pattern("students:*")
    cache.delete_pattern("faculties:*")
    cache.delete_pattern("courses:*")

    return {"message": "Запись студента успешно удалена"}


# Эндпоинты с кешированием
@app.get("/faculties/")
async def get_faculties(
        db: DBManager = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cache_key = "faculties:all"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    faculties = db.get_unique_faculties()
    cache.set(cache_key, faculties)
    return faculties


@app.get("/courses/")
async def get_courses(
        db: DBManager = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cache_key = "courses:all"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    courses = db.get_unique_courses()
    cache.set(cache_key, courses)
    return courses


@app.get("/faculties/{faculty_name}/stats")
async def get_faculty_stats(
        faculty_name: str,
        db: DBManager = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cache_key = f"faculties:{faculty_name}:stats"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    students = db.get_students_by_faculty(faculty_name)
    if not students:
        raise HTTPException(status_code=404, detail="Факультет не найден")

    avg_grade = db.get_average_grade_by_faculty(faculty_name)
    result = FacultyStats(
        faculty=faculty_name,
        average_grade=avg_grade,
        student_count=len(students)
    )

    cache.set(cache_key, result.dict())
    return result


@app.get("/courses/{course_name}/stats")
async def get_course_stats(
        course_name: str,
        db: DBManager = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cache_key = f"courses:{course_name}:stats"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    avg_grade = db.get_average_grade_by_course(course_name)
    low_grades = db.get_students_low_grade_by_course(course_name)

    result = CourseStats(
        course=course_name,
        average_grade=avg_grade,
        record_count=len(low_grades)
    )

    cache.set(cache_key, result.dict())
    return result


@app.get("/faculties/{faculty_name}/students")
async def get_faculty_students(
        faculty_name: str,
        db: DBManager = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cache_key = f"faculties:{faculty_name}:students"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    students = db.get_students_by_faculty(faculty_name)
    if not students:
        raise HTTPException(status_code=404, detail="Факультет не найден")

    cache.set(cache_key, students)
    return students


@app.get("/courses/{course_name}/low-grades")
async def get_course_low_grades(
        course_name: str,
        max_grade: int = 30,
        db: DBManager = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    cache_key = f"courses:{course_name}:low_grades:{max_grade}"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    students = db.get_students_low_grade_by_course(course_name, max_grade)
    cache.set(cache_key, students)
    return students


# Новые эндпоинты для фоновых задач
@app.post("/load-csv/")
async def load_csv(
        background_tasks: BackgroundTasks,
        filename: str = "students.csv",
        current_user: User = Depends(get_current_user)
):
    """Загрузка данных из CSV файла в фоновом режиме"""
    background_tasks.add_task(load_csv_background, filename)

    # Инвалидируем кеш
    cache.delete_pattern("students:*")
    cache.delete_pattern("faculties:*")
    cache.delete_pattern("courses:*")

    return {"message": f"Задача загрузки данных из {filename} запущена в фоновом режиме"}


@app.post("/delete-students/")
async def delete_students(
        background_tasks: BackgroundTasks,
        student_ids: List[str],
        current_user: User = Depends(get_current_user)
):
    """Удаление записей по списку ID в фоновом режиме"""
    if not student_ids:
        raise HTTPException(status_code=400, detail="Список ID не может быть пустым")

    background_tasks.add_task(delete_students_background, student_ids)

    return {"message": f"Задача удаления {len(student_ids)} записей запущена в фоновом режиме"}


@app.post("/clear-cache/")
async def clear_cache(current_user: User = Depends(get_current_user)):
    """Очистка всего кеша"""
    cache.clear_all()
    return {"message": "Кеш успешно очищен"}


if __name__ == "__main__":
    # посмотреть http://127.0.0.1:8000/docs
    uvicorn.run(app, host="0.0.0.0", port=8000)