"""Multi-agent system implementation using pydantic_ai for Munder Difflin Paper Company."""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic import BaseModel
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

# Load environment variables before creating agents
load_dotenv()

# ---- API CONFIGURATION ----

# The project uses a custom OpenAI-compatible proxy
os.environ["OPENAI_BASE_URL"] = "https://openai.vocareum.com/v1"
API_KEY = os.getenv("OPENAI_API_KEY")

# ---- CONTEXT MODELS ----


class OrderContext(BaseModel):
    """Context for processing an order through the system."""

    order_id: str
    customer_request: str
    requested_items: dict  # {item_name: quantity}
    customer_budget: float = None
    deadline: str = None


# ---- RESPONSE MODELS ----


class InventoryResponse(BaseModel):
    """Structured response from the Inventory Agent."""

    can_fulfill: bool
    explanation: str
    available_items: dict
    missing_items: list[str]


class QuoteResponse(BaseModel):
    """Structured response from the Quoting Agent."""

    quote_amount: float
    breakdown: str
    applied_discounts: list[str]


class FinanceResponse(BaseModel):
    """Structured response from the Finance Agent."""

    approved: bool
    cash_balance: float
    explanation: str


class SalesResponse(BaseModel):
    """Structured response from the Sales Agent."""

    success: bool
    transaction_id: str
    explanation: str


# ---- AGENT DEFINITIONS ----

MODEL = "openai:gpt-4o"

# Inventory Agent - manages stock checks and supply chain
inventory_agent = Agent(
    MODEL,
    name="InventoryAgent",
    result_type=InventoryResponse,
    system_prompt=(
        "You are the Inventory Agent. Check if requested items are in stock. "
        "1. CALL 'get_complete_inventory' to see stock levels. "
        "2. Compare requested vs available. "
        "3. Set 'can_fulfill=True' ONLY if ALL items are available. "
        "4. If not, list missing items."
    ),
)


@inventory_agent.tool
def check_inventory_stock(ctx: RunContext[None], item: str) -> dict:
    """Check current stock level for a specific item."""
    stock = get_stock_level(item)
    return {"item": item, "current_stock": stock, "can_fulfill": stock > 0}


@inventory_agent.tool
def get_complete_inventory(ctx: RunContext[None]) -> dict:
    """Get all inventory items and stock levels."""
    all_items = get_all_inventory()
    return {
        "inventory_snapshot": all_items,
        "total_items": len(all_items),
        "timestamp": datetime.utcnow().isoformat(),
    }


@inventory_agent.tool
def check_supplier_delivery(ctx: RunContext[None], item: str) -> dict:
    """Check supplier delivery date for an item."""
    delivery_date = get_supplier_delivery_date(item)
    return {
        "item": item,
        "supplier_delivery_date": delivery_date,
        "delivery_status": "on_schedule",
    }


# Quoting Agent - generates pricing and quotes
quoting_agent = Agent(
    MODEL,
    name="QuotingAgent",
    result_type=QuoteResponse,
    system_prompt=(
        "You are the Quoting Agent. Generate a quote for the order. "
        "1. Base price: $0.05/sheet for standard (A4, A3, printer, copy), $0.15/sheet for specialty (cardstock, glossy, colored). "
        "2. Discounts: 10% off if total > 1000, 5% off if total > 500. "
        "3. Be mathematically precise. "
        "4. Provide a brief breakdown."
    ),
)


@quoting_agent.tool
def lookup_historical_quotes(ctx: RunContext[None], query: str) -> dict:
    """Search historical quotes for similar requests."""
    results = search_quote_history(query)
    return results


# Finance Agent - ensures financial feasibility
finance_agent = Agent(
    MODEL,
    name="FinanceAgent",
    result_type=FinanceResponse,
    system_prompt=(
        "You are the Finance Agent. This is a sale, so we are receiving money. "
        "1. CALL 'check_company_cash' to see balance. "
        "2. Approve the sale ('approved=True') unless it's clearly impossible. "
        "3. Report current balance."
    ),
)


@finance_agent.tool
def check_company_cash(ctx: RunContext[None]) -> dict:
    """Check company cash balance."""
    balance = get_cash_balance()
    return {
        "current_cash_balance": balance,
        "currency": "USD",
        "timestamp": datetime.utcnow().isoformat(),
    }


@finance_agent.tool
def generate_finance_report(ctx: RunContext[None]) -> dict:
    """Generate financial report."""
    report = generate_financial_report()
    return {
        "financial_summary": report,
        "report_timestamp": datetime.utcnow().isoformat(),
    }


# Sales Agent - processes approved orders
sales_agent = Agent(
    MODEL,
    name="SalesAgent",
    result_type=SalesResponse,
    system_prompt=(
        "You are the Sales Agent. Finalize the sale. "
        "1. YOU MUST CALL 'record_transaction_tool' with the quote amount. "
        "2. YOU MUST CALL 'update_inventory_after_sale_tool' with the items dictionary. "
        "3. Only if BOTH succeed, set 'success=True'."
    ),
)


@sales_agent.tool
def record_transaction_tool(ctx: RunContext[None], order_id: str, amount: float) -> dict:
    """Record a completed transaction."""
    success = create_transaction(order_id, amount)
    return {
        "order_id": order_id,
        "transaction_amount": amount,
        "recorded": success,
        "timestamp": datetime.utcnow().isoformat() if success else None,
    }


@sales_agent.tool
def update_inventory_after_sale_tool(ctx: RunContext[None], items: dict) -> dict:
    """Reduce inventory after sale is confirmed."""
    total_reduced = 0
    details = {}
    for item, quantity in items.items():
        success = reduce_inventory(item, quantity)
        if success:
            total_reduced += quantity
            details[item] = "updated"
        else:
            details[item] = "failed (insufficient stock)"

    return {
        "inventory_updated": total_reduced > 0,
        "items_removed": total_reduced,
        "details": details,
        "timestamp": datetime.utcnow().isoformat(),
    }
