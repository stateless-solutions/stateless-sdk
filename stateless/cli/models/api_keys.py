from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field


class APIKeyFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    prefix: Optional[str]
    account_id: UUID4
    expires_at: Optional[datetime]
    key: Optional[str] = Field(None)

    created_at: datetime
    updated_at: datetime


class APIKeyCreate(BaseModel):
    account_id: Optional[UUID4] = Field(None, description="The account ID")
    name: str = Field(..., description="The name of the API key")
    prefix: Optional[str] = Field(None, description="The prefix of the API key")
    expires_at: Optional[datetime] = Field(
        None, description="The expiration datetime of the API key"
    )


class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The name of the API key")
    prefix: Optional[str] = Field(None, description="The prefix of the API key")
    expires_at: Optional[datetime] = Field(
        None, description="The expiration datetime of the API key"
    )
