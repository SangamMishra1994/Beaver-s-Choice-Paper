This project implements a multi-agent system to automate the business workflow of Beaver’s Choice Paper Company.

Architecture
The system uses an orchestrator agent that coordinates four worker agents:
InventoryAgent, QuotingAgent, FinanceAgent, and SalesAgent.

The InventoryAgent checks stock levels using inventory tools.
The QuotingAgent generates price estimates based on historical quotes.
The FinanceAgent validates financial feasibility by checking company cash balance.
The SalesAgent records completed transactions.

Evaluation
The system was evaluated using the dataset quote_requests_sample.csv.
Results were generated in test_results.csv.

Strengths
The system separates responsibilities clearly across agents.
Agents use specialized tools to access business data.

Improvements
Future improvements could include:

1. Adding a negotiation agent to handle customer bargaining.
2. Implementing automatic supplier ordering when stock is insufficient.
