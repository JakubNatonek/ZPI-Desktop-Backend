from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.thesis_datetime import THESIS_DATETIME_FORMAT, format_datetime_minute, normalize_to_utc_minute


class AdminThesisStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ThesisPrintListItem(BaseModel):
    own_topic: bool
    student_name: str
    topic: str
    promotor_name: str


class AdminThesisProposalResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda value: format_datetime_minute(value)})

    id: int
    student_id: int
    student_name: str
    student_email: str
    student_index: str | None = None
    student_group: str | None = None
    student_average_grade: float
    lecturer_id: int
    lecturer_name: str
    lecturer_email: str
    topic: str
    justification: str
    status: AdminThesisStatus
    submitted_at: datetime
    reviewed_at: datetime | None = None


class AdminThesisStatusUpdate(BaseModel):
    status: AdminThesisStatus


class AdminThesisTopicUpdate(BaseModel):
    topic: str = Field(min_length=5, max_length=255)


class AdminThesisStats(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int


class AdminThesisSettingsUpdate(BaseModel):
    tab_visible_from: datetime | None = None
    tab_visible_to: datetime | None = None
    topic_submission_from: datetime | None = None
    topic_submission_to: datetime | None = None
    proposal_selection_from: datetime | None = None
    proposal_selection_deadline: datetime | None = None
    max_approved_proposals: int | None = Field(default=None, ge=1)

    @field_validator(
        "tab_visible_from",
        "tab_visible_to",
        "topic_submission_from",
        "topic_submission_to",
        "proposal_selection_from",
        "proposal_selection_deadline",
        mode="before",
    )
    @classmethod
    def parse_minute_datetime(cls, value: datetime | str | None) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return normalize_to_utc_minute(value)
        if isinstance(value, str):
            try:
                parsed = datetime.strptime(value.strip(), THESIS_DATETIME_FORMAT)
            except ValueError as exc:
                raise ValueError("Datetime must match format YYYY-MM-DD HH:MM") from exc
            return normalize_to_utc_minute(parsed)
        return value

    @model_validator(mode="after")
    def validate_ranges(self) -> "AdminThesisSettingsUpdate":
        if (
            self.tab_visible_from is not None
            and self.tab_visible_to is not None
            and self.tab_visible_from > self.tab_visible_to
        ):
            raise ValueError("Tab visibility start date must be earlier than end date")

        if (
            self.topic_submission_from is not None
            and self.topic_submission_to is not None
            and self.topic_submission_from > self.topic_submission_to
        ):
            raise ValueError("Topic submission start date must be earlier than end date")

        if (
            self.proposal_selection_from is not None
            and self.proposal_selection_deadline is not None
            and self.proposal_selection_from > self.proposal_selection_deadline
        ):
            raise ValueError("Proposal selection start date must be earlier than end date")

        return self


class AdminThesisSettingsResponse(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda value: format_datetime_minute(value)})

    tab_visible_from: datetime | None = None
    tab_visible_to: datetime | None = None
    topic_submission_from: datetime | None = None
    topic_submission_to: datetime | None = None
    proposal_selection_from: datetime | None = None
    proposal_selection_deadline: datetime | None = None
    max_approved_proposals: int
    tab_visible_now: bool
    topic_submission_open: bool
    proposal_selection_open: bool
    updated_at: datetime
