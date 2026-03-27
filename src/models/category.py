from pydantic import Field

from src.models.common import YNABBaseModel

# Fields excluded from the standard category list display
CATEGORY_LIST_EXCLUDE: set[str] = set()

# Fields included in the category detail display (get_category_for_month)
# NOTE: Empty set means include all fields (None is passed to model_dump)
CATEGORY_DETAIL_INCLUDE: set[str] = set()


class Category(YNABBaseModel):
    id: str = Field()
    category_group_id: str = Field()
    category_group_name: str | None = Field(default=None)
    name: str = Field()
    hidden: bool = Field(default=False)
    original_category_group_id: str | None = Field(default=None)
    note: str | None = Field(default=None)
    budgeted: int = Field(default=0)
    activity: int = Field(default=0)
    balance: int = Field(default=0)
    goal_type: str | None = Field(default=None)
    goal_needs_whole_amount: bool | None = Field(default=None)
    goal_day: int | None = Field(default=None)
    goal_cadence: int | None = Field(default=None)
    goal_cadence_frequency: int | None = Field(default=None)
    goal_creation_month: str | None = Field(default=None)
    goal_target: int | None = Field(default=None)
    goal_target_month: str | None = Field(default=None)
    goal_target_date: str | None = Field(default=None)
    goal_percentage_complete: int | None = Field(default=None)
    goal_months_to_budget: int | None = Field(default=None)
    goal_under_funded: int | None = Field(default=None)
    goal_overall_funded: int | None = Field(default=None)
    goal_overall_left: int | None = Field(default=None)
    goal_snoozed_at: str | None = Field(default=None)
    deleted: bool = Field(default=False)


class CategoryGroup(YNABBaseModel):
    id: str = Field()
    name: str = Field()
    hidden: bool = Field(default=False)
    deleted: bool = Field(default=False)
    categories: list[Category] = Field(default=[])
