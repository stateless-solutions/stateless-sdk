from typing import List, Optional

from pydantic import BaseModel, Field


class BucketCreate(BaseModel):
    user_id: Optional[str] = Field(
        ..., description="The user ID, can only be set by admins"
    )
    name: str = Field(..., description="The name of the bucket")
    chain_id: int = Field(..., description="The ID of the associated chain")
    offerings: Optional[List[str]] = Field(
        description="A list of offerings UUIDs to associate with the bucket",
        default_factory=list,
    )


class BucketUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The name of the bucket")
    offerings: Optional[List[str]] = Field(
        None, description="A list of offerings UUIDs to associate with the bucket"
    )
