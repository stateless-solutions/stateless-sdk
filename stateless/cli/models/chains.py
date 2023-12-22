from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field


class ChainFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    chain_id: int

    created_at: datetime
    updated_at: datetime


class ChainCreate(BaseModel):
    chain_id: int = Field(..., description="The ID of the chain")
    name: str = Field(..., description="The name of the chain")


class ChainUpdate(BaseModel):
    name: str = Field(None, description="The updated name of the chain")
