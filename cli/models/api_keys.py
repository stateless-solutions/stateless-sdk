from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, UUID4


class APIKeyCreate(BaseModel):
    account_id: Optional[UUID4] = Field(..., description="The account ID")
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
