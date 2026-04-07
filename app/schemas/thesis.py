from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ThesisStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LecturerResponse(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str


class ThesisProposalCreateRequest(BaseModel):
    lecturer_id: int
    topic: str = Field(min_length=10, max_length=255)
    justification: str = Field(min_length=20)
    student_average_grade: float = Field(default=0.0, ge=0.0, le=5.0)


class ThesisProposalStatusUpdateRequest(BaseModel):
    status: ThesisStatus


class ThesisProposalResponse(BaseModel):
    id: int
    student_id: int
    student_name: str
    student_email: str
    student_average_grade: float
    lecturer_id: int
    lecturer_name: str
    topic: str
    justification: str
    status: ThesisStatus
    submitted_at: datetime
    reviewed_at: datetime | None = None


class ThesisScheduleAvailabilityResponse(BaseModel):
    tab_visible_from: datetime | None = None
    tab_visible_to: datetime | None = None
    topic_submission_from: datetime | None = None
    topic_submission_to: datetime | None = None
    proposal_selection_from: datetime | None = None
    proposal_selection_deadline: datetime | None = None
    can_view_tab: bool
    can_submit_topics: bool
    can_select_proposals: bool
