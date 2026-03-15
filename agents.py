"""Multi-agent system implementation using pydantic_ai for Munder Difflin Paper Company."""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from pydantic_ai import Agent, Tool
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

# ---- CONTEXT MODELS ----


class OrderContext(BaseModel):
    """Context for processing an order through the system."""

    order_id: str
    customer_request: str
    requested_items: dict  # {item_name: quantity}
    customer_budget: float = None
    deadline: str = None


# ---- TOOL DEFINITIONS FOR AGENTS ----

# Inventory Agent Tools


def check_inventory_stock(item: str) -> dict:
    """Check current stock level for a specific item using helper function get_stock_level."""
    stock = get_stock_level(item)
    return {"item": item, "current_stock": stock, "can_fulfill": stock > 0}


def get_complete_inventory() -> dict:
    """Get all inventory items and stock levels using helper function get_all_inventory."""
    all_items = get_all_inventory()
    return {
        "inventory_snapshot": all_items,
        "total_items": len(all_items),
        "timestamp": datetime.utcnow().isoformat(),
    }


def check_supplier_delivery(item: str) -> dict:
    """Check supplier delivery date for an item using helper function get_supplier_delivery_date."""
    delivery_date = get_supplier_delivery_date(item)
    return {
        "item": item,
        "supplier_delivery_date": delivery_date,
        "delivery_status": "on_schedule",
    }


# Quoting Agent Tools


def lookup_historical_quotes(query: str) -> dict:
    """Search historical quotes for similar requests using helper function search_quote_history."""
    results = search_quote_history(query)
    return results


# Finance Agent Tools


def check_company_cash() -> dict:
    """Check company cash balance using helper function get_cash_balance."""
    balance = get_cash_balance()
    return {
        "current_cash_balance": balance,
        "currency": "USD",
        "timestamp": datetime.utcnow().isoformat(),
    }


def generate_finance_report() -> dict:
    """Generate financial report using helper function generate_financial_report."""
    report = generate_financial_report()
    return {
        "financial_summary": report,
        "report_timestamp": datetime.utcnow().isoformat(),
    }


# Sales Agent Tools


def record_transaction(order_id: str, amount: float) -> dict:
    """Record a completed transaction using helper function create_transaction."""
    success = create_transaction(order_id, amount)
    return {
        "order_id": order_id,
        "transaction_amount": amount,
        "recorded": success,
        "timestamp": datetime.utcnow().isoformat() if success else None,
    }


