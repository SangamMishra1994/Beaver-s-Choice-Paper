from orchestrator import OrchestratorAgent
from agents import quoting_agent, inventory_agent, finance_agent, sales_agent


class MunderDifflinAgent:

    def __init__(self):
        self.orchestrator = OrchestratorAgent()

    def process_request(self, request):

        result = self.orchestrator.process_request(request)

        if result["decision"] == "fulfilled":
            return f"Order completed. Quote: {result['quote']}"
        else:
            return (
                "Order could not be fulfilled due to inventory or finance constraints."
            )
