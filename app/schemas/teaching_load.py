from typing import Optional

from pydantic import BaseModel, Field


class TeachingLoadAssignmentDto(BaseModel):
    id: int
    teacher_id: int
    teacher_title: Optional[str] = None
    teacher_first_name: Optional[str] = None
    teacher_last_name: Optional[str] = None
    subject_id: int
    subject_name: Optional[str] = None
    activity_id: int
    activity_name: Optional[str] = None
    semester_id: int
    semester_name: Optional[str] = None
    field_of_study_id: Optional[int] = None
    field_of_study_label: Optional[str] = None
    hours: int

    model_config = {"from_attributes": True}


class TeachingLoadCreatePayload(BaseModel):
    teacher_id: int
    subject_id: int
    activity_id: int
    semester_id: int
    field_of_study_id: Optional[int] = None
    hours: int = Field(ge=0)


class TeachingLoadPatchPayload(BaseModel):
    teacher_id: Optional[int] = None
    subject_id: Optional[int] = None
    activity_id: Optional[int] = None
    semester_id: Optional[int] = None
    field_of_study_id: Optional[int] = None
    hours: Optional[int] = Field(None, ge=0)


# Aliases for CRUD compatibility
TeachingLoadAssignmentCreate = TeachingLoadCreatePayload
TeachingLoadAssignmentPatch = TeachingLoadPatchPayload
TeachingLoadAssignmentUpdate = TeachingLoadCreatePayload


class TeachingLoadListResponse(BaseModel):
    items: list[TeachingLoadAssignmentDto]
