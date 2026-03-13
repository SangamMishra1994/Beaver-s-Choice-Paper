from agents import quoting_agent, inventory_agent, finance_agent, sales_agent


class OrchestratorAgent:

    def process_request(self, request):

        print("\n--- New Request ---")
        print("Customer Request:", request)

        # Step 1: Inventory Check
        inventory_result = inventory_agent.run(
            f"Check if we can fulfill this request: {request}"
        )

        print("Inventory Result:", inventory_result)

        # Step 2: Quote Generation
        quote_result = quoting_agent.run(f"Generate quote for this request: {request}")

        print("Quote Result:", quote_result)

        # Step 3: Finance Check
        finance_result = finance_agent.run(
            f"Check if we can financially support fulfilling this order: {request}"
        )

        print("Finance Result:", finance_result)

        decision = "fulfilled"

        if "cannot" in str(inventory_result).lower():
            decision = "unfulfilled"

        if "insufficient" in str(finance_result).lower():
            decision = "unfulfilled"

        # Step 4: Finalize Sale
        if decision == "fulfilled":

            sales_result = sales_agent.run(
                "Finalize the order and record the transaction."
            )

        else:
            sales_result = "Order not processed"

        return {
            "request": request,
            "quote": quote_result,
            "inventory": inventory_result,
            "finance": finance_result,
            "decision": decision,
            "sales": sales_result,
        }
