from typing import Optional

from pydantic import BaseModel, Field


class AccountRegister(BaseModel):
    oauth_id: str = Field(..., description="The OAuth2 Unique Identifier")
    status: str = Field("active", description="The status of the account")
    email: Optional[str] | None = Field(
        None, description="The email address of the account"
    )
    name: Optional[str] | None = Field(
        None, description="The name associated with the account"
    )
    username: str = Field(..., description="The username associated with the account")
