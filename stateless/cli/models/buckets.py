from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

from .billing import InvoiceFullResponse
from .chains import ChainFullResponse
from .offerings import OfferingFullResponse


class BucketFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    user_id: UUID4
    chain_id: int
    invoice_id: Optional[UUID4]

    created_at: datetime
    updated_at: datetime

    # Relationships
    chain: Optional[ChainFullResponse]
    invoice: Optional[InvoiceFullResponse]
    offerings: Optional[List[OfferingFullResponse]]


class BucketCreate(BaseModel):
    user_id: Optional[str] = Field(
        None, description="The user ID, can only be set by admins"
    )
    name: str = Field(..., description="The name of the bucket")
    chain_id: int = Field(..., description="The ID of the associated chain")
    offerings: Optional[List[str]] = Field(
        description="A list of offerings UUIDs to associate with the bucket",
        default_factory=list,
    )
    invoice_id: Optional[str] = Field(
        None, description="The invoice to associate with the bucket"
    )


class BucketUpdate(BaseModel):
    name: Optional[str] = Field(None, description="The name of the bucket")
    offerings: Optional[List[str]] = Field(
        None, description="A list of offerings UUIDs to associate with the bucket"
    )
    invoice_id: Optional[str] = Field(
        None, description="The invoice to associate with the bucket"
    )
