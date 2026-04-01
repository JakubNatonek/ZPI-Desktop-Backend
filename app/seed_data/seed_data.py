from datetime import date

from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password
from app.core.database import SessionLocal
from app.models.model_user import User, Role, Department
from app.models.model_teacher import Teacher
from app.models.model_student import Student
from app.models.model_group import Group
from app.models.model_subject import Subject
from app.models.model_room import Room
from app.models.model_semestr import Semestr
from app.models.model_day import Day


def seed_roles():
    """Seed roles table with sample data."""
    db: Session = SessionLocal()
    try:
        roles = [
            {"id": 1, "name": "admin"},
            {"id": 2, "name": "wykładowca"},
            {"id": 3, "name": "student"},
        ]
        for role in roles:
            exists = db.query(Role).filter_by(id=role["id"]).first()
            if not exists:
                db.add(Role(**role))
        db.commit()
        print("Roles seeded.")
    finally:
        db.close()


def seed_departments():
    """Seed departments table with sample data."""
    db: Session = SessionLocal()
    try:
        departments = [
            {"id": 1, "name": "admin"},
            {"id": 2, "name": "Informatyka"},
            {"id": 3, "name": "Fizyka"},
            {"id": 4, "name": "Matematyka"},
            {"id": 5, "name": "Elektronika"},
        ]
        for dep in departments:
            exists = db.query(Department).filter_by(id=dep["id"]).first()
            if not exists:
                db.add(Department(**dep))
        db.commit()
        print("Departments seeded.")
    finally:
        db.close()


def seed_groups():
    """Seed groups table with sample data."""
    db: Session = SessionLocal()
    try:
        groups = [
            {"id": 1, "specialization": "Informatyka Stosowana", "code": "IS1", "year": 1, "studies_type": "stacjonarne"},
            {"id": 2, "specialization": "Informatyka Stosowana", "code": "IS2", "year": 2, "studies_type": "stacjonarne"},
            {"id": 3, "specialization": "Informatyka Stosowana", "code": "IS3", "year": 3, "studies_type": "stacjonarne"},
            {"id": 4, "specialization": "Systemy Komputerowe", "code": "SK1", "year": 1, "studies_type": "stacjonarne"},
            {"id": 5, "specialization": "Systemy Komputerowe", "code": "SK2", "year": 2, "studies_type": "niestacjonarne"},
        ]
        for group in groups:
            exists = db.query(Group).filter_by(id=group["id"]).first()
            if not exists:
                db.add(Group(**group))
        db.commit()
        print("Groups seeded.")
    finally:
        db.close()


def seed_rooms():
    """Seed rooms table with sample data."""
    db: Session = SessionLocal()
    try:
        rooms = [
            {"id": 1, "building": "A", "number": "101", "seats": 30, "description": "Sala wykladowa", "type": "wykladowa", "activities": "wyklad,seminarium"},
            {"id": 2, "building": "A", "number": "102", "seats": 20, "description": "Laboratorium komputerowe", "type": "laboratorium", "activities": "cwiczenia,laboratorium"},
            {"id": 3, "building": "A", "number": "201", "seats": 50, "description": "Aula", "type": "wykladowa", "activities": "wyklad"},
            {"id": 4, "building": "B", "number": "101", "seats": 25, "description": "Sala cwiczeniowa", "type": "cwiczeniowa", "activities": "cwiczenia,seminarium"},
            {"id": 5, "building": "B", "number": "102", "seats": 15, "description": "Laboratorium fizyczne", "type": "laboratorium", "activities": "laboratorium"},
            {"id": 6, "building": "C", "number": "001", "seats": 100, "description": "Duza aula", "type": "wykladowa", "activities": "wyklad,konferencja"},
        ]
        for room in rooms:
            exists = db.query(Room).filter_by(id=room["id"]).first()
            if not exists:
                db.add(Room(**room))
        db.commit()
        print("Rooms seeded.")
    finally:
        db.close()


