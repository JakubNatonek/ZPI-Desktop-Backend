from pydantic import BaseModel, Field


class PartialGradeResponse(BaseModel):
    id: int
    label: str
    grade: str
    info: str


class SubjectGradeResponse(BaseModel):
    subject: str
    teacher: str
    final_grade: str
    partial_grades: list[PartialGradeResponse]


class SemesterGradesResponse(BaseModel):
    semester: int
    semester_label: str
    subjects: list[SubjectGradeResponse]


class StudentSummaryResponse(BaseModel):
    student_id: int
    student_name: str


class StudentGradesResponse(BaseModel):
    student_id: int
    student_name: str
    subjects: list[SubjectGradeResponse]


class LecturerSemesterGradesResponse(BaseModel):
    semester: int
    semester_label: str
    students: list[StudentGradesResponse]


class PartialGradeUpdateItem(BaseModel):
    label: str = Field(min_length=1)
    grade: str = Field(min_length=1)
    info: str = ""


class SubjectGradeUpdateRequest(BaseModel):
    student_id: int
    semester: int = Field(ge=1, le=20)
    subject: str = Field(min_length=1)
    final_grade: str = Field(min_length=1)
    partial_grades: list[PartialGradeUpdateItem] = Field(default_factory=list)


class SubjectGradeDeleteRequest(BaseModel):
    student_id: int
    semester: int = Field(ge=1, le=20)
    subject: str = Field(min_length=1)
