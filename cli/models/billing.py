from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

# Invoice

class TransactionType(Enum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"

class InvoiceFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    alias: str
    contract_address: str
    user_id: UUID4

    created_at: datetime
    updated_at: datetime


class InvoiceCreate(BaseModel):
    user_id: Optional[UUID4] = Field(..., description="The user ID")
    alias: Optional[str] = Field(None, description="The alias of the invoice")
    contract_address: str = Field(
        ..., description="The contract address associated with the invoice"
    )


class InvoiceUpdate(BaseModel):
    alias: Optional[str] = Field(None, description="The alias of the invoice")
    contract_address: Optional[str] = Field(
        None, description="The contract address associated with the invoice"
    )


# InvoiceTransaction


class InvoiceTransactionFullResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    amount: int
    type: TransactionType
    invoice_id: UUID4
    date: datetime

    created_at: datetime
    updated_at: datetime


class InvoiceTransactionsCreate(BaseModel):
    invoice_id: UUID4 = Field(..., description="The invoice ID")
    amount: int = Field(..., description="The amount of the transaction")
    type: TransactionType = Field(
        ..., description="The type of transaction (credit/debit)"
    )
    date: datetime = Field(..., description="The date of the transaction")


class InvoiceTransactionsUpdate(BaseModel):
    amount: Optional[int] = Field(None, description="The amount of the transaction")
    type: Optional[TransactionType] = Field(
        None, description="The type of transaction (credit/debit)"
    )
    date: Optional[datetime] = Field(None, description="The date of the transaction")


class InvoiceBalanceResponse(BaseModel):
    balance: int = Field(..., description="The balance of the invoice")