def seed_subjects():
    """Seed subjects table with sample data."""
    db: Session = SessionLocal()
    try:
        subjects = [
            {"id": 1, "name": "Programowanie obiektowe", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
            {"id": 2, "name": "Programowanie obiektowe", "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium", "blocked": False, "periodic": True},
            {"id": 3, "name": "Bazy danych", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
            {"id": 4, "name": "Bazy danych", "type": "cwiczenia", "type_display": "C", "room_properties": "cwiczeniowa", "blocked": False, "periodic": True},
            {"id": 5, "name": "Algorytmy i struktury danych", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
            {"id": 6, "name": "Algorytmy i struktury danych", "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium", "blocked": False, "periodic": True},
            {"id": 7, "name": "Fizyka", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
            {"id": 8, "name": "Fizyka", "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium", "blocked": False, "periodic": True},
            {"id": 9, "name": "Matematyka dyskretna", "type": "wyklad", "type_display": "W", "room_properties": "wykladowa", "blocked": False, "periodic": True},
            {"id": 10, "name": "Matematyka dyskretna", "type": "cwiczenia", "type_display": "C", "room_properties": "cwiczeniowa", "blocked": False, "periodic": True},
        ]
        for subject in subjects:
            exists = db.query(Subject).filter_by(id=subject["id"]).first()
            if not exists:
                db.add(Subject(**subject))
        db.commit()
        print("Subjects seeded.")
    finally:
        db.close()


def seed_semesters():
    """Seed semesters table with sample data."""
    db: Session = SessionLocal()
    try:
        semesters = [
            {"nazwa": "Semestr zimowy 2025/2026", "data_rozpoczecia": date(2025, 10, 1), "data_zakonczenia": date(2026, 2, 15)},
            {"nazwa": "Semestr letni 2025/2026", "data_rozpoczecia": date(2026, 2, 17), "data_zakonczenia": date(2026, 6, 30)},
            {"nazwa": "Semestr zimowy 2026/2027", "data_rozpoczecia": date(2026, 10, 1), "data_zakonczenia": date(2027, 2, 15)},
        ]

        created_count = 0
        for sem in semesters:
            exists = db.query(Semestr).filter_by(
                nazwa=sem["nazwa"],
                data_rozpoczecia=sem["data_rozpoczecia"],
                data_zakonczenia=sem["data_zakonczenia"],
            ).first()
            if not exists:
                db.add(Semestr(**sem))
                created_count += 1
        db.commit()
        print(f"Semesters seeded. Added: {created_count}")
    finally:
        db.close()


def seed_days():
    """Seed days table with week day IDs used by availability preferences."""
    db: Session = SessionLocal()
    try:
        days = [
            {"id": 1, "name": "monday"},
            {"id": 2, "name": "tuesday"},
            {"id": 3, "name": "wednesday"},
            {"id": 4, "name": "thursday"},
            {"id": 5, "name": "friday"},
            {"id": 6, "name": "saturday"},
            {"id": 7, "name": "sunday"},
        ]

        created_count = 0
        for day in days:
            exists = db.query(Day).filter_by(id=day["id"]).first()
            if not exists:
                db.add(Day(**day))
                created_count += 1

        db.commit()
        print(f"Days seeded. Added: {created_count}")
    finally:
        db.close()


def seed_users_and_profiles():
    """Seed users with teacher and student profiles."""
    db: Session = SessionLocal()
    try:
        # Default password hash for "test123"
        default_password_hash = hash_password("test123")

        # Teachers (role_id=2)
        teachers_data = [
            {
                "user": {"user_id": 2, "first_name": "Jan", "last_name": "Kowalski", "login": "jkowalski", "email": "jan.kowalski@uczelnia.pl", "password_hash": default_password_hash, "role_id": 2, "department_id": 2},
                "teacher": {"title": "dr hab.", "prop": "profesor"}
            },
            {
                "user": {"user_id": 3, "first_name": "Anna", "last_name": "Nowak", "login": "anowak", "email": "anna.nowak@uczelnia.pl", "password_hash": default_password_hash, "role_id": 2, "department_id": 2},
                "teacher": {"title": "dr", "prop": "adiunkt"}
            },
            {
                "user": {"user_id": 4, "first_name": "Piotr", "last_name": "Wisniewski", "login": "pwisniewski", "email": "piotr.wisniewski@uczelnia.pl", "password_hash": default_password_hash, "role_id": 2, "department_id": 3},
                "teacher": {"title": "dr", "prop": "adiunkt"}
            },
            {
                "user": {"user_id": 5, "first_name": "Maria", "last_name": "Zalewska", "login": "mzalewska", "email": "maria.zalewska@uczelnia.pl", "password_hash": default_password_hash, "role_id": 2, "department_id": 4},
                "teacher": {"title": "prof. dr hab.", "prop": "profesor"}
            },
        ]

        for teacher_data in teachers_data:
            user_exists = db.query(User).filter_by(user_id=teacher_data["user"]["user_id"]).first()
            if not user_exists:
                user = User(**teacher_data["user"])
                db.add(user)
                db.flush()
                teacher = Teacher(user_id=user.user_id, **teacher_data["teacher"])
                db.add(teacher)

        # Students (role_id=3)
        students_data = [
            {
                "user": {"user_id": 10, "first_name": "Tomasz", "last_name": "Adamski", "login": "tadamski", "email": "tomasz.adamski@student.uczelnia.pl", "password_hash": default_password_hash, "role_id": 3, "department_id": 2},
                "student": {"index_number": "123456", "group_id": 1, "semester": 1}
            },
            {
                "user": {"user_id": 11, "first_name": "Katarzyna", "last_name": "Bak", "login": "kbak", "email": "katarzyna.bak@student.uczelnia.pl", "password_hash": default_password_hash, "role_id": 3, "department_id": 2},
                "student": {"index_number": "123457", "group_id": 1, "semester": 1}
            },
            {
                "user": {"user_id": 12, "first_name": "Michal", "last_name": "Celinski", "login": "mcelinski", "email": "michal.celinski@student.uczelnia.pl", "password_hash": default_password_hash, "role_id": 3, "department_id": 2},
                "student": {"index_number": "123458", "group_id": 2, "semester": 3}
            },
            {
                "user": {"user_id": 13, "first_name": "Ewa", "last_name": "Dabrowska", "login": "edabrowska", "email": "ewa.dabrowska@student.uczelnia.pl", "password_hash": default_password_hash, "role_id": 3, "department_id": 2},
                "student": {"index_number": "123459", "group_id": 2, "semester": 3}
            },
            {
                "user": {"user_id": 14, "first_name": "Adam", "last_name": "Mazur", "login": "amazur", "email": "adam.mazur@student.uczelnia.pl", "password_hash": default_password_hash, "role_id": 3, "department_id": 2},
                "student": {"index_number": "123460", "group_id": 3, "semester": 5}
            },
        ]

        for student_data in students_data:
            user_exists = db.query(User).filter_by(user_id=student_data["user"]["user_id"]).first()
            if not user_exists:
                user = User(**student_data["user"])
                db.add(user)
                db.flush()
                student = Student(user_id=user.user_id, **student_data["student"])
                db.add(student)

        db.commit()
        print("Users, teachers, and students seeded.")
    finally:
        db.close()


def seed_all():
    """Run all seed functions in correct order."""
    print("Starting database seeding...")
    seed_roles()
    seed_departments()
    seed_groups()
    seed_rooms()
    seed_subjects()
    seed_semesters()
    seed_days()
    seed_users_and_profiles()
    print("Database seeding completed!")


if __name__ == "__main__":
    seed_all()
