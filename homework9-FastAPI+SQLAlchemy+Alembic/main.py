from db_service import DBManager


def main():
    db = DBManager()

    try:
        # Загружаем данные из CSV
        print("Загрузка данных из CSV...")
        db.load_from_csv("students.csv")

        print("=" * 60)

        # 1. Все записи
        print("=== Все записи в базе ===")
        students = db.select()
        for student in students:
            print(f"{student.surname} {student.name}, {student.faculty}, {student.course}: {student.grade}")

        print("=" * 60)

        # 2. Записи по факультету
        print("\n=== Записи факультета 'ФТФ' ===")
        ftf_students = db.get_students_by_faculty("ФТФ")
        for student in ftf_students:
            print(f"{student.surname} {student.name}, {student.course}: {student.grade}")

        print("=" * 60)

        # 3. Уникальные предметы
        print("\n=== Уникальные предметы ===")
        courses = db.get_unique_courses()
        for course in courses:
            print(f"Предмет: {course}")

        print("=" * 60)

        # 4. Средний балл по факультетам
        print("\n=== Средний балл по факультетам ===")
        faculties = db.get_unique_faculties()
        for faculty in faculties:
            avg_grade = db.get_average_grade_by_faculty(faculty)
            print(f"{faculty}: {avg_grade}")

        print("=" * 60)

        # 5. Записи с низкой оценкой по предметам
        print("\n=== Записи с оценкой ниже 30 по предметам ===")
        for course in courses:
            low_grade_students = db.get_students_low_grade_by_course(course)
            if low_grade_students:
                print(f"\nПредмет '{course}':")
                for student in low_grade_students:
                    print(f"  {student.surname} {student.name}: {student.grade}")

        print("=" * 60)

        # 6. ДОПОЛНИТЕЛЬНО: Средний балл по предметам
        print("\n=== Средний балл по предметам ===")
        for course in courses:
            avg_grade = db.get_average_grade_by_course(course)
            print(f"{course}: {avg_grade}")

        print("=" * 60)

        # 7. ДОПОЛНИТЕЛЬНО: Записи конкретного студента
        print("\n=== Все записи студента Смит Федор ===")
        smith_records = db.get_student_records("Смит", "Федор")
        for record in smith_records:
            print(f"{record.course}: {record.grade}")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()