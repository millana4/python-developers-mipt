import csv
from sqlalchemy import create_engine, func, and_, cast, Integer
from sqlalchemy.orm import sessionmaker
from models import Student, Base


class DBManager:
    def __init__(self, db_url='sqlite:///students.sqlite'):
        self.engine = create_engine(db_url, echo=True)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def insert(self, surname, name, faculty, course, grade):
        student = Student(
            surname=surname,
            name=name,
            faculty=faculty,
            course=course,
            grade=grade,
        )
        self.session.add(student)
        self.session.commit()

    def select(self):
        students = self.session.query(Student).all()
        return students

    def load_from_csv(self, filename="students.csv"):
        with open(filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                if len(row) >= 5:
                    try:
                        # Преобразуем оценку в число
                        grade = int(row[4].strip())
                        student = Student(
                            surname=row[0].strip(),
                            name=row[1].strip(),
                            faculty=row[2].strip(),
                            course=row[3].strip(),  # название предмета
                            grade=grade
                        )
                        self.session.add(student)
                    except ValueError as e:
                        print(f"Ошибка преобразования оценки '{row[4]}': {e}")
                        continue

            self.session.commit()

    # 1. Получение записей по названию факультета
    def get_students_by_faculty(self, faculty_name):
        """Возвращает все записи указанного факультета"""
        students = self.session.query(Student).filter(
            Student.faculty == faculty_name
        ).all()
        return students

    # 2. Получение списка уникальных предметов (курсов)
    def get_unique_courses(self):
        """Возвращает список уникальных предметов"""
        courses = self.session.query(Student.course).distinct().all()
        return [course[0] for course in courses]

    # 3. Получение среднего балла по факультету
    def get_average_grade_by_faculty(self, faculty_name):
        """Возвращает средний балл для указанного факультета"""
        avg_grade = self.session.query(
            func.avg(Student.grade)
        ).filter(
            Student.faculty == faculty_name
        ).scalar()

        return round(avg_grade, 2) if avg_grade is not None else 0

    # 4. Получение записей по предмету с оценкой ниже 30 баллов
    def get_students_low_grade_by_course(self, course_name, max_grade=30):
        """Возвращает записи указанного предмета с оценкой ниже max_grade"""
        students = self.session.query(Student).filter(
            and_(
                Student.course == course_name,
                Student.grade < max_grade
            )
        ).all()
        return students

    # 5. ДОПОЛНИТЕЛЬНО: Получение уникальных факультетов
    def get_unique_faculties(self):
        """Возвращает список уникальных факультетов"""
        faculties = self.session.query(Student.faculty).distinct().all()
        return [faculty[0] for faculty in faculties]

    # 6. ДОПОЛНИТЕЛЬНО: Получение всех записей конкретного студента
    def get_student_records(self, surname, name):
        """Возвращает все записи конкретного студента"""
        records = self.session.query(Student).filter(
            and_(
                Student.surname == surname,
                Student.name == name
            )
        ).all()
        return records

    # 7. ДОПОЛНИТЕЛЬНО: Средний балл по предмету
    def get_average_grade_by_course(self, course_name):
        """Возвращает средний балл по предмету"""
        avg_grade = self.session.query(
            func.avg(Student.grade)
        ).filter(
            Student.course == course_name
        ).scalar()

        return round(avg_grade, 2) if avg_grade is not None else 0

    def close(self):
        self.session.close()



