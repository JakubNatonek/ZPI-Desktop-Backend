from pydantic import BaseModel, Field


class TeachingLoadAssignmentBase(BaseModel):
    teacher_id: int = Field(ge=1)
    subject_id: int = Field(ge=1)
    activity_id: int = Field(ge=1)
    semester_id: int = Field(ge=1)
    hours: int = Field(ge=1)
    group_id: int = Field(ge=1)


class TeachingLoadAssignmentCreate(TeachingLoadAssignmentBase):
    pass


class TeachingLoadAssignmentUpdate(TeachingLoadAssignmentBase):
    pass


class TeachingLoadAssignmentPatch(BaseModel):
    teacher_id: int | None = Field(default=None, ge=1)
    subject_id: int | None = Field(default=None, ge=1)
    activity_id: int | None = Field(default=None, ge=1)
    semester_id: int | None = Field(default=None, ge=1)
    hours: int | None = Field(default=None, ge=1)
    group_id: int | None = Field(default=None, ge=1)


class TeachingLoadAssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    teacher_title: str | None = None
    teacher_first_name: str | None = None
    teacher_last_name: str | None = None
    subject_id: int
    subject_name: str | None = None
    activity_id: int
    activity_name: str | None = None
    semester_id: int
    semester_name: str | None = None
    group_id: int | None = None
    group_label: str | None = None
    hours: int


class TeachingLoadAssignmentListResponse(BaseModel):
    items: list[TeachingLoadAssignmentResponse]
