from src.server._shared import mcp

# Import domain modules to trigger @mcp.tool() registration
from src.server.budgets import list_budgets, get_budget  # noqa: F401
from src.server.accounts import list_accounts, get_account  # noqa: F401
from src.server.transactions import (  # noqa: F401
    list_transactions, get_transaction, get_transactions_by_account,
    get_transactions_by_category, get_transactions_by_payee,
    search_transactions, create_transaction, create_transactions,
    update_transaction, delete_transaction, update_transactions,
)
from src.server.categories import (  # noqa: F401
    list_categories, get_category, create_category, update_category,
    create_category_group, update_category_group,
    get_category_for_month, update_category_for_month,
)
from src.server.payees import list_payees  # noqa: F401
from src.server.months import list_months, get_month  # noqa: F401
from src.server.scheduled import list_scheduled_transactions  # noqa: F401
from src.server.analytics import get_money_flow, get_spending_by_category  # noqa: F401


def main():
    mcp.run(transport="stdio")
