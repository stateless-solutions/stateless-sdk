from pydantic import BaseModel, Field


class ChainCreate(BaseModel):
    chain_id: int = Field(..., description="The ID of the chain")
    name: str = Field(..., description="The name of the chain")


class ChainUpdate(BaseModel):
    name: str = Field(None, description="The updated name of the chain")
