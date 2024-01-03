from datetime import datetime
from typing import Optional

from pydantic import Field

from .accounts import AccountCreate, AccountFullResponse


class ProviderFullResponse(AccountFullResponse):
    payment_address: str
    p_created_at: datetime
    p_updated_at: datetime


class ProviderCreate(AccountCreate):
    payment_address: Optional[str] = Field(None, description="Payment Address")
