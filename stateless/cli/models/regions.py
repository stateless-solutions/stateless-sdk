from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field


class RegionFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    created_at: datetime
    updated_at: datetime


class RegionCreate(BaseModel):
    name: str = Field(..., description="The name of the region")


class RegionUpdate(BaseModel):
    name: str = Field(None, description="The updated name of the region")
