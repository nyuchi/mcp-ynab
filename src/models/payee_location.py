from pydantic import Field

from src.models.common import YNABBaseModel

PAYEE_LOCATION_DEFAULT_EXCLUDE: set[str] = {"deleted"}


class PayeeLocation(YNABBaseModel):
    id: str = Field()
    payee_id: str = Field()
    latitude: str = Field()
    longitude: str = Field()
    deleted: bool = Field(default=False)
