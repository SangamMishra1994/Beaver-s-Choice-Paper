"""Orchestrator for multi-agent system - coordinates all agents in proper sequence."""

import json
import re
from datetime import datetime
from agents import (
    inventory_agent,
    quoting_agent,
    finance_agent,
    sales_agent,
    OrderContext,
)


class OrchestratorAgent:
    """Orchestrates the workflow between Inventory, Quoting, Finance, and Sales agents."""

    def __init__(self):
        """Initialize the orchestrator with access to all worker agents."""
        self.inventory_agent = inventory_agent
        self.quoting_agent = quoting_agent
        self.finance_agent = finance_agent
        self.sales_agent = sales_agent
        self.results = []

    def extract_items_from_request(self, request: str) -> dict:
        """
        Extract requested items and quantities from customer request.
        Returns a dictionary {item_name: quantity_requested}
        """
        # Look for patterns like "200 sheets of A4 paper", "500 sheets of colored paper"
        items = {}

        # Common paper items we track
        paper_types = [
            "A4 paper",
            "A3 paper",
            "cardstock",
            "colored paper",
            "standard copy paper",
            "letter-sized paper",
            "printer paper",
            "glossy paper",
            "construction paper",
            "poster paper",
        ]

        request_lower = request.lower()

        for paper_type in paper_types:
            if paper_type in request_lower:
                # Extract quantity - look for numbers before the paper type
                import re

                pattern = (
                    r"(\d+)\s+(?:sheets?|reams?|units?|rolls?)\s+of\s+"
                    + re.escape(paper_type)
                )
                matches = re.findall(pattern, request_lower, re.IGNORECASE)
                if matches:
                    items[paper_type] = int(matches[0])
                else:
                    # If we find the type but no quantity, assume small order
                    if items.get(paper_type) is None:
                        items[paper_type] = 100  # Default quantity

        # If no specific items found, try generic paper
        if not items:
            # Look for any quantity mentioned with paper
            if "paper" in request_lower:
                items["A4 paper"] = 500  # Default fallback
            elif "cardstock" in request_lower:
                items["cardstock"] = 200
            elif "colored paper" in request_lower:
                items["colored paper"] = 300

        return items if items else {"A4 paper": 500}

    def parse_inventory_decision(self, response: str) -> dict:
        """Parse inventory agent response to extract decision."""
        # Handle both string and object responses
        response_text = str(response).lower()
        can_fulfill = (
            "can_fulfill" in response_text
            or "can fulfill" in response_text
            or "fulfilled" in response_text
            or "yes" in response_text
        )

        return {"can_fulfill": can_fulfill, "response": str(response)}

    def parse_quote_response(self, response: str) -> dict:
        """Parse quoting agent response to extract quote amount."""
        response_text = str(response)

        # Look for quote amount pattern: $123 or quote_amount: $123
        amounts = re.findall(r"\$(\d+(?:\.\d{2})?)", response_text)

        quote_amount = None
        if amounts:
            quote_amount = float(amounts[0])

        return {"quote_amount": quote_amount, "response": response_text}

    def parse_finance_decision(self, response: str) -> dict:
        """Parse finance agent response to extract decision."""
        response_text = str(response).lower()
        approved = "approved" in response_text or "yes" in response_text

        remaining = re.findall(r"\$(\d+(?:\.\d{2})?)", str(response))
        remaining_balance = float(remaining[0]) if remaining else None

        return {
            "approved": approved,
            "remaining_balance": remaining_balance,
            "response": str(response),
        }

    def process_request(self, request: str, order_id: str = None) -> dict:
        """
        Process a customer request through the entire agent workflow.

        Args:
            request: Customer's text request
            order_id: Unique identifier for this order

        Returns:
            Dictionary with complete order processing result
        """
        if not order_id:
            order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        print(f"\n{'='*80}")
        print(f"PROCESSING ORDER: {order_id}")
        print(f"{'='*80}")
        print(f"Customer Request: {request[:200]}...")

        # Extract requested items
        requested_items = self.extract_items_from_request(request)
        print(f"\nExtracted Items: {requested_items}")

        # Create order context
        context = OrderContext(
            order_id=order_id, customer_request=request, requested_items=requested_items
        )

        result = {
            "order_id": order_id,
            "customer_request": request[:200] + "...",
            "requested_items": requested_items,
            "timestamp": datetime.utcnow().isoformat(),
            "stages": {},
        }

        # STAGE 1: Inventory Check
        print("\n[STAGE 1] Checking Inventory...")
        inventory_prompt = f"""
A customer has requested the following items: {json.dumps(requested_items)}

Request: {request}

Check if we can fulfill this order using your available tools.
"""
        try:
            inventory_response = self.inventory_agent.run_sync(inventory_prompt)
            # Handle both direct string and agent response object
            response_data = (
                inventory_response.data
                if hasattr(inventory_response, "data")
                else inventory_response
            )
            inventory_result = self.parse_inventory_decision(str(response_data))
            result["stages"]["inventory"] = inventory_result
            print(
                f"Inventory Decision: {'✅ CAN FULFILL' if inventory_result['can_fulfill'] else '❌ CANNOT FULFILL'}"
            )

            if not inventory_result["can_fulfill"]:
                result["final_status"] = "UNFULFILLED"
                result["reason"] = "Insufficient inventory"
                print(f"❌ Order cannot be fulfilled - insufficient inventory\n")
                self.results.append(result)
                return result
        except Exception as e:
            print(f"⚠️  Inventory check error: {e}")
            result["stages"]["inventory"] = {"can_fulfill": False, "error": str(e)}
            result["final_status"] = "UNFULFILLED"
            result["reason"] = "Inventory check failed"
            self.results.append(result)
            return result

        # STAGE 2: Generate Quote
        print("\n[STAGE 2] Generating Quote...")
        quote_prompt = f"""
We can fulfill an order for: {json.dumps(requested_items)}

Customer request: {request}

Generate a competitive quote considering bulk discounts (10% for large orders, 5% for medium).
Provide the total quote amount and brief pricing breakdown.
"""
        try:
            quote_response = self.quoting_agent.run_sync(quote_prompt)
            response_data = (
                quote_response.data
                if hasattr(quote_response, "data")
                else quote_response
            )
            quote_result = self.parse_quote_response(str(response_data))
            result["stages"]["quoting"] = quote_result

            if quote_result["quote_amount"] is None:
                quote_result["quote_amount"] = self.estimate_quote(requested_items)

            print(f"Quote Generated: 💰 ${quote_result['quote_amount']:.2f}")
        except Exception as e:
            print(f"⚠️  Quote generation error: {e}")
            quote_result = {"quote_amount": self.estimate_quote(requested_items)}
            result["stages"]["quoting"] = quote_result
            print(f"Quote Generated (fallback): ${quote_result['quote_amount']:.2f}")

        # STAGE 3: Finance Check
        print("\n[STAGE 3] Checking Finance...")
        finance_prompt = f"""
Proposed quote amount: ${quote_result['quote_amount']:.2f}

Order: {json.dumps(requested_items)}

Check if company can financially support this order. Use your tools to verify cash balance and report.
"""
        try:
            finance_response = self.finance_agent.run_sync(finance_prompt)
            response_data = (
                finance_response.data
                if hasattr(finance_response, "data")
                else finance_response
            )
            finance_result = self.parse_finance_decision(str(response_data))
            result["stages"]["finance"] = finance_result
            print(
                f"Finance Decision: {'✅ APPROVED' if finance_result['approved'] else '❌ REJECTED'}"
            )

            if not finance_result["approved"]:
                result["final_status"] = "UNFULFILLED"
                result["reason"] = "Insufficient funds"
                print(f"❌ Order cannot be fulfilled - insufficient funds\n")
                self.results.append(result)
                return result
        except Exception as e:
            print(f"⚠️  Finance check error: {e}")
            result["stages"]["finance"] = {"approved": False, "error": str(e)}
            result["final_status"] = "UNFULFILLED"
            result["reason"] = "Finance check failed"
            self.results.append(result)
            return result

        # STAGE 4: Finalize Sale
        print("\n[STAGE 4] Finalizing Sale...")
        sales_prompt = f"""
Order {order_id} has been approved for ${quote_result['quote_amount']:.2f}

Items: {json.dumps(requested_items)}

Finalize this sale by recording the transaction and updating inventory.
"""
        try:
            sales_response = self.sales_agent.run_sync(sales_prompt)
            response_data = (
                sales_response.data
                if hasattr(sales_response, "data")
                else sales_response
            )
            sales_result = {"response": str(response_data), "success": True}
            result["stages"]["sales"] = sales_result
            result["final_status"] = "FULFILLED"
            result["quote_amount"] = quote_result["quote_amount"]
            print(f"✅ Order confirmed and processed!")
        except Exception as e:
            print(f"⚠️  Sales finalization error: {e}")
            result["stages"]["sales"] = {"success": False, "error": str(e)}
            result["final_status"] = "UNFULFILLED"
            result["reason"] = "Sales processing failed"

        print(f"\n{'='*80}\n")
        self.results.append(result)
        return result

    def estimate_quote(self, items: dict) -> float:
        """
        Estimate quote based on standard pricing.
        Used as fallback if quote generation fails.
        """
        # Base pricing per item type
        pricing = {
            "A4 paper": 0.05,
            "A3 paper": 0.06,
            "cardstock": 0.15,
            "colored paper": 0.10,
            "standard copy paper": 0.05,
            "letter-sized paper": 0.05,
            "printer paper": 0.05,
            "glossy paper": 0.08,
            "construction paper": 0.07,
            "poster paper": 0.12,
        }

        total = 0
        total_quantity = 0
        for item, quantity in items.items():
            price_per_unit = pricing.get(item, 0.10)
            total += quantity * price_per_unit
            total_quantity += quantity

        # Apply bulk discount
        if total_quantity > 1000:
            total *= 0.90  # 10% discount
        elif total_quantity > 500:
            total *= 0.95  # 5% discount

        return round(total, 2)

    def get_summary(self) -> dict:
        """Get summary of all processed orders."""
        fulfilled = sum(1 for r in self.results if r.get("final_status") == "FULFILLED")
        unfulfilled = sum(
            1 for r in self.results if r.get("final_status") == "UNFULFILLED"
        )
        total_revenue = sum(
            r.get("quote_amount", 0)
            for r in self.results
            if r.get("final_status") == "FULFILLED"
        )

        return {
            "total_orders": len(self.results),
            "fulfilled": fulfilled,
            "unfulfilled": unfulfilled,
            "total_revenue": total_revenue,
            "orders": self.results,
        }
