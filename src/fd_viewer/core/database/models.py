from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel


class FixedDepositModel(SQLModel):
    holder_name: str
    bank_name: str
    deposited_date: date = Field(
        default_factory=date.today, description="The principal amount deposited"
    )
    maturity_date: date = Field(default_factory=date.today)
    principal_amount: Decimal = Field(default=Decimal("0.0"))
    maturity_amount: Decimal = Field(default=Decimal("0.0"))
    interest_rate: Decimal = Field(default=Decimal("0.0"))
    period: Optional[int] = Field(default=None)  # in days

    @property
    def time_period(self) -> timedelta:
        """Returns the difference in the maturity and deposited date in terms of timedelta object"""
        return self.maturity_date - self.deposited_date


class FixedDeposit(FixedDepositModel, table=True): ...
