from pydantic import BaseModel, Field


class RegionCreate(BaseModel):
    name: str = Field(..., description="The name of the region")


class RegionUpdate(BaseModel):
    name: str = Field(None, description="The updated name of the region")
