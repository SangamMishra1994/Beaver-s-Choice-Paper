Reflection Report – Multi-Agent Sales Automation System
1. System Architecture and Workflow

The system is designed as a multi-agent architecture where an orchestrator agent coordinates several specialized worker agents to process customer quote requests.

The workflow begins when a customer request is received from the dataset quote_requests_sample.csv. This request is passed to the Orchestrator Agent, which is responsible for analyzing the request and delegating tasks to the appropriate worker agents.

The system consists of the following agents:

Orchestrator Agent

The orchestrator agent acts as the central coordinator of the system. It receives incoming requests and determines which worker agents should be responsible for handling each part of the task. It then collects the outputs from each agent and compiles the final response for the customer.

Inventory Agent

The inventory agent is responsible for checking product availability and ensuring that sufficient stock exists before a quote can be fulfilled. It interacts with the inventory data using the following helper functions:

get_all_inventory()

get_stock_level()

get_supplier_delivery_date()

These functions allow the system to verify whether items are available and whether additional stock can be ordered from suppliers if needed.

Quote Agent

The quote agent generates pricing information for customer requests. It uses historical quote data to help determine pricing and ensure consistency in quoting. This agent uses the helper function:

search_quote_history()

By analyzing previous quotes, the system can provide more consistent pricing decisions.

Sales / Ordering Agent

The sales agent finalizes the transaction if the request can be fulfilled. This agent is responsible for recording transactions and updating the financial state of the business. It interacts with the system through the following helper functions:

create_transaction()

get_cash_balance()

generate_financial_report()

These tools ensure that all financial operations are tracked correctly.

To implement the multi-agent architecture, the system uses the smolagents framework, which allows the definition of multiple agents and enables orchestration between them.

2. Evaluation of the System

The system was evaluated using the dataset provided in quote_requests_sample.csv. Each request in the dataset was processed by the multi-agent system, and the results were recorded in the file test_results.csv.

The evaluation demonstrated the following outcomes:

Multiple quote requests were successfully processed and fulfilled.

Several requests resulted in updates to the system's cash balance, indicating that transactions were successfully completed.

Some requests were not fulfilled due to conditions such as insufficient stock or unavailable products.

These outcomes demonstrate that the system correctly evaluates inventory availability before committing to transactions and prevents orders that cannot be fulfilled.

A key strength of the system is that it separates responsibilities across multiple agents, allowing each agent to focus on a specific domain such as inventory management, pricing, or financial transactions. This modular design makes the system easier to maintain and extend.

3. Strengths of the Implementation

The implemented multi-agent system has several strengths.

First, the clear separation of responsibilities between agents improves modularity and scalability. Each agent performs a well-defined role, making the architecture easier to maintain.

Second, the system integrates helper functions from the starter code, ensuring that the business logic for inventory, financial transactions, and historical quotes is reused consistently.

Third, the system produces transparent outputs for customer interactions, providing clear responses when requests cannot be fulfilled due to stock limitations or other operational constraints.

Finally, the architecture is designed to be extensible, meaning additional agents or tools can easily be added to expand the system’s capabilities.

4. Potential Improvements

Although the system functions correctly, there are several potential improvements that could enhance its performance and capabilities.

Improvement 1 – Negotiation Agent

A negotiation agent could be introduced to interact with customers and dynamically adjust pricing based on demand, order quantity, or previous customer interactions. This would make the system more flexible and realistic for real-world sales scenarios.

Improvement 2 – Automated Supplier Ordering

The system could be enhanced with a supplier management agent that automatically places restocking orders when inventory levels fall below a certain threshold. This would help prevent situations where customer requests cannot be fulfilled due to insufficient stock.

Improvement 3 – Business Analytics Agent

Another improvement would be the addition of a business analytics agent that continuously analyzes transaction history and financial reports to provide recommendations for improving profitability and operational efficiency.

5. Conclusion

The implemented multi-agent system successfully demonstrates how multiple specialized agents can collaborate to process customer requests, verify inventory, generate quotes, and finalize transactions. By combining orchestrator logic with dedicated worker agents and helper functions, the system provides a modular and scalable architecture suitable for automated sales workflows.

The evaluation results confirm that the system correctly handles both successful and unsuccessful requests while maintaining accurate financial tracking. With further enhancements such as negotiation capabilities and automated restocking, the system could evolve into a more advanced intelligent business assistant.