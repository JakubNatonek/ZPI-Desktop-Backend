from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.model_user import User
from app.models.model_subject import Subject
from app.models.model_activity import Activity
from app.models.model_semestr import Semestr
from app.models.model_group import Group
from app.models.model_teaching_load_assignment import TeachingLoadAssignment
from app.cruds.crud_roles_for_user import get_roles_for_user


def seed_teaching_loads(db: Session) -> None:
	"""Seed teaching load assignments with sample data."""
	
	# Get all lecturers (wykladowca role)
	users = db.query(User).all()
	lecturers = []
	for user in users:
		roles = {str(role.name).strip().lower() for role in get_roles_for_user(db, user.user_id) if role.name}
		if "wykladowca" in roles or "lecturer" in roles:
			lecturers.append(user)
	
	if not lecturers:
		print("No lecturers found. Skipping teaching load seeding.")
		return
	
	# Get sample data
	subjects = db.query(Subject).all()[:4]
	activities = db.query(Activity).all()
	semester = db.query(Semestr).first()
	groups = db.query(Group).all()
	
	if not subjects or not activities or not semester or not groups:
		print("Missing required data (subjects, activities, semester, or groups). Skipping teaching load seeding.")
		return
	
	# Create sample assignments
	sample_assignments = []
	for idx, lecturer in enumerate(lecturers[:3]):  # First 3 lecturers
		for subject_idx, subject in enumerate(subjects):
			activity = activities[subject_idx % len(activities)]
			group = groups[subject_idx % len(groups)]
			hours = 15 + (idx * 5) + (subject_idx * 10)
			
			sample_assignments.append({
				"teacher_id": lecturer.user_id,
				"subject_id": subject.id,
				"activity_id": activity.id,
				"semester_id": semester.id,
				"group_id": group.id,
				"hours": hours,
			})
	
	created_count = 0
	for assignment_data in sample_assignments:
		exists = db.query(TeachingLoadAssignment).filter(
			and_(
				TeachingLoadAssignment.teacher_id == assignment_data["teacher_id"],
				TeachingLoadAssignment.subject_id == assignment_data["subject_id"],
				TeachingLoadAssignment.activity_id == assignment_data["activity_id"],
				TeachingLoadAssignment.semester_id == assignment_data["semester_id"],
				TeachingLoadAssignment.group_id == assignment_data["group_id"],
			)
		).first()
		
		if not exists:
			db.add(TeachingLoadAssignment(**assignment_data))
			created_count += 1
	
	db.commit()
	print(f"Teaching loads seeded. Added: {created_count}")
