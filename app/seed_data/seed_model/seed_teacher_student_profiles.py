from sqlalchemy.orm import Session

from app.auth.password_utils import hash_password
from app.models.model_department import Department
from app.models.model_role import Role
from app.models.model_student import Student
from app.models.model_teacher import Teacher
from app.models.model_user import User


def seed_teacher_student_profiles(db: Session) -> None:
	"""Seed teachers and students together with their user accounts."""
	default_password = "test123"
	default_password_hash = hash_password(default_password)

	teachers_data = [
		{
			"user": {"first_name": "Jan", "last_name": "Kowalski", "album_number": "20001", "login": "jkowalski", "email": "jan.kowalski@uczelnia.pl", "role_name": "wykladowca", "department_name": "Informatyka"},
			"teacher": {"title": "dr hab.", "prop": "profesor"},
		},
		{
			"user": {"first_name": "Anna", "last_name": "Nowak", "album_number": "20002", "login": "anowak", "email": "anna.nowak@uczelnia.pl", "role_name": "wykladowca", "department_name": "Informatyka"},
			"teacher": {"title": "dr", "prop": "adiunkt"},
		},
		{
			"user": {"first_name": "Piotr", "last_name": "Wisniewski", "album_number": "20003", "login": "pwisniewski", "email": "piotr.wisniewski@uczelnia.pl", "role_name": "wykladowca", "department_name": "Fizyka"},
			"teacher": {"title": "dr", "prop": "adiunkt"},
		},
		{
			"user": {"first_name": "Maria", "last_name": "Zalewska", "album_number": "20004", "login": "mzalewska", "email": "maria.zalewska@uczelnia.pl", "role_name": "wykladowca", "department_name": "Matematyka"},
			"teacher": {"title": "prof. dr hab.", "prop": "profesor"},
		},
	]

	students_data = [
		{
			"user": {"first_name": "Tomasz", "last_name": "Adamski", "album_number": "30001", "login": "tadamski", "email": "tomasz.adamski@student.uczelnia.pl", "role_name": "student", "department_name": "Informatyka"},
			"student": {"index_number": "123456", "group_id": 1, "semester": 1},
		},
		{
			"user": {"first_name": "Katarzyna", "last_name": "Bak", "album_number": "30002", "login": "kbak", "email": "katarzyna.bak@student.uczelnia.pl", "role_name": "student", "department_name": "Informatyka"},
			"student": {"index_number": "123457", "group_id": 1, "semester": 1},
		},
		{
			"user": {"first_name": "Michal", "last_name": "Celinski", "album_number": "30003", "login": "mcelinski", "email": "michal.celinski@student.uczelnia.pl", "role_name": "student", "department_name": "Informatyka"},
			"student": {"index_number": "123458", "group_id": 2, "semester": 3},
		},
		{
			"user": {"first_name": "Ewa", "last_name": "Dabrowska", "album_number": "30004", "login": "edabrowska", "email": "ewa.dabrowska@student.uczelnia.pl", "role_name": "student", "department_name": "Informatyka"},
			"student": {"index_number": "123459", "group_id": 2, "semester": 3},
		},
		{
			"user": {"first_name": "Adam", "last_name": "Mazur", "album_number": "30005", "login": "amazur", "email": "adam.mazur@student.uczelnia.pl", "role_name": "student", "department_name": "Informatyka"},
			"student": {"index_number": "123460", "group_id": 3, "semester": 5},
		},
	]

	created_count = 0
	for profile_data in [*teachers_data, *students_data]:
		user_payload = profile_data["user"]
		role = db.query(Role).filter(Role.name == user_payload["role_name"]).first()
		department = db.query(Department).filter(Department.name == user_payload["department_name"]).first()

		if role is None or department is None:
			print(
				"User profile seed skipped for "
				f"{user_payload['login']}: missing role={user_payload['role_name']} "
				f"or department={user_payload['department_name']}."
			)
			continue

		existing = db.query(User).filter(User.login == user_payload["login"]).first()
		if existing is not None:
			continue

		user = User(
			first_name=user_payload["first_name"],
			last_name=user_payload["last_name"],
			album_number=user_payload["album_number"],
			login=user_payload["login"],
			email=user_payload["email"],
			public_key=None,
			password_hash=default_password_hash,
			plain_password=default_password,
			must_change_password=False,
			role_id=role.id,
			department_id=department.id,
		)
		db.add(user)
		db.flush()

		if "teacher" in profile_data:
			db.add(Teacher(user_id=user.user_id, **profile_data["teacher"]))
		else:
			db.add(Student(user_id=user.user_id, **profile_data["student"]))

		created_count += 1

	if created_count == 0:
		print("User profiles seeded: no new teacher or student accounts added.")
		return

	db.commit()
	print(f"User profiles seeded: added {created_count} account(s).")