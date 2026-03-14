"""
Main execution script for the Munder Difflin Multi-Agent System.
Processes customer requests from quote_requests_sample.csv and generates results.
"""

import os
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv
from orchestrator import OrchestratorAgent
from diagram_generator import generate_workflow_diagram
from helpers import (
    initialize_inventory,
    initialize_cash_balance,
    generate_financial_report,
)

# Load environment variables
load_dotenv()

# Ensure database is initialized
initialize_inventory()
initialize_cash_balance()


def run_system_evaluation():
    """
    Run the multi-agent system on all sample requests and generate test_results.csv
    """
    print("\n" + "=" * 80)
    print("MUNDER DIFFLIN MULTI-AGENT SYSTEM - EVALUATION START")
    print("=" * 80)

    # Load sample requests
    try:
        requests_df = pd.read_csv("quote_requests_sample.csv")
        print(
            f"\nLoaded {len(requests_df)} customer requests from quote_requests_sample.csv"
        )
    except FileNotFoundError:
        print("ERROR: quote_requests_sample.csv not found!")
        return

    # Initialize orchestrator
    orchestrator = OrchestratorAgent()

    # Process each request
    print("\nProcessing requests through multi-agent system...\n")

    for idx, row in requests_df.iterrows():
        order_id = f"ORD-{idx+1:03d}"
        customer_request = row.get("request", "")

        # Process through orchestrator
        result = orchestrator.process_request(customer_request, order_id)

    # Get summary
    summary = orchestrator.get_summary()

    # Generate test results CSV
    generate_test_results(summary, requests_df)

    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Requests Processed: {summary['total_orders']}")
    print(f"  ✅ Fulfilled: {summary['fulfilled']}")
    print(f"  ❌ Unfulfilled: {summary['unfulfilled']}")
    print(
        f"  📊 Success Rate: {(summary['fulfilled']/summary['total_orders']*100):.1f}%"
    )
    print(f"\n💰 Total Revenue Generated: ${summary['total_revenue']:.2f}")

    # Final financial report
    final_report = generate_financial_report()
    print(f"\n📈 Final Financial Report:")
    print(f"   Current Cash Balance: ${final_report['current_cash_balance']:.2f}")
    print(f"   Total Sales Value: ${final_report['total_sales']:.2f}")
    print(f"   Transactions Recorded: {final_report['transaction_count']}")

    print("\n✅ Test results saved to test_results.csv")

    # Generate workflow diagram showing agent-to-agent communication
    print("\n📊 Generating workflow diagram showing multi-agent orchestration...")
    try:
        generate_workflow_diagram("workflow_diagram.png")
    except Exception as e:
        print(f"⚠️  Warning: Could not generate diagram: {e}")

    print("=" * 80 + "\n")

    return summary


def generate_test_results(summary: dict, requests_df: pd.DataFrame):
    """
    Generate test_results.csv with detailed order processing results.
    """
    results_data = []

    for order in summary["orders"]:
        result_row = {
            "order_id": order.get("order_id"),
            "status": order.get("final_status"),
            "reason_if_unfulfilled": order.get("reason", ""),
            "quote_amount": order.get("quote_amount", ""),
            "inventory_available": order.get("stages", {})
            .get("inventory", {})
            .get("can_fulfill", False),
            "finance_approved": order.get("stages", {})
            .get("finance", {})
            .get("approved", False),
            "customer_request_preview": order.get("customer_request", "")[:100],
            "requested_items": str(order.get("requested_items", {})),
            "timestamp": order.get("timestamp"),
        }
        results_data.append(result_row)

    # Create results dataframe
    results_df = pd.DataFrame(results_data)

    # Save to CSV
    results_df.to_csv("test_results.csv", index=False)

    # Also print to console
    print("\n" + "=" * 80)
    print("DETAILED TEST RESULTS")
    print("=" * 80)
    print(results_df.to_string())
    print("\n")


if __name__ == "__main__":
    run_system_evaluation()
