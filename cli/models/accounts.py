from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field


class AccountFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: Optional[str]
    username: str
    status: str
    email: Optional[str]

    role: str
    oauth_id: str
    account_type: str

    created_at: datetime
    updated_at: datetime


class AccountCreate(BaseModel):
    oauth_id: str = Field(..., description="The OAuth2 Unique Identifier")
    status: str = Field("active", description="The status of the account")
    email: Optional[str] | None = Field(
        None, description="The email address of the account"
    )
    name: Optional[str] | None = Field(
        None, description="The name associated with the account"
    )
    username: str = Field(..., description="The username associated with the account")
