from pydantic import UUID4, BaseModel, Field


class EntrypointCreate(BaseModel):
    url: str = Field(..., description="The URL of the entrypoint")
    offering_id: UUID4 = Field(
        ..., description="The ID of the offering for the entrypoint"
    )
    region_id: UUID4 = Field(..., description="The ID of the region for the entrypoint")


class EntrypointUpdate(BaseModel):
    url: str = Field(None, description="The updated URL of the entrypoint")
