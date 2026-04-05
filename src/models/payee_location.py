from pydantic import Field

from src.models.common import YNABBaseModel


class PayeeLocation(YNABBaseModel):
    id: str = Field()
    payee_id: str = Field()
    latitude: str = Field()
    longitude: str = Field()
    deleted: bool = Field(default=False)
