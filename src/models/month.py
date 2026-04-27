from pydantic import Field

from src.models.common import YNABBaseModel
from src.models.category import Category

MONTH_DEFAULT_EXCLUDE: set[str] = {"deleted"}


class MonthSummary(YNABBaseModel):
    month: str = Field()
    note: str | None = Field(default=None)
    income: int = Field(default=0)
    budgeted: int = Field(default=0)
    activity: int = Field(default=0)
    to_be_budgeted: int = Field(default=0)
    age_of_money: int | None = Field(default=None)
    deleted: bool = Field(default=False)


class MonthDetail(YNABBaseModel):
    month: str = Field()
    note: str | None = Field(default=None)
    income: int = Field(default=0)
    budgeted: int = Field(default=0)
    activity: int = Field(default=0)
    to_be_budgeted: int = Field(default=0)
    age_of_money: int | None = Field(default=None)
    deleted: bool = Field(default=False)
    categories: list[Category] = Field(default=[])
