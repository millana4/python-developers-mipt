import csv
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models import Student, Base


class DBManager:
    def __init__(self, db_url='sqlite:///students.sqlite'):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # CREATE операция
    def create_student(self, surname: str, name: str, faculty: str, course: str, grade: int):
        """Создание новой записи студента"""
        try:
            student = Student(
                surname=surname,
                name=name,
                faculty=faculty,
                course=course,
                grade=grade,
            )
            self.session.add(student)
            self.session.commit()
            return student
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Ошибка при создании записи")
        except Exception as e:
            self.session.rollback()
            raise e

    # READ операции
    def get_all_students(self):
        """Получение всех записей"""
        return self.session.query(Student).all()

    def get_student_by_id(self, student_id: str):
        """Получение записи по UUID"""
        return self.session.query(Student).filter(Student.uuid == student_id).first()

    def get_students_by_faculty(self, faculty_name: str):
        """Получение записей по факультету"""
        return self.session.query(Student).filter(Student.faculty == faculty_name).all()

    def get_unique_courses(self):
        """Получение уникальных предметов"""
        courses = self.session.query(Student.course).distinct().all()
        return [course[0] for course in courses]

    def get_unique_faculties(self):
        """Получение уникальных факультетов"""
        faculties = self.session.query(Student.faculty).distinct().all()
        return [faculty[0] for faculty in faculties]

    # UPDATE операция
    def update_student(self, student_id: str, **kwargs):
        """Обновление записи студента"""
        try:
            student = self.get_student_by_id(student_id)
            if not student:
                return None

            for key, value in kwargs.items():
                if hasattr(student, key):
                    setattr(student, key, value)

            self.session.commit()
            return student
        except Exception as e:
            self.session.rollback()
            raise e

    # DELETE операция
    def delete_student(self, student_id: str):
        """Удаление записи студента"""
        try:
            student = self.get_student_by_id(student_id)
            if not student:
                return False

            self.session.delete(student)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e

    # Аналитические методы
    def get_average_grade_by_faculty(self, faculty_name: str):
        """Средний балл по факультету"""
        avg_grade = self.session.query(
            func.avg(Student.grade)
        ).filter(Student.faculty == faculty_name).scalar()
        return round(avg_grade, 2) if avg_grade is not None else 0

    def get_students_low_grade_by_course(self, course_name: str, max_grade: int = 30):
        """Записи по предмету с оценкой ниже указанной"""
        return self.session.query(Student).filter(
            and_(Student.course == course_name, Student.grade < max_grade)
        ).all()

    def get_average_grade_by_course(self, course_name: str):
        """Средний балл по предмету"""
        avg_grade = self.session.query(
            func.avg(Student.grade)
        ).filter(Student.course == course_name).scalar()
        return round(avg_grade, 2) if avg_grade is not None else 0

    # Загрузка из CSV
    def load_from_csv(self, filename: str = "students.csv"):
        """Загрузка данных из CSV файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)

                for row in csv_reader:
                    if len(row) >= 5:
                        try:
                            grade = int(row[4].strip())
                            student = Student(
                                surname=row[0].strip(),
                                name=row[1].strip(),
                                faculty=row[2].strip(),
                                course=row[3].strip(),
                                grade=grade
                            )
                            self.session.add(student)
                        except ValueError as e:
                            print(f"Ошибка преобразования оценки '{row[4]}': {e}")
                            continue

                self.session.commit()
        except FileNotFoundError:
            print(f"Файл {filename} не найден")

    def close(self):
        self.session.close()


