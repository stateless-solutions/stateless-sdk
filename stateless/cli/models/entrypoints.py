from datetime import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

from .regions import RegionFullResponse


class EntrypointNoURLResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    offering_id: UUID4
    region_id: UUID4
    
    region: Optional[RegionFullResponse]

    created_at: datetime
    updated_at: datetime


class EntrypointFullResponse(EntrypointNoURLResponse):
    model_config = ConfigDict(from_attributes=True)

    url: str


class EntrypointCreate(BaseModel):
    url: str = Field(..., description="The URL of the entrypoint")
    offering_id: UUID4 = Field(
        ..., description="The ID of the offering for the entrypoint"
    )
    region_id: UUID4 = Field(..., description="The ID of the region for the entrypoint")


class EntrypointUpdate(BaseModel):
    url: str = Field(None, description="The updated URL of the entrypoint")
