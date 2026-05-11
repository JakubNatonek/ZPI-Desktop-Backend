from pydantic import BaseModel, Field


class SubjectPreferenceCreate(BaseModel):
    subject_id: int = Field(ge=1)
    user_id: int | None = Field(None, ge=1)  # Optional for admin operations


class SubjectPreferenceResponse(BaseModel):
    id: int
    user_id: int
    subject_id: int
    subject_name: str | None = None

    class Config:
        from_attributes = True
