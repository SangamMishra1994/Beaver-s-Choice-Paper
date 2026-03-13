"""Helper functions for the Beaver's Choice Paper multi-agent system."""

import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Float, DateTime
from sqlalchemy.orm import declarative_base, Session

# Database setup
DATABASE_URL = "sqlite:///munder_difflin.db"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

# ---- DATABASE MODELS ----


class Inventory(Base):
    """Inventory model for tracking stock levels."""

    __tablename__ = "inventory"

    item = Column(String, primary_key=True)
    quantity = Column(Float, default=1000)
    supplier_delivery_date = Column(String, default="2025-04-15")


class FinancialRecord(Base):
    """Financial record model for transactions."""

    __tablename__ = "financial_records"

    id = Column(String, primary_key=True)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    transaction_type = Column(String)


class CashBalance(Base):
    """Cash balance model."""

    __tablename__ = "cash_balance"

    id = Column(String, primary_key=True, default="main")
    balance = Column(Float, default=10000.0)
    last_updated = Column(DateTime, default=datetime.utcnow)


# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


# ---- HELPER FUNCTIONS ----


def get_session():
    """Get a database session."""
    return Session(engine)


def initialize_inventory():
    """Initialize inventory with default items if empty."""
    session = get_session()
    try:
        items = session.query(Inventory).all()
        if not items:
            default_items = [
                Inventory(
                    item="A4 paper", quantity=5000, supplier_delivery_date="2025-04-15"
                ),
                Inventory(
                    item="cardstock", quantity=2000, supplier_delivery_date="2025-04-15"
                ),
                Inventory(
                    item="colored paper",
                    quantity=3000,
                    supplier_delivery_date="2025-04-15",
                ),
                Inventory(
                    item="standard copy paper",
                    quantity=4000,
                    supplier_delivery_date="2025-04-15",
                ),
                Inventory(
                    item="letter-sized paper",
                    quantity=2500,
                    supplier_delivery_date="2025-04-15",
                ),
            ]
            session.add_all(default_items)
            session.commit()
    finally:
        session.close()


def initialize_cash_balance():
    """Initialize cash balance if not exists."""
    session = get_session()
    try:
        balance = session.query(CashBalance).filter_by(id="main").first()
        if not balance:
            balance = CashBalance(id="main", balance=10000.0)
            session.add(balance)
            session.commit()
    finally:
        session.close()


def get_stock_level(item: str) -> int:
    """
    Get the current stock level for an item.

    Args:
        item: The name of the item

    Returns:
        The quantity in stock
    """
    session = get_session()
    try:
        initialize_inventory()
        inventory_item = session.query(Inventory).filter_by(item=item).first()
        if inventory_item:
            return int(inventory_item.quantity)
        return 0
    finally:
        session.close()


def get_all_inventory() -> dict:
    """
    Get all inventory items and their stock levels.

    Returns:
        Dictionary with item names as keys and quantities as values
    """
    session = get_session()
    try:
        initialize_inventory()
        items = session.query(Inventory).all()
        return {item.item: int(item.quantity) for item in items}
    finally:
        session.close()


def get_supplier_delivery_date(item: str) -> str:
    """
    Get the supplier delivery date for an item.

    Args:
        item: The name of the item

    Returns:
        Delivery date as a string
    """
    session = get_session()
    try:
        initialize_inventory()
        inventory_item = session.query(Inventory).filter_by(item=item).first()
        if inventory_item:
            return inventory_item.supplier_delivery_date
        return "2025-04-15"  # Default delivery date
    finally:
        session.close()


def get_cash_balance() -> float:
    """
    Get the company's current cash balance.

    Returns:
        Current cash balance
    """
    session = get_session()
    try:
        initialize_cash_balance()
        balance = session.query(CashBalance).filter_by(id="main").first()
        if balance:
            return float(balance.balance)
        return 10000.0
    finally:
        session.close()


def create_transaction(order_id: str, amount: float) -> bool:
    """
    Record a transaction and update cash balance.
    Deducts the amount from company balance (payment received).

    Args:
        order_id: The order ID
        amount: The amount of the transaction

        Returns:
        True if transaction was recorded successfully
    """
    session = get_session()
    try:
        initialize_cash_balance()

        # Record the transaction
        transaction = FinancialRecord(
            id=order_id, amount=amount, transaction_type="sale"
        )
        session.add(transaction)

        # Update cash balance - DEDUCT the cost of goods/fulfilled order
        balance = session.query(CashBalance).filter_by(id="main").first()
        if balance:
            # Deduct from balance since we need to pay for inventory/fulfillment
            balance.balance -= amount
            if balance.balance < 0:
                session.rollback()
                return False  # Insufficient funds
    except Exception as e:
        print(f"Error creating transaction: {e}")
        return False
    finally:
        session.close()


def generate_financial_report() -> dict:
    """
    Generate a financial report.

    Returns:
        Dictionary containing financial summary
    """
    session = get_session()
    try:
        initialize_cash_balance()

        balance = session.query(CashBalance).filter_by(id="main").first()
        current_balance = float(balance.balance) if balance else 0

        transactions = session.query(FinancialRecord).all()
        total_sales = sum(
            t.amount for t in transactions if t.transaction_type == "sale"
        )
        transaction_count = len(transactions)

        return {
            "current_cash_balance": current_balance,
            "total_sales": total_sales,
            "transaction_count": transaction_count,
            "report_date": datetime.utcnow().isoformat(),
        }
    finally:
        session.close()


def reduce_inventory(item: str, quantity: float) -> bool:
    """
    Reduce inventory when an order is fulfilled.

    Args:
        item: The item name
        quantity: Quantity to reduce

    Returns:
        True if reduction was successful, False if insufficient stock
    """
    session = get_session()
    try:
        initialize_inventory()
        inventory_item = session.query(Inventory).filter_by(item=item).first()

        if inventory_item and inventory_item.quantity >= quantity:
            inventory_item.quantity -= quantity
            session.commit()
            return True

        return False  # Insufficient stock
    except Exception as e:
        print(f"Error reducing inventory: {e}")
        return False
    finally:
        session.close()


def search_quote_history(query: str) -> dict:
    """
    Search historical quotes from quotes.csv.

    Args:
        query: Search query string

    Returns:
        Dictionary with matching quotes
    """
    try:
        # Read quotes CSV
        quotes_df = pd.read_csv("quotes.csv")

        # Search in the explanation column for the query
        matches = quotes_df[
            quotes_df["quote_explanation"].str.contains(query, case=False, na=False)
        ]

        if len(matches) > 0:
            return {
                "found": True,
                "count": len(matches),
                "quotes": matches.to_dict("records")[:5],  # Return first 5 matches
            }
        else:
            return {
                "found": False,
                "count": 0,
                "message": f"No quotes found matching '{query}'",
            }
    except FileNotFoundError:
        return {"found": False, "count": 0, "message": "Quotes database file not found"}
    except Exception as e:
        return {
            "found": False,
            "count": 0,
            "message": f"Error searching quotes: {str(e)}",
        }


# Initialize database on import
initialize_inventory()
initialize_cash_balance()
