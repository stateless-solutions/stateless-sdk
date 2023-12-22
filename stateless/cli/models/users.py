from datetime import datetime

from pydantic import UUID4, Field

from .accounts import AccountCreate, AccountFullResponse


class UserFullResponse(AccountFullResponse):
    u_created_at: datetime
    u_updated_at: datetime


class UserCreate(AccountCreate):
    id: UUID4 | None = Field(
        None, description="The account id associated with the user"
    )
