from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import uuid4


class EntryCreate(BaseModel):
    """Model for creating a new journal entry (user input)."""

    work: str = Field(
        max_length=256,
        description="What did you work on today?",
        json_schema_extra={"example": "Studied FastAPI and built my first API endpoints"}
    )
    struggle: str = Field(
        max_length=256,
        description="What's one thing you struggled with today?",
        json_schema_extra={"example": "Understanding async/await syntax and when to use it"}
    )
    intention: str = Field(
        max_length=256,
        description="What will you study/work on tomorrow?",
        json_schema_extra={"example": "Practice PostgreSQL queries and database design"}
    )

    # TODO: Add field validation rules - DONE (Field max_length)
    # TODO: Add custom validators - DONE (strip whitespace + empty check)
    # TODO: Add schema versioning - SKIPPED (out of scope for now)
    # TODO: Add data sanitization methods - DONE (basic whitespace normalization)

    @field_validator("work", "struggle", "intention")
    @classmethod
    def strip_and_validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must not be empty or whitespace")
        return value


class EntryUpdate(BaseModel):
    """Model for updating an existing journal entry (PATCH)."""

    # optional fields for PATCH
    work: str | None = Field(
        default=None,
        max_length=256,
        description="Updated work description"
    )
    struggle: str | None = Field(
        default=None,
        max_length=256,
        description="Updated struggle description"
    )
    intention: str | None = Field(
        default=None,
        max_length=256,
        description="Updated intention description"
    )

    # TODO: Reuse EntryCreate validation rules — DONE (shared validator logic)

    @field_validator("work", "struggle", "intention")
    @classmethod
    def strip_and_validate_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("field must not be empty or whitespace")
        return value


class Entry(BaseModel):
    """Full journal entry model (stored and returned)."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="unique identifier for the entry (uuid)"
    )

    work: str = Field(
        ...,
        max_length=256,
        description="what did you work on today?"
    )
    struggle: str = Field(
        ...,
        max_length=256,
        description="what’s one thing you struggled with today?"
    )
    intention: str = Field(
        ...,
        max_length=256,
        description="what will you study/work on tomorrow?"
    )

    # TODO: Add custom validators — DONE (strip whitespace + empty check)

    @field_validator("work", "struggle", "intention")
    @classmethod
    def strip_and_validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("field must not be empty or whitespace")
        return value

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
