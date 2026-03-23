from datetime import datetime
from typing import Literal

from pydantic import BaseModel


RequestThesisFieldType = Literal["text", "textarea", "email", "number", "date", "select"]


class RequestThesisOption(BaseModel):
    label: str
    value: str


class RequestThesisField(BaseModel):
    key: str
    label: str
    type: RequestThesisFieldType
    required: bool
    placeholder: str | None = None
    options: list[RequestThesisOption] | None = None


class RequestThesisDefinition(BaseModel):
    id: int
    name: str
    description: str
    templateFileName: str
    fields: list[RequestThesisField]


class SubmitRequestThesisPayload(BaseModel):
    documentTypeId: int
    values: dict[str, str | int | float | bool]
    teacherUserId: int | None = None


class SubmitRequestThesisResponse(BaseModel):
    id: int
    status: Literal["SENT", "QUEUED"]


class RequestThesisSubmissionItem(BaseModel):
    id: int
    documentTypeId: int
    documentName: str
    submittedAt: datetime
    isApproved: bool
    values: dict[str, str | int | float | bool]
    studentUserId: int
    teacherUserId: int | None = None


class RequestThesisSubmissionsResponse(BaseModel):
    viewerRole: Literal["teacher", "student"]
    items: list[RequestThesisSubmissionItem]


class UpdateThesisStatusPayload(BaseModel):
    isApproved: bool
