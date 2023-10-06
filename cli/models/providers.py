from typing import Optional

from pydantic import Field

from cli.models.accounts import AccountRegister


class ProviderCreate(AccountRegister):
    payment_address: Optional[str] = Field(None, description="Payment Address")
