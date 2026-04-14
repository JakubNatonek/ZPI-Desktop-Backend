"""
Seed data for mobile-app-related tables.

Creates groups, subjects, student/teacher user profiles, department assignments,
and grade records so the mobile app can fetch meaningful data.

Call seed_mobile_data(db) AFTER seed_departments, seed_roles, seed_titles, and seed_admin.
"""

import random
from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password
from app.cruds.crud_departments_for_user import add_department_to_user
from app.cruds.crud_roles_for_user import add_role_to_user
from app.models.model_department import Department
from app.models.model_department_for_user import DepartmentsForUser
from app.models.model_grade import GradeRecord
from app.models.model_group import Group
from app.models.model_role import Role
from app.models.model_student import Student
from app.models.model_subject import Subject
from app.models.model_teacher import Teacher
from app.models.model_user import User


DEFAULT_PASSWORD_HASH = hash_password("test123")


# ---------------------------------------------------------------------------
# 1) Groups
# ---------------------------------------------------------------------------

GROUPS = [
    {"specialization": "Informatyka Stosowana", "code": "IS1", "year": 1, "studies_type": "stacjonarne", "department_abbr": "WI"},
    {"specialization": "Informatyka Stosowana", "code": "IS2", "year": 2, "studies_type": "stacjonarne", "department_abbr": "WI"},
    {"specialization": "Informatyka Stosowana", "code": "IS3", "year": 3, "studies_type": "stacjonarne", "department_abbr": "WI"},
    {"specialization": "Systemy Komputerowe", "code": "SK1", "year": 1, "studies_type": "stacjonarne", "department_abbr": "WI"},
    {"specialization": "Systemy Komputerowe", "code": "SK2", "year": 2, "studies_type": "niestacjonarne", "department_abbr": "WI"},
]


def _seed_groups(db: Session) -> dict[str, int]:
    """Returns mapping code -> group.id."""
    code_to_id: dict[str, int] = {}
    for g in GROUPS:
        existing = db.query(Group).filter_by(code=g["code"]).first()
        if existing:
            code_to_id[g["code"]] = existing.id
            continue
        dept = db.query(Department).filter_by(abbreviation=g["department_abbr"]).first()
        group = Group(
            specialization=g["specialization"],
            code=g["code"],
            year=g["year"],
            studies_type=g["studies_type"],
            department_id=dept.id if dept else None,
        )
        db.add(group)
        db.flush()
        code_to_id[g["code"]] = group.id
    db.commit()
    print(f"[mobile] Groups seeded: {len(code_to_id)}")
    return code_to_id


# ---------------------------------------------------------------------------
# 2) Subjects
# ---------------------------------------------------------------------------

SUBJECTS = [
    {"name": "Programowanie obiektowe",      "type": "wyklad",       "type_display": "W", "room_properties": "wykladowa",     "blocked": False, "periodic": True},
    {"name": "Programowanie obiektowe",      "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium",  "blocked": False, "periodic": True},
    {"name": "Bazy danych",                  "type": "wyklad",       "type_display": "W", "room_properties": "wykladowa",     "blocked": False, "periodic": True},
    {"name": "Bazy danych",                  "type": "cwiczenia",    "type_display": "C", "room_properties": "cwiczeniowa",   "blocked": False, "periodic": True},
    {"name": "Algorytmy i struktury danych", "type": "wyklad",       "type_display": "W", "room_properties": "wykladowa",     "blocked": False, "periodic": True},
    {"name": "Algorytmy i struktury danych", "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium",  "blocked": False, "periodic": True},
    {"name": "Fizyka",                       "type": "wyklad",       "type_display": "W", "room_properties": "wykladowa",     "blocked": False, "periodic": True},
    {"name": "Fizyka",                       "type": "laboratorium", "type_display": "L", "room_properties": "laboratorium",  "blocked": False, "periodic": True},
    {"name": "Matematyka dyskretna",         "type": "wyklad",       "type_display": "W", "room_properties": "wykladowa",     "blocked": False, "periodic": True},
    {"name": "Matematyka dyskretna",         "type": "cwiczenia",    "type_display": "C", "room_properties": "cwiczeniowa",   "blocked": False, "periodic": True},
]


def _seed_subjects(db: Session) -> list[str]:
    """Returns list of subject names."""
    names: list[str] = []
    for s in SUBJECTS:
        exists = db.query(Subject).filter_by(name=s["name"], type=s["type"]).first()
        if not exists:
            db.add(Subject(**s))
        names.append(s["name"])
    db.commit()
    print(f"[mobile] Subjects seeded: {len(SUBJECTS)}")
    return list(dict.fromkeys(names))  # unique, ordered


# ---------------------------------------------------------------------------
# 3) Teachers & Students (user accounts + profiles)
# ---------------------------------------------------------------------------

TEACHERS = [
    {
        "first_name": "Jan", "last_name": "Kowalski", "album_number": "20001",
        "login": "jkowalski", "email": "jan.kowalski@uczelnia.pl",
        "department_abbr": "WI", "title": "dr hab.", "prop": "profesor",
    },
    {
        "first_name": "Anna", "last_name": "Nowak", "album_number": "20002",
        "login": "anowak", "email": "anna.nowak@uczelnia.pl",
        "department_abbr": "WI", "title": "dr", "prop": "adiunkt",
    },
    {
        "first_name": "Piotr", "last_name": "Wisniewski", "album_number": "20003",
        "login": "pwisniewski", "email": "piotr.wisniewski@uczelnia.pl",
        "department_abbr": "WI", "title": "dr", "prop": "adiunkt",
    },
    {
        "first_name": "Maria", "last_name": "Zalewska", "album_number": "20004",
        "login": "mzalewska", "email": "maria.zalewska@uczelnia.pl",
        "department_abbr": "WI", "title": "prof. dr hab.", "prop": "profesor",
    },
]

