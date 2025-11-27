import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from models import Base, Student, User
from auth import AuthService
import uuid
from datetime import datetime

# Тестовая база данных
TEST_DATABASE_URL = "sqlite:///./test_students.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Переопределяем зависимость для тестов
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Создаем тестового клиента
client = TestClient(app)


# Фикстуры для тестов
@pytest.fixture(scope="function")
def test_db():
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)
    yield
    # Очищаем после теста
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db):
    """Создание тестового пользователя"""
    db = TestingSessionLocal()
    auth_service = AuthService(db)
    user = auth_service.create_user("testuser", "testpassword")
    db.close()
    return user


@pytest.fixture
def auth_headers(test_user):
    """Получение auth headers"""
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_student_data():
    """Данные для тестового студента"""
    return {
        "surname": "Иванов",
        "name": "Петр",
        "faculty": "ФТФ",
        "course": "Физика",
        "grade": 85
    }


@pytest.fixture
def create_sample_student(auth_headers, sample_student_data):
    """Создание тестового студента"""
    response = client.post("/students/", json=sample_student_data, headers=auth_headers)
    return response.json()


# Тесты для эндпоинта GET /students/
class TestGetAllStudents:
    """Тесты для получения всех студентов"""

    def test_get_all_students_success(self, auth_headers, create_sample_student):
        """Тест успешного получения всех студентов"""
        # Act
        response = client.get("/students/", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["surname"] == "Иванов"
        assert data[0]["name"] == "Петр"
        assert "uuid" in data[0]

    def test_get_all_students_empty(self, auth_headers, test_db):
        """Тест получения пустого списка студентов"""
        # Act
        response = client.get("/students/", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_students_unauthorized(self):
        """Тест доступа без авторизации"""
        # Act
        response = client.get("/students/")

        # Assert
        assert response.status_code == 403


# Тесты для эндпоинта POST /students/
class TestCreateStudent:
    """Тесты для создания студента"""

    def test_create_student_success(self, auth_headers, sample_student_data):
        """Тест успешного создания студента"""
        # Act
        response = client.post("/students/", json=sample_student_data, headers=auth_headers)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["surname"] == sample_student_data["surname"]
        assert data["name"] == sample_student_data["name"]
        assert data["faculty"] == sample_student_data["faculty"]
        assert data["course"] == sample_student_data["course"]
        assert data["grade"] == sample_student_data["grade"]
        assert "uuid" in data
        assert "created_at" in data

    def test_create_student_invalid_data(self, auth_headers):
        """Тест создания студента с невалидными данными"""
        # Arrange
        invalid_data = {
            "surname": "И",  # Слишком короткая фамилия
            "name": "П",  # Слишком короткое имя
            "faculty": "Ф",  # Слишком короткий факультет
            "course": "Ф",  # Слишком короткий курс
            "grade": 150  # Оценка вне диапазона
        }

        # Act
        response = client.post("/students/", json=invalid_data, headers=auth_headers)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_create_student_unauthorized(self, sample_student_data):
        """Тест создания студента без авторизации"""
        # Act
        response = client.post("/students/", json=sample_student_data)

        # Assert
        assert response.status_code == 403


# Тесты для эндпоинта GET /students/{student_id}
class TestGetStudentById:
    """Тесты для получения студента по ID"""

    def test_get_student_by_id_success(self, auth_headers, create_sample_student):
        """Тест успешного получения студента по ID"""
        # Arrange
        student_id = create_sample_student["uuid"]

        # Act
        response = client.get(f"/students/{student_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == student_id
        assert data["surname"] == "Иванов"
        assert data["name"] == "Петр"

    def test_get_student_by_id_not_found(self, auth_headers):
        """Тест получения несуществующего студента"""
        # Arrange
        non_existent_id = str(uuid.uuid4())

        # Act
        response = client.get(f"/students/{non_existent_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 404
        assert "Студент не найден" in response.json()["detail"]

    def test_get_student_by_id_invalid_uuid(self, auth_headers):
        """Тест получения студента с невалидным UUID"""
        # Act
        response = client.get("/students/invalid-uuid", headers=auth_headers)

        # Assert
        assert response.status_code == 422  # Validation error


# Тесты для эндпоинта PUT /students/{student_id}
class TestUpdateStudent:
    """Тесты для обновления студента"""

    def test_update_student_success(self, auth_headers, create_sample_student):
        """Тест успешного обновления студента"""
        # Arrange
        student_id = create_sample_student["uuid"]
        update_data = {
            "grade": 95,
            "course": "Математика"
        }

        # Act
        response = client.put(f"/students/{student_id}", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == student_id
        assert data["grade"] == 95
        assert data["course"] == "Математика"
        # Проверяем, что остальные поля не изменились
        assert data["surname"] == "Иванов"
        assert data["name"] == "Петр"

    def test_update_student_partial_data(self, auth_headers, create_sample_student):
        """Тест частичного обновления студента"""
        # Arrange
        student_id = create_sample_student["uuid"]
        update_data = {
            "grade": 90  # Только одно поле
        }

        # Act
        response = client.put(f"/students/{student_id}", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["grade"] == 90
        assert data["surname"] == "Иванов"  # Остальные поля не изменились

    def test_update_student_not_found(self, auth_headers):
        """Тест обновления несуществующего студента"""
        # Arrange
        non_existent_id = str(uuid.uuid4())
        update_data = {"grade": 95}

        # Act
        response = client.put(f"/students/{non_existent_id}", json=update_data, headers=auth_headers)

        # Assert
        assert response.status_code == 404


# Тесты для эндпоинта DELETE /students/{student_id}
class TestDeleteStudent:
    """Тесты для удаления студента"""

    def test_delete_student_success(self, auth_headers, create_sample_student):
        """Тест успешного удаления студента"""
        # Arrange
        student_id = create_sample_student["uuid"]

        # Act
        response = client.delete(f"/students/{student_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        assert "успешно удалена" in response.json()["message"]

        # Проверяем, что студент действительно удален
        get_response = client.get(f"/students/{student_id}", headers=auth_headers)
        assert get_response.status_code == 404

    def test_delete_student_not_found(self, auth_headers):
        """Тест удаления несуществующего студента"""
        # Arrange
        non_existent_id = str(uuid.uuid4())

        # Act
        response = client.delete(f"/students/{non_existent_id}", headers=auth_headers)

        # Assert
        assert response.status_code == 404


# Тесты для эндпоинта GET /faculties/{faculty_name}/stats
class TestGetFacultyStats:
    """Тесты для получения статистики по факультету"""

    def test_get_faculty_stats_success(self, auth_headers, create_sample_student):
        """Тест успешного получения статистики по факультету"""
        # Arrange
        faculty_name = "ФТФ"

        # Act
        response = client.get(f"/faculties/{faculty_name}/stats", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["faculty"] == faculty_name
        assert "average_grade" in data
        assert "student_count" in data
        assert isinstance(data["average_grade"], (int, float))
        assert isinstance(data["student_count"], int)

    def test_get_faculty_stats_not_found(self, auth_headers):
        """Тест получения статистики по несуществующему факультету"""
        # Arrange
        non_existent_faculty = "НесуществующийФакультет"

        # Act
        response = client.get(f"/faculties/{non_existent_faculty}/stats", headers=auth_headers)

        # Assert
        assert response.status_code == 404

    def test_get_faculty_stats_calculation(self, auth_headers):
        """Тест правильности расчета статистики"""
        # Arrange - создаем нескольких студентов одного факультета
        students_data = [
            {"surname": "Иванов", "name": "Петр", "faculty": "ФТФ", "course": "Физика", "grade": 80},
            {"surname": "Петров", "name": "Иван", "faculty": "ФТФ", "course": "Математика", "grade": 90},
            {"surname": "Сидоров", "name": "Алексей", "faculty": "ФТФ", "course": "Информатика", "grade": 70}
        ]

        for student_data in students_data:
            client.post("/students/", json=student_data, headers=auth_headers)

        # Act
        response = client.get("/faculties/ФТФ/stats", headers=auth_headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["student_count"] == 3
        # Средняя оценка: (80 + 90 + 70) / 3 = 80
        assert data["average_grade"] == 80.0


# Дополнительные интеграционные тесты
class TestIntegrationScenarios:
    """Интеграционные тесты сценариев"""

    def test_full_crud_cycle(self, auth_headers, sample_student_data):
        """Полный цикл CRUD операций"""
        # 1. Create
        create_response = client.post("/students/", json=sample_student_data, headers=auth_headers)
        assert create_response.status_code == 201
        student_id = create_response.json()["uuid"]

        # 2. Read
        get_response = client.get(f"/students/{student_id}", headers=auth_headers)
        assert get_response.status_code == 200
        assert get_response.json()["grade"] == 85

        # 3. Update
        update_response = client.put(f"/students/{student_id}", json={"grade": 95}, headers=auth_headers)
        assert update_response.status_code == 200
        assert update_response.json()["grade"] == 95

        # 4. Delete
        delete_response = client.delete(f"/students/{student_id}", headers=auth_headers)
        assert delete_response.status_code == 200

        # 5. Verify deletion
        verify_response = client.get(f"/students/{student_id}", headers=auth_headers)
        assert verify_response.status_code == 404

    def test_authentication_flow(self, test_db):
        """Тест полного цикла аутентификации"""
        # 1. Регистрация
        register_data = {"username": "newuser", "password": "newpassword"}
        register_response = client.post("/auth/register", json=register_data)
        assert register_response.status_code == 200

        # 2. Логин
        login_response = client.post("/auth/login", json=register_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Доступ к защищенному эндпоинту
        students_response = client.get("/students/", headers=headers)
        assert students_response.status_code == 200

        # 4. Логаут
        logout_response = client.post("/auth/logout", headers=headers)
        assert logout_response.status_code == 200