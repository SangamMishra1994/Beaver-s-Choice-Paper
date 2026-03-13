from pydantic_ai import Agent, Tool
from helpers import (
    create_transaction,
    get_all_inventory,
    get_stock_level,
    get_supplier_delivery_date,
    get_cash_balance,
    generate_financial_report,
    search_quote_history,
    reduce_inventory,
)

# ---- TOOLS ----


@Tool
def inventory_lookup(item: str):
    """Check inventory levels for an item."""
    stock = get_stock_level(item)
    return {"item": item, "stock": stock}


@Tool
def get_full_inventory():
    """Get all inventory items and their stock levels."""
    return get_all_inventory()


@Tool
def supplier_eta(item: str):
    """Get supplier delivery date."""
    return get_supplier_delivery_date(item)


@Tool
def quote_history(query: str):
    """Search past quotes."""
    return search_quote_history(query)


@Tool
def check_cash():
    """Get company cash balance."""
    return get_cash_balance()


@Tool
def finalize_sale(order_id: str, amount: float):
    """Record a completed transaction."""
    create_transaction(order_id, amount)
    return {"status": "transaction recorded"}


@Tool
def financial_report():
    """Generate finance summary."""
    return generate_financial_report()


# ---- AGENTS ----

quoting_agent = Agent(
    name="QuotingAgent",
    tools=[quote_history],
    instructions="""
You are responsible for generating quotes for customer requests.

Steps:
1. Check historical quote data using quote_history tool.
2. Estimate price for requested item and quantity.
3. Return structured quote response including price and reasoning.
""",
)

inventory_agent = Agent(
    name="InventoryAgent",
    tools=[inventory_lookup, get_full_inventory, supplier_eta],
    instructions="""
You manage inventory decisions.

Steps:
1. Use get_full_inventory tool to get overview of all stock levels.
2. Use inventory_lookup tool to check specific stock levels.
3. If stock is low, use supplier_eta tool to check delivery date.
4. Return whether order can be fulfilled or not with reasoning.
""",
)

finance_agent = Agent(
    name="FinanceAgent",
    tools=[check_cash, financial_report],
    instructions="""
You verify financial feasibility.

Steps:
1. Check company cash balance using check_cash.
2. Decide if the company can afford the transaction.
3. Provide approval or rejection reasoning.
""",
)

sales_agent = Agent(
    name="SalesAgent",
    tools=[finalize_sale],
    instructions="""
You finalize approved sales.

Steps:
1. Record the completed transaction using finalize_sale tool.
2. Return confirmation that the sale has been processed.
""",
)
