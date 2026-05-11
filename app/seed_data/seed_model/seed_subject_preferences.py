from sqlalchemy.orm import Session

from app.models.model_user import User
from app.models.model_subject import Subject
from app.cruds.crud_roles_for_user import get_roles_for_user
from app.cruds.crud_subject_preferences import add_preference
from fastapi import HTTPException


def seed_subject_preferences(db: Session) -> None:
	"""Seed subject preferences for lecturers.
	
	Assigns 2-3 subjects to each lecturer (wykladowca role).
	"""
	
	# Get all lecturers (wykladowca role)
	users = db.query(User).all()
	lecturers = []
	for user in users:
		roles = {str(role.name).strip().lower() for role in get_roles_for_user(db, user.user_id) if role.name}
		if "wykladowca" in roles or "lecturer" in roles:
			lecturers.append(user)
	
	if not lecturers:
		print("No lecturers found. Skipping subject preferences seeding.")
		return
	
	# Get available subjects
	subjects = db.query(Subject).all()
	
	if not subjects:
		print("No subjects found. Skipping subject preferences seeding.")
		return
	
	# Assign 2-3 subjects to each lecturer
	created_count = 0
	for idx, lecturer in enumerate(lecturers):
		# Assign 2-3 subjects per lecturer (vary count)
		num_subjects = 2 if idx % 2 == 0 else 3
		selected_subjects = subjects[idx::len(lecturers)][:num_subjects]
		
		for subject in selected_subjects:
			try:
				add_preference(db, lecturer.user_id, subject.id)
				created_count += 1
			except HTTPException as e:
				# Preference already exists or validation error
				if e.status_code == 400:
					# Already exists, skip
					pass
				else:
					print(f"Error adding preference for lecturer {lecturer.user_id}, subject {subject.id}: {e.detail}")
			except Exception as e:
				print(f"Unexpected error adding preference for lecturer {lecturer.user_id}, subject {subject.id}: {e}")
	
	print(f"Subject preferences seeded. Created {created_count} preferences.")