def update_inventory_after_sale(items: dict) -> dict:
    """Reduce inventory after sale is confirmed."""
    total_reduced = 0
    for item, quantity in items.items():
        success = reduce_inventory(item, quantity)
        if success:
            total_reduced += quantity

    return {
        "inventory_updated": total_reduced > 0,
        "items_removed": total_reduced,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ---- AGENT DEFINITIONS (Simplified for testing without API) ----


class SimpleAgent:
    """Simple agent wrapper that uses tools directly without LLM calls."""

    def __init__(self, name, tools_dict):
        self.name = name
        self.tools_dict = tools_dict

    def run_sync(self, prompt):
        """Execute agent logic based on prompt."""
        return {"status": "success", "response": prompt}


# Inventory Agent - manages stock checks and supply chain
class InventoryAgent:
    """Inventory checking agent implementation."""

    def __init__(self):
        self.name = "InventoryAgent"

    def run_sync(self, prompt):
        """Check inventory availability for requested items."""
        try:
            # Extract requested items from prompt - parse JSON dict
            import json
            import re

            # Try to find requested_items JSON in the prompt
            json_match = re.search(
                r"\{[^}]*(?:item|quantity)[^}]*\}", prompt, re.DOTALL
            )
            requested_items = {}

            if json_match:
                try:
                    requested_items = json.loads(json_match.group())
                except:
                    pass

            # If we couldn't parse, try to extract from the prompt more broadly
            if not requested_items:
                # Try to extract from "requested the following items:" pattern
                items_match = re.search(
                    r"requested.*?items:?\s*\{[^}]+\}",
                    prompt,
                    re.IGNORECASE | re.DOTALL,
                )
                if items_match:
                    try:
                        requested_items = json.loads(
                            re.search(r"\{[^}]+\}", items_match.group()).group()
                        )
                    except:
                        pass

            # Get current inventory
            inventory = get_complete_inventory()
            inventory_snapshot = inventory.get("inventory_snapshot", {})

            # Check if all requested items are available in requested quantities
            can_fulfill = True
            unfulfilled_items = []

            if requested_items:
                for item, requested_qty in requested_items.items():
                    available_qty = inventory_snapshot.get(item, 0)
                    if available_qty < requested_qty:
                        can_fulfill = False
                        unfulfilled_items.append(
                            f"{item} (requested: {requested_qty}, available: {available_qty})"
                        )

            decision = "CAN_FULFILL" if can_fulfill else "CANNOT_FULFILL"
            response_msg = (
                f"Inventory check complete. "
                if can_fulfill
                else f"Inventory insufficient. "
            )

            if unfulfilled_items:
                response_msg += f"Cannot fulfill: {', '.join(unfulfilled_items)}"
            else:
                response_msg += f"All {len(requested_items)} items available in sufficient quantities."

            return {
                "status": "success",
                "decision": decision,
                "can_fulfill": can_fulfill,
                "inventory": inventory,
                "response": response_msg,
                "unfulfilled_items": unfulfilled_items,
            }
        except Exception as e:
            return {
                "status": "error",
                "decision": "CANNOT_FULFILL",
                "can_fulfill": False,
                "response": f"Inventory check failed: {str(e)}",
            }


inventory_agent = InventoryAgent()


# Quoting Agent - generates pricing and quotes
class QuotingAgent:
    """Quote generation agent implementation."""

    def __init__(self):
        self.name = "QuotingAgent"

    def run_sync(self, prompt):
        """Generate quote for customer order."""
        try:
            # Simple quote logic based on word count (items)
            min_quote = 50.0
            quote_amount = min_quote + (len(prompt.split()) * 2.5)
            quote_amount = round(quote_amount, 2)

            return {
                "status": "success",
                "quote_generated": True,
                "amount": quote_amount,
                "response": f"Quote generated: ${quote_amount}",
            }
        except Exception as e:
            return {
                "status": "error",
                "quote_generated": False,
                "amount": 0,
                "response": f"Quote generation failed: {str(e)}",
            }


quoting_agent = QuotingAgent()


# Finance Agent - ensures financial feasibility
class FinanceAgent:
    """Finance checking agent implementation."""

    def __init__(self):
        self.name = "FinanceAgent"

    def run_sync(self, prompt):
        """Verify financial feasibility of order."""
        try:
            import re

            # Extract quote amount from prompt
            amount_match = re.search(r"\$(\d+(?:\.\d{2})?)", prompt)
            quote_amount = 0
            if amount_match:
                quote_amount = float(amount_match.group(1))

            cash_balance = get_cash_balance()

            # Approved if we have enough cash to pay for the order
            # (In a real scenario, this would be cost of goods/fulfillment cost)
            approved = cash_balance >= quote_amount

            response_msg = (
                f"Finance check complete. Available cash: ${cash_balance:.2f}. "
            )
            if approved:
                response_msg += (
                    f"Quote amount ${quote_amount:.2f} is within budget. ✓ APPROVED"
                )
            else:
                response_msg += f"Quote amount ${quote_amount:.2f} exceeds available funds. ✗ REJECTED"

            return {
                "status": "success",
                "approved": approved,
                "cash_balance": cash_balance,
                "quote_amount": quote_amount,
                "response": response_msg,
            }
        except Exception as e:
            return {
                "status": "error",
                "approved": False,
                "cash_balance": 0,
                "response": f"Finance check failed: {str(e)}",
            }


finance_agent = FinanceAgent()


# Sales Finalization Agent - processes approved orders
class SalesAgent:
    """Sales finalization agent implementation."""

    def __init__(self):
        self.name = "SalesAgent"

    def run_sync(self, prompt):
        """Process and finalize completed order."""
        try:
            import json
            import re

            # Extract order_id from prompt
            order_id_match = re.search(r"Order (\w+-\w+)", prompt)
            order_id = order_id_match.group(1) if order_id_match else "ORD-UNKNOWN"

            # Extract quote amount from prompt
            amount_match = re.search(r"\$(\d+(?:\.\d{2})?)", prompt)
            quote_amount = 0
            if amount_match:
                quote_amount = float(amount_match.group(1))

            # Extract items dict from prompt
            items_match = re.search(r"Items:?\s*(\{[^}]+\})", prompt, re.IGNORECASE)
            requested_items = {}
            if items_match:
                try:
                    requested_items = json.loads(items_match.group(1))
                except:
                    pass

            # Record transaction
            transaction_recorded = record_transaction(order_id, quote_amount)

            # Update inventory
            inventory_updated = update_inventory_after_sale(requested_items)

            response_msg = f"Order {order_id} finalized successfully. "
            if transaction_recorded.get("recorded"):
                response_msg += f"Transaction ${quote_amount:.2f} recorded. "
            if inventory_updated.get("inventory_updated"):
                response_msg += f"Inventory reduced by {inventory_updated.get('items_removed')} units."

            return {
                "status": "success",
                "order_finalized": True,
                "order_id": order_id,
                "transaction_recorded": transaction_recorded.get("recorded", False),
                "inventory_updated": inventory_updated.get("inventory_updated", False),
                "response": response_msg,
            }
        except Exception as e:
            return {
                "status": "error",
                "order_finalized": False,
                "response": f"Order finalization failed: {str(e)}",
            }


sales_agent = SalesAgent()
