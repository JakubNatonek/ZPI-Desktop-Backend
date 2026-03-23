from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ThesisStatus = Literal["PENDING", "APPROVED", "REJECTED"]


class ThesisLecturerItem(BaseModel):
    id: int
    firstName: str
    lastName: str
    email: str


class SubmitThesisProposalPayload(BaseModel):
    lecturerId: int
    topic: str = Field(min_length=10)
    justification: str = Field(min_length=20)
    studentAverageGrade: float = 0.0


class ThesisProposalResponse(BaseModel):
    id: int
    studentName: str
    studentEmail: str
    studentAverageGrade: float
    lecturerId: int
    lecturerName: str
    topic: str
    justification: str
    status: ThesisStatus
    submittedAt: datetime


class UpdateThesisProposalStatusPayload(BaseModel):
    isApproved: bool
