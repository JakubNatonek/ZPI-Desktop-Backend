from pydantic import BaseModel, Field


class PartialGradeResponse(BaseModel):
    id: int
    label: str
    grade: str
    weight: float
    info: str


class SubjectGradeResponse(BaseModel):
    subject: str
    teacher: str
    final_grade: str
    subject_weight: float
    weighted_average: str
    partial_grades: list[PartialGradeResponse]


class SemesterGradesResponse(BaseModel):
    semester: int
    semester_label: str
    semester_type: str
    semester_average: str
    subjects: list[SubjectGradeResponse]


class StudentSummaryResponse(BaseModel):
    student_id: int
    student_name: str


class StudentGradesResponse(BaseModel):
    student_id: int
    student_name: str
    album_number: str
    subjects: list[SubjectGradeResponse]


class LecturerSemesterGradesResponse(BaseModel):
    semester: int
    semester_label: str
    semester_type: str
    is_current: bool = False
    students: list[StudentGradesResponse]


class SemesterOptionResponse(BaseModel):
    semester: int
    semester_label: str
    semester_type: str
    is_current: bool


class PartialGradeUpdateItem(BaseModel):
    label: str = Field(min_length=1)
    grade: str = Field(min_length=1)
    weight: float = Field(default=1.0, ge=0.0)
    info: str = ""


class SubjectGradeUpdateRequest(BaseModel):
    student_id: int
    semester: int = Field(ge=1, le=20)
    subject: str = Field(min_length=1)
    final_grade: str = Field(min_length=1)
    subject_weight: float = Field(default=1.0, ge=0.0)
    partial_grades: list[PartialGradeUpdateItem] = Field(default_factory=list)


class AdminSubjectGradeUpdateRequest(BaseModel):
    student_id: int
    lecturer_id: int | None = None
    semester: int = Field(ge=1, le=20)
    subject: str = Field(min_length=1)
    final_grade: str = Field(min_length=1)
    subject_weight: float = Field(default=1.0, ge=0.0)
    partial_grades: list[PartialGradeUpdateItem] = Field(default_factory=list)
