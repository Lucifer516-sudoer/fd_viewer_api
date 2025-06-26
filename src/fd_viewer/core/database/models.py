from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class FixedDepositModel(SQLModel):
    """
    A base model for fixed deposits, capturing all necessary financial and temporal fields.
    Intended to be extended by a database-mapped model (see `FixedDeposit`).
    """

    holder_name: str = Field(description="Name of the fixed deposit holder")
    bank_name: str = Field(description="Bank where the fixed deposit is held")

    deposited_date: date = Field(
        default_factory=date.today,
        description="Date when the principal amount was deposited",
    )
    maturity_date: date = Field(
        default_factory=date.today, description="Date when the fixed deposit matures"
    )

    principal_amount: Decimal = Field(
        default=Decimal("0.0"), description="Principal amount deposited (in currency)"
    )
    maturity_amount: Decimal = Field(
        default=Decimal("0.0"),
        description="Total maturity amount receivable at end of the term",
    )
    interest_rate: Decimal = Field(
        default=Decimal("0.0"), description="Annual interest rate in percentage"
    )

    period: Optional[int] = Field(
        default=None,
        description="Deposit term in days (if provided, will auto-calculate maturity_date)",
    )

    @property
    def time_period(self) -> timedelta:
        """
        Returns the duration between deposited and maturity dates as a timedelta.
        This represents the actual term of the fixed deposit.
        """
        return self.maturity_date - self.deposited_date


class FixedDeposit(FixedDepositModel, table=True):
    """
    The SQL table model for a Fixed Deposit. Adds a primary key 'id' to make the model persistent.
    """

    id: Optional[int] = Field(
        default=None, primary_key=True, description="Primary key ID"
    )
