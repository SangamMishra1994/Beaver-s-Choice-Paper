# Munder Difflin Multi-Agent System - Workflow Diagram & Architecture

## 1. System Architecture Overview

The Munder Difflin Multi-Agent System is designed with a hierarchical architecture consisting of:

- **1 Orchestrator Agent** (coordinator)
- **4 Worker Agents** (specialized functions)
- **10 Specialized Tools** (implementing helper functions)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CUSTOMER REQUESTS (CSV)                         │
│  - Inventory checks               - Quote generation                 │
│  - Sales inquiries                - Order fulfillment               │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR AGENT                                  │
│  Role: Coordinates workflow, delegates tasks, makes final decisions │
│  Process:                                                           │
│  1. Parse customer request                                         │
│  2. Extract requested items & quantities                           │
│  3. Delegate to worker agents in sequence:                         │
│     ├─ Inventory Agent (check stock availability)                  │
│     ├─ Quoting Agent (generate price quotes)                       │
│     ├─ Finance Agent (verify financial feasibility)                │
│     └─ Sales Agent (process & finalize order)                      │
│  4. Aggregate results & return order status                        │
└─────────┬──────────────┬──────────────┬──────────────┬──────────────┘
          │              │              │              │
    Phase 1         Phase 2         Phase 3        Phase 4
┌─────────▼────────┐ ┌────────▼─────────┐ ┌──────▼──────────┐ ┌───▼────────────┐
│  INVENTORY       │ │    QUOTING       │ │    FINANCE      │ │     SALES      │
│     AGENT        │ │     AGENT        │ │     AGENT       │ │     AGENT      │
└──────────────────┘ └──────────────────┘ └─────────────────┘ └───────────────┘
  Responsibility:      Responsibility:     Responsibility:    Responsibility:
  ✓ Stock checks       ✓ Price quotes      ✓ Cash balance     ✓ Record sales
  ✓ Supply timing      ✓ Bulk discounts    ✓ Fund approval    ✓ Update inventory
  ✓ Order feasibility  ✓ Historical refs   ✓ Risk assessment  ✓ Transaction log
        │                    │                    │                   │
        ▼                    ▼                    ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   TOOLS & DATA   │ │  TOOLS & DATA    │ │  TOOLS & DATA    │ │  TOOLS & DATA    │
