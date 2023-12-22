from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field


class OfferingFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    chain_id: Optional[int]
    provider_id: UUID4

    created_at: datetime
    updated_at: datetime


class OfferingCreate(BaseModel):
    chain_id: int = Field(..., description="The ID of the chain for the offering")
    provider_id: Optional[UUID4] = Field(
        None, description="The ID of the provider for the offering"
    )


class OfferingUpdate(BaseModel):
    chain_id: int = Field(
        None, description="The updated ID of the chain for the offering"
    )
    provider_id: UUID4 = Field(
        None, description="The updated ID of the provider for the offering"
    )
