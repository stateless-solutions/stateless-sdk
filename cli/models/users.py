from pydantic import UUID4, Field

from cli.models.accounts import AccountRegister


class UserCreate(AccountRegister):
    id: UUID4 | None = Field(
        None, description="The account id associated with the user"
    )
