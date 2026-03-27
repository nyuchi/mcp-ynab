from pydantic import Field

from src.models.common import YNABBaseModel


class User(YNABBaseModel):
    id: str = Field()
