from pydantic import Field

from src.models.common import YNABBaseModel

TRANSACTION_DISPLAY_EXCLUDE: set[str] = set()


class Subtransaction(YNABBaseModel):
    id: str = Field()
    transaction_id: str = Field()
    amount: int = Field(default=0)
    memo: str | None = Field(default=None)
    payee_id: str | None = Field(default=None)
    payee_name: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    category_name: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None)
    transfer_transaction_id: str | None = Field(default=None)
    deleted: bool = Field(default=False)


class Transaction(YNABBaseModel):
    id: str = Field()
    date: str = Field()
    amount: int = Field(default=0)
    memo: str | None = Field(default=None)
    cleared: str = Field(default="uncleared")
    approved: bool = Field(default=False)
    flag_color: str | None = Field(default=None)
    flag_name: str | None = Field(default=None)
    account_id: str | None = Field(default=None)
    account_name: str | None = Field(default=None)
    payee_id: str | None = Field(default=None)
    payee_name: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    category_name: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None)
    transfer_transaction_id: str | None = Field(default=None)
    matched_transaction_id: str | None = Field(default=None)
    import_id: str | None = Field(default=None)
    import_payee_name: str | None = Field(default=None)
    import_payee_name_original: str | None = Field(default=None)
    debt_transaction_type: str | None = Field(default=None)
    subtransactions: list[Subtransaction] = Field(default=[])
    deleted: bool = Field(default=False)


class HybridTransaction(YNABBaseModel):
    """Returned by the per-category and per-payee transactions endpoints.

    A flattened view that may represent either a regular transaction or a subtransaction.
    """
    id: str = Field()
    date: str = Field()
    amount: int = Field(default=0)
    memo: str | None = Field(default=None)
    cleared: str = Field(default="uncleared")
    approved: bool = Field(default=False)
    flag_color: str | None = Field(default=None)
    flag_name: str | None = Field(default=None)
    account_id: str | None = Field(default=None)
    account_name: str | None = Field(default=None)
    payee_id: str | None = Field(default=None)
    payee_name: str | None = Field(default=None)
    category_id: str | None = Field(default=None)
    category_name: str | None = Field(default=None)
    transfer_account_id: str | None = Field(default=None)
    transfer_transaction_id: str | None = Field(default=None)
    matched_transaction_id: str | None = Field(default=None)
    import_id: str | None = Field(default=None)
    import_payee_name: str | None = Field(default=None)
    import_payee_name_original: str | None = Field(default=None)
    debt_transaction_type: str | None = Field(default=None)
    type: str | None = Field(default=None)
    parent_transaction_id: str | None = Field(default=None)
    deleted: bool = Field(default=False)