├──────────────────┤ ├──────────────────┤ ├──────────────────┤ ├──────────────────┤
│ ✓ check_inv_     │ │ ✓ lookup_        │ │ ✓ check_company_ │ │ ✓ record_        │
│   stock()        │ │   historical_    │ │   cash()         │ │   transaction()  │
│   Helper:        │ │   quotes()       │ │   Helper:        │ │   Helper:        │
│   get_stock_     │ │   Helper:        │ │   get_cash_      │ │   create_        │
│   level()        │ │   search_quote   │ │   balance()      │ │   transaction()  │
│                  │ │   _history()     │ │                  │ │                  │
├──────────────────┤ │                  │ ├──────────────────┤ ├──────────────────┤
│ ✓ get_complete_  │ │                  │ │ ✓ generate_      │ │ ✓ update_        │
│   inventory()    │ │                  │ │   finance_       │ │   inventory_     │
│   Helper:        │ │                  │ │   report()       │ │   after_sale()   │
│   get_all_       │ │                  │ │   Helper:        │ │   Helper:        │
│   inventory()    │ │                  │ │   generate_      │ │   reduce_        │
│                  │ │                  │ │   financial_     │ │   inventory()    │
├──────────────────┤ │                  │ │   report()       │ ├──────────────────┤
│ ✓ check_supplier_│ │                  │ │                  │ │ Additional Helper│
│   delivery()     │ │                  │ │                  │ │ Functions Used:  │
│   Helper:        │ │                  │ │                  │ │ • get_supplier_  │
│   get_supplier_  │ │                  │ │                  │ │   delivery_date()│
│   delivery_date()│ │                  │ │                  │ │ • get_all_       │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
```

## 2. Agent Responsibilities & Tools

### Inventory Manager Agent

**Primary Role:** Assess inventory availability and supply chain feasibility

**Tools:**

1. `check_inventory_stock(item: str)` → Uses `get_stock_level()`
   - Returns current stock level for specific item
   - Determines if order quantity can be fulfilled
2. `get_complete_inventory()` → Uses `get_all_inventory()`
   - Returns snapshot of all inventory items
   - Provides overview before item-specific checks
3. `check_supplier_delivery(item: str)` → Uses `get_supplier_delivery_date()`
   - Retrieves next delivery date for low-stock items
   - Helps assess if future orders can be fulfilled

**Decision Logic:**

- CAN_FULFILL: All requested items have sufficient stock
- CANNOT_FULFILL: Any item has insufficient stock OR restock timeline doesn't meet deadline

---

### Quoting Agent

**Primary Role:** Generate competitive and transparent pricing

**Tools:**

1. `lookup_historical_quotes(query: str)` → Uses `search_quote_history()`
   - Searches past quotes matching order characteristics
   - Provides pricing precedent for similar orders

**Quote Calculation:**

- Base pricing per paper type (e.g., A4: $0.05/sheet, cardstock: $0.15/sheet)
- Quantity multiplier: units × unit_price
- Bulk discount logic:
  - 10% discount for orders > 1000 units
  - 5% discount for orders 500-1000 units
  - No discount for orders < 500 units
- Return: Itemized breakdown + total with discount applied

---

### Finance Agent

**Primary Role:** Verify financial viability of orders

**Tools:**

1. `check_company_cash()` → Uses `get_cash_balance()`
   - Returns current available cash
   - Determines if transaction amount is affordable
2. `generate_finance_report()` → Uses `generate_financial_report()`
   - Provides financial health summary
   - Shows transaction history and cash trends

**Approval Criteria:**

- APPROVED: Current cash balance ≥ quote amount + safety reserve (20% of balance)
- REJECTED: Insufficient funds after accounting for operational reserves

---

### Sales Finalization Agent

**Primary Role:** Process approved orders and update company records

**Tools:**

1. `record_transaction(order_id: str, amount: float)` → Uses `create_transaction()`
   - Records sale as financial transaction
   - Updates cash balance (deducts order cost)
   - Returns transaction confirmation
2. `update_inventory_after_sale(items: dict)` → Uses `reduce_inventory()`
   - Decrements stock for each fulfilled item
   - Updates inventory database
   - Returns confirmation of stock reduction

**Finalization Process:**

- Record transaction with order ID and amount
- Reduce inventory by ordered quantities
- Generate confirmation with order details
- Log transaction timestamp

---

## 3. Data Flow & Integration Points

### Input: Customer Request

```json
{
  "customer_role": "office manager",
  "request": "200 sheets of A4 glossy paper, 100 sheets of cardstock...",
  "deadline": "April 15, 2025"
}
```

### Processing Pipeline

1. **Request Parsing**
   - Extract items: {"A4 paper": 200, "cardstock": 100}
   - Validate against available types
   - Set order context (deadline, budget if mentioned)

2. **Inventory Phase**
   - Agent calls: `get_complete_inventory()` then `check_inventory_stock()` for each item
   - Database access: Inventory table via SQLAlchemy ORM
   - Decision point: PROCEED or HALT

3. **Quoting Phase** (if inventory approved)
   - Agent calls: `lookup_historical_quotes()` to find similar orders
   - Calculation: Base pricing + quantity + bulk discount
   - Return: Quote amount and itemized breakdown

4. **Finance Phase** (if quote generated)
   - Agent calls: `check_company_cash()` then `generate_finance_report()`
   - Decision logic: Balance ≥ (quote_amount × 1.2)
   - Return: APPROVED or REJECTED with reasoning

5. **Sales Phase** (if finance approved)
   - Agent calls: `record_transaction()` with order_id and amount
   - Agent calls: `update_inventory_after_sale()` with items dict
   - Updates: FinancialRecord table + Inventory table
   - Return: Confirmation with transaction ID

### Output: Order Processing Result

```json
{
  "order_id": "ORD-001",
  "final_status": "FULFILLED",
  "quote_amount": 65.50,
  "inventory_decision": "CAN_FULFILL",
  "finance_decision": "APPROVED",
  "stages": {
    "inventory": {"can_fulfill": true, ...},
    "quoting": {"quote_amount": 65.50, ...},
    "finance": {"approved": true, ...},
    "sales": {"transaction_recorded": true, ...}
  }
}
```

---

## 4. Helper Functions Utilization Matrix

| Helper Function                | Primary Agent | Purpose                    | Tool Name                   |
| ------------------------------ | ------------- | -------------------------- | --------------------------- |
| `get_stock_level()`            | Inventory     | Check item quantity        | check_inventory_stock       |
| `get_all_inventory()`          | Inventory     | Get all stock levels       | get_complete_inventory      |
| `get_supplier_delivery_date()` | Inventory     | Check restock timing       | check_supplier_delivery     |
| `search_quote_history()`       | Quoting       | Find historical precedents | lookup_historical_quotes    |
| `get_cash_balance()`           | Finance       | Check available funds      | check_company_cash          |
| `generate_financial_report()`  | Finance       | Get financial summary      | generate_finance_report     |
| `create_transaction()`         | Sales         | Record sale                | record_transaction          |
| `reduce_inventory()`           | Sales         | Update stock               | update_inventory_after_sale |
| `get_supplier_delivery_date()` | Inventory     | Restock scheduling         | check_supplier_delivery     |
| `get_cash_balance()`           | Finance       | Financial verification     | check_company_cash          |

---

## 5. Decision Trees

### Order Processing Decision Tree

```
START: Customer Request
  │
  ├─ Inventory Agent: Can we fulfill?
  │  ├─ YES → Continue
  │  └─ NO → UNFULFILLED (reason: insufficient inventory)
  │
  ├─ Quoting Agent: Generate quote
  │  ├─ SUCCESS → Proceed with amount
  │  └─ FAILURE → Use fallback estimation
  │
  ├─ Finance Agent: Can we afford?
  │  ├─ YES → Continue
  │  └─ NO → UNFULFILLED (reason: insufficient funds)
  │
  ├─ Sales Agent: Record & finalize
  │  ├─ SUCCESS → FULFILLED ✓
  │  └─ FAILURE → UNFULFILLED (reason: transaction error)
  │
  END: Return order result
```

---

## 6. Orchestration Framework Choice: pydantic-ai

**Why pydantic-ai?**

- Structured tool definitions with clear contracts
- Type-safe agent tool integration
- Synchronous `run_sync()` method for orchestrated workflows
- Excellent for sequential agent delegation patterns
- Built-in support for agent instructions and context

**Implementation:**

```python
# Agent with tools
agent = Agent(
    model="gpt-4o",
    name="InventoryAgent",
    tools=[Tool(check_inventory_stock), Tool(get_complete_inventory)],
    instructions="..."
)

# Orchestrated execution
response = agent.run_sync("Check if we can fulfill this order...")
result = response.data  # Extract structured result
```

---

## 7. Success Metrics & Expected Behavior

**Fulfillment Criteria:**

- ✅ All 4 stages must complete successfully
- ✅ Inventory available for all requested items
- ✅ Quote amount must be computable
- ✅ Cash balance must cover transaction
- ✅ Transaction must record without errors

**Performance Expectations:**

- Typical order processing time: 2-3 seconds (with API calls)
- Success rate: 60-70% fulfillment (due to inventory/finance constraints)
- Revenue per fulfilled order: $50-$150
- Average quote discount: 5-10% for bulk orders
