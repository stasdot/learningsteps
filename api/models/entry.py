from pydantic import BaseModel, Field, field_validator
from typing import Optional
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

    # TODO: Add field validation rules - DONE
    # TODO: Add custom validators - DONE for stripping whitespace and checking emptiness
    # TODO: Add schema versioning || skip for now
    # TODO: Add data sanitization methods || minimal implementation

class Entry(BaseModel):
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

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="timestamp when the entry was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="timestamp when the entry was last updated"
    )

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