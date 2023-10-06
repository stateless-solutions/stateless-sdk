from typing import Optional

from pydantic import UUID4, BaseModel, Field


class OfferingCreate(BaseModel):
    chain_id: int = Field(..., description="The ID of the chain for the offering")
    provider_id: Optional[UUID4] = Field(
        ..., description="The ID of the provider for the offering"
    )


class OfferingUpdate(BaseModel):
    chain_id: int = Field(
        None, description="The updated ID of the chain for the offering"
    )
    provider_id: UUID4 = Field(
        None, description="The updated ID of the provider for the offering"
    )