STUDENTS = [
    {
        "first_name": "Tomasz", "last_name": "Adamski", "album_number": "30001",
        "login": "tadamski", "email": "tomasz.adamski@student.uczelnia.pl",
        "department_abbr": "WI", "index_number": "123456", "group_code": "IS1", "semester": 1,
    },
    {
        "first_name": "Katarzyna", "last_name": "Bak", "album_number": "30002",
        "login": "kbak", "email": "katarzyna.bak@student.uczelnia.pl",
        "department_abbr": "WI", "index_number": "123457", "group_code": "IS1", "semester": 1,
    },
    {
        "first_name": "Michal", "last_name": "Celinski", "album_number": "30003",
        "login": "mcelinski", "email": "michal.celinski@student.uczelnia.pl",
        "department_abbr": "WI", "index_number": "123458", "group_code": "IS2", "semester": 3,
    },
    {
        "first_name": "Ewa", "last_name": "Dabrowska", "album_number": "30004",
        "login": "edabrowska", "email": "ewa.dabrowska@student.uczelnia.pl",
        "department_abbr": "WI", "index_number": "123459", "group_code": "IS2", "semester": 3,
    },
    {
        "first_name": "Adam", "last_name": "Mazur", "album_number": "30005",
        "login": "amazur", "email": "adam.mazur@student.uczelnia.pl",
        "department_abbr": "WI", "index_number": "123460", "group_code": "IS3", "semester": 5,
    },
]


def _seed_profiles(db: Session, group_codes: dict[str, int]) -> tuple[list[int], list[int]]:
    """
    Create teacher + student user accounts with roles, departments, and profiles.
    Returns (teacher_user_ids, student_user_ids).
    """
    lecturer_role = db.query(Role).filter(Role.name == "wykladowca").first()
    student_role = db.query(Role).filter(Role.name == "student").first()

    teacher_ids: list[int] = []
    student_ids: list[int] = []

    for t in TEACHERS:
        existing = db.query(User).filter(User.login == t["login"]).first()
        if existing:
            teacher_ids.append(existing.user_id)
            continue
        dept = db.query(Department).filter_by(abbreviation=t["department_abbr"]).first()
        user = User(
            first_name=t["first_name"], last_name=t["last_name"],
            album_number=t["album_number"], login=t["login"], email=t["email"],
            password_hash=DEFAULT_PASSWORD_HASH, must_change_password=True,
        )
        db.add(user)
        db.flush()
        if lecturer_role:
            add_role_to_user(db, user.user_id, lecturer_role.id)
        if dept:
            add_department_to_user(db, user.user_id, dept.id)
        db.add(Teacher(user_id=user.user_id, title=t["title"], prop=t["prop"]))
        teacher_ids.append(user.user_id)

    for s in STUDENTS:
        existing = db.query(User).filter(User.login == s["login"]).first()
        if existing:
            student_ids.append(existing.user_id)
            continue
        dept = db.query(Department).filter_by(abbreviation=s["department_abbr"]).first()
        user = User(
            first_name=s["first_name"], last_name=s["last_name"],
            album_number=s["album_number"], login=s["login"], email=s["email"],
            password_hash=DEFAULT_PASSWORD_HASH, must_change_password=True,
        )
        db.add(user)
        db.flush()
        if student_role:
            add_role_to_user(db, user.user_id, student_role.id)
        if dept:
            add_department_to_user(db, user.user_id, dept.id)
        db.add(Student(
            user_id=user.user_id,
            index_number=s["index_number"],
            group_id=group_codes.get(s["group_code"]),
            semester=s["semester"],
        ))
        student_ids.append(user.user_id)

    db.commit()
    print(f"[mobile] Profiles seeded: {len(teacher_ids)} teachers, {len(student_ids)} students")
    return teacher_ids, student_ids


# ---------------------------------------------------------------------------
# 4) Grades
# ---------------------------------------------------------------------------

def _seed_grades(db: Session, student_ids: list[int], lecturer_ids: list[int]) -> None:
    rng = random.Random(42)
    subjects = db.query(Subject).all()
    if len(subjects) < 3 or not lecturer_ids:
        print("[mobile] Grades skipped: not enough subjects or lecturers.")
        return

    grade_values = [3.0, 3.5, 4.0, 4.5, 5.0]
    created = 0

    for sid in student_ids:
        selected = rng.sample(subjects, min(3, len(subjects)))
        for order, subj in enumerate(selected, start=1):
            exists = db.query(GradeRecord).filter(
                GradeRecord.student_id == sid,
                GradeRecord.subject_name == subj.name,
                GradeRecord.sort_order == order,
            ).first()
            if exists:
                continue
            db.add(GradeRecord(
                student_id=sid,
                lecturer_id=rng.choice(lecturer_ids),
                semester=1,
                subject_name=subj.name,
                component_label=f"Zadanie {order}",
                component_info=subj.type_display or subj.type,
                grade_value=rng.choice(grade_values),
                is_final=(order == len(selected)),
                sort_order=order,
            ))
            created += 1

    db.commit()
    print(f"[mobile] Grades seeded: {created}")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def seed_mobile_data(db: Session) -> None:
    """Seed all tables required by the mobile app (groups, subjects, profiles, grades)."""
    group_codes = _seed_groups(db)
    _seed_subjects(db)
    teacher_ids, student_ids = _seed_profiles(db, group_codes)
    _seed_grades(db, student_ids, teacher_ids)
    print("[mobile] All mobile seed data applied.")
