"""
Diagram generator for multi-agent system orchestration.
Generates workflow_diagram.png showing agent-to-agent communication.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np


def generate_workflow_diagram(output_file="workflow_diagram.png"):
    """
    Generate a diagram showing multi-agent orchestration and calling patterns.

    Args:
        output_file: Path to save the diagram PNG file
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Define colors for different component types
    color_orchestrator = "#FF6B6B"  # Red
    color_agent = "#4ECDC4"  # Teal
    color_tool = "#FFE66D"  # Yellow
    color_data = "#95E1D3"  # Green
    color_input = "#F38181"  # Pink

    # Title
    ax.text(
        5,
        9.5,
        "Beaver's Choice Paper: Multi-Agent System Architecture",
        fontsize=18,
        fontweight="bold",
        ha="center",
        va="top",
    )

    # ========== INPUT SECTION ==========
    input_box = FancyBboxPatch(
        (0.2, 7.5),
        1.2,
        0.8,
        boxstyle="round,pad=0.1",
        edgecolor="black",
        facecolor=color_input,
        linewidth=2,
    )
    ax.add_patch(input_box)
    ax.text(
        0.8,
        7.9,
        "Customer\nRequest",
        fontsize=10,
        ha="center",
        va="center",
        fontweight="bold",
    )

    # ========== ORCHESTRATOR AGENT (Center) ==========
    orchestrator = FancyBboxPatch(
        (3.5, 6.8),
        2,
        1.2,
        boxstyle="round,pad=0.1",
        edgecolor="black",
        facecolor=color_orchestrator,
        linewidth=3,
    )
    ax.add_patch(orchestrator)
    ax.text(
        4.5,
        7.6,
        "Orchestrator Agent",
        fontsize=12,
        ha="center",
        va="center",
        fontweight="bold",
        color="white",
    )
    ax.text(
        4.5,
        7.2,
        "(Coordinator)",
        fontsize=9,
        ha="center",
        va="center",
        color="white",
        style="italic",
    )

    # ========== WORKER AGENTS (4 corners) ==========
    # Inventory Agent (Top-Left)
    inv_agent = FancyBboxPatch(
        (0.5, 5.5),
        1.8,
        0.9,
        boxstyle="round,pad=0.08",
        edgecolor="black",
        facecolor=color_agent,
        linewidth=2,
    )
    ax.add_patch(inv_agent)
    ax.text(
        1.4,
        6.0,
        "Inventory Agent",
        fontsize=11,
        ha="center",
        va="center",
        fontweight="bold",
        color="white",
    )

    # Quoting Agent (Top-Right)
    quote_agent = FancyBboxPatch(
        (7.7, 5.5),
        1.8,
        0.9,
        boxstyle="round,pad=0.08",
        edgecolor="black",
        facecolor=color_agent,
        linewidth=2,
    )
    ax.add_patch(quote_agent)
    ax.text(
        8.6,
        6.0,
        "Quoting Agent",
        fontsize=11,
        ha="center",
        va="center",
        fontweight="bold",
        color="white",
    )

    # Finance Agent (Bottom-Left)
    fin_agent = FancyBboxPatch(
        (0.5, 3.5),
        1.8,
        0.9,
        boxstyle="round,pad=0.08",
        edgecolor="black",
        facecolor=color_agent,
        linewidth=2,
    )
    ax.add_patch(fin_agent)
    ax.text(
        1.4,
        4.0,
        "Finance Agent",
        fontsize=11,
        ha="center",
        va="center",
        fontweight="bold",
        color="white",
    )

    # Sales Agent (Bottom-Right)
    sales_agent = FancyBboxPatch(
        (7.7, 3.5),
        1.8,
        0.9,
        boxstyle="round,pad=0.08",
        edgecolor="black",
        facecolor=color_agent,
        linewidth=2,
    )
    ax.add_patch(sales_agent)
    ax.text(
        8.6,
        4.0,
        "Sales Agent",
        fontsize=11,
        ha="center",
        va="center",
        fontweight="bold",
        color="white",
    )

    # ========== AGENT TOOLS (Under each agent) ==========
    # Inventory Tools
    inv_tools = FancyBboxPatch(
        (0.2, 2.0),
        2.4,
        1.1,
        boxstyle="round,pad=0.05",
        edgecolor="black",
        facecolor=color_tool,
        linewidth=1.5,
        linestyle="--",
    )
    ax.add_patch(inv_tools)
    ax.text(
        1.4,
        2.95,
        "Tools & Helper Functions:",
        fontsize=9,
        ha="center",
        fontweight="bold",
    )
    ax.text(
        1.4,
        2.55,
        "check_inventory_stock()\n→ get_stock_level()\n\nget_complete_inventory()\n→ get_all_inventory()",
        fontsize=7.5,
        ha="center",
        va="center",
    )

    # Quote Tools
    quote_tools = FancyBboxPatch(
        (7.4, 2.0),
        2.4,
        1.1,
        boxstyle="round,pad=0.05",
        edgecolor="black",
        facecolor=color_tool,
        linewidth=1.5,
        linestyle="--",
    )
    ax.add_patch(quote_tools)
    ax.text(
        8.6,
        2.95,
        "Tools & Helper Functions:",
        fontsize=9,
        ha="center",
        fontweight="bold",
    )
    ax.text(
        8.6,
        2.55,
        "lookup_historical_quotes()\n→ search_quote_history()",
        fontsize=7.5,
        ha="center",
        va="center",
    )

    # Finance Tools
    fin_tools = FancyBboxPatch(
        (0.2, 0.5),
        2.4,
        1.1,
        boxstyle="round,pad=0.05",
        edgecolor="black",
        facecolor=color_tool,
        linewidth=1.5,
        linestyle="--",
    )
    ax.add_patch(fin_tools)
    ax.text(
        1.4,
        1.45,
        "Tools & Helper Functions:",
        fontsize=9,
        ha="center",
        fontweight="bold",
    )
    ax.text(
        1.4,
        1.05,
        "check_company_cash()\n→ get_cash_balance()\n\ngenerate_finance_report()\n→ generate_financial_report()",
        fontsize=7.5,
        ha="center",
        va="center",
    )

    # Sales Tools
    sales_tools = FancyBboxPatch(
        (7.4, 0.5),
        2.4,
        1.1,
        boxstyle="round,pad=0.05",
        edgecolor="black",
        facecolor=color_tool,
        linewidth=1.5,
        linestyle="--",
    )
    ax.add_patch(sales_tools)
    ax.text(
        8.6,
        1.45,
        "Tools & Helper Functions:",
        fontsize=9,
        ha="center",
        fontweight="bold",
    )
    ax.text(
        8.6,
        1.05,
        "record_transaction()\n→ create_transaction()\n\nupdate_inventory_after_sale()\n→ reduce_inventory()",
        fontsize=7.5,
        ha="center",
        va="center",
    )

    # ========== WORKFLOW ARROWS (Orchestrator calling agents) ==========
    # Input to Orchestrator
    arrow1 = FancyArrowPatch(
        (1.4, 7.9),
        (3.5, 7.4),
        arrowstyle="->",
        mutation_scale=25,
        linewidth=2.5,
        color="#FF6B6B",
    )
    ax.add_patch(arrow1)
    ax.text(
        2.4,
        8.0,
        "1",
        fontsize=10,
        ha="center",
        bbox=dict(boxstyle="circle", facecolor="white", edgecolor="black"),
    )

    # Orchestrator to Inventory (with label)
    arrow_orch_inv = FancyArrowPatch(
        (3.8, 6.8),
        (2.0, 6.0),
        arrowstyle="<->",
        mutation_scale=20,
        linewidth=2,
        color="#4ECDC4",
        connectionstyle="arc3,rad=.3",
    )
    ax.add_patch(arrow_orch_inv)
    ax.text(
        2.8,
        7.0,
        "PHASE 1\nInventory Check",
        fontsize=9,
        ha="center",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.7),
    )
    # I/O labels
    ax.text(3.2, 7.3, "↓ requested_items", fontsize=7, ha="left", style="italic")
    ax.text(3.0, 6.5, "↑ can_fulfill", fontsize=7, ha="left", style="italic")

    # Orchestrator to Quoting (with label)
    arrow_orch_quote = FancyArrowPatch(
        (5.2, 6.8),
        (7.7, 6.0),
        arrowstyle="<->",
        mutation_scale=20,
        linewidth=2,
        color="#4ECDC4",
        connectionstyle="arc3,rad=-.3",
    )
    ax.add_patch(arrow_orch_quote)
    ax.text(
        6.8,
        7.0,
        "PHASE 2\nGenerate Quote",
        fontsize=9,
        ha="center",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.7),
    )
    # I/O labels
    ax.text(6.2, 7.3, "↓ items, request", fontsize=7, ha="right", style="italic")
    ax.text(7.0, 6.5, "↑ quote_amt", fontsize=7, ha="right", style="italic")

    # Orchestrator to Finance (with label)
    arrow_orch_fin = FancyArrowPatch(
        (3.8, 6.8),
        (2.0, 4.4),
        arrowstyle="<->",
        mutation_scale=20,
        linewidth=2,
        color="#4ECDC4",
        connectionstyle="arc3,rad=.3",
    )
    ax.add_patch(arrow_orch_fin)
    ax.text(
        2.8,
        5.3,
        "PHASE 3\nFinance Check",
        fontsize=9,
        ha="center",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.7),
    )
    # I/O labels
    ax.text(3.2, 5.8, "↓ quote_amt", fontsize=7, ha="left", style="italic")
    ax.text(3.0, 4.9, "↑ approved", fontsize=7, ha="left", style="italic")

    # Orchestrator to Sales (with label)
    arrow_orch_sales = FancyArrowPatch(
        (5.2, 6.8),
        (7.7, 4.4),
        arrowstyle="<->",
        mutation_scale=20,
        linewidth=2,
        color="#4ECDC4",
        connectionstyle="arc3,rad=-.3",
    )
    ax.add_patch(arrow_orch_sales)
    ax.text(
        6.8,
        5.3,
        "PHASE 4\nRecord Sales",
        fontsize=9,
        ha="center",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.7),
    )
    # I/O labels
    ax.text(6.2, 5.8, "↓ order_id, items", fontsize=7, ha="right", style="italic")
    ax.text(7.0, 4.9, "↑ success", fontsize=7, ha="right", style="italic")

    # Agents to their Tools (downward arrows)
    for agent_pos, tool_y in [(1.4, 3.1), (8.6, 3.1), (1.4, 1.6), (8.6, 1.6)]:
        arrow = FancyArrowPatch(
            (agent_pos, tool_y + 0.2),
            (agent_pos, tool_y),
            arrowstyle="->",
            mutation_scale=15,
            linewidth=1.5,
            color="gray",
            linestyle=":",
        )
        ax.add_patch(arrow)

    # ========== DATABASE COMPONENT ==========
    db_box = FancyBboxPatch(
        (4, 0.5),
        2,
        1,
        boxstyle="round,pad=0.1",
        edgecolor="black",
        facecolor=color_data,
        linewidth=2,
        linestyle=":",
    )
    ax.add_patch(db_box)
    ax.text(
        5,
        1.1,
        "SQLite Database",
        fontsize=11,
        ha="center",
        va="center",
        fontweight="bold",
    )
    ax.text(
        5,
        0.75,
        "(Inventory, Transactions,\nFinancial Records)",
        fontsize=8,
        ha="center",
        va="center",
        style="italic",
    )

    # Connections to Database from tools and agents
    for x_pos in [1.4, 8.6]:
        arrow_db = FancyArrowPatch(
            (x_pos, 2.3),
            (5, 1.5),
            arrowstyle="<->",
            mutation_scale=15,
            linewidth=1.5,
            color="gray",
            linestyle=":",
            alpha=0.6,
        )
        ax.add_patch(arrow_db)

    # ========== LEGEND ==========
    legend_x, legend_y = 0.2, 0.1
    ax.text(legend_x, legend_y + 0.25, "Legend:", fontsize=10, fontweight="bold")

    # Legend items
    orchestrator_patch = mpatches.Patch(
        facecolor=color_orchestrator, edgecolor="black", label="Orchestrator"
    )
    agent_patch = mpatches.Patch(
        facecolor=color_agent, edgecolor="black", label="Worker Agent"
    )
    tool_patch = mpatches.Patch(
        facecolor=color_tool, edgecolor="black", label="Agent Tools"
    )
    data_patch = mpatches.Patch(
        facecolor=color_data, edgecolor="black", label="Data Component"
    )

    ax.legend(
        handles=[orchestrator_patch, agent_patch, tool_patch, data_patch],
        loc="lower right",
        fontsize=9,
        ncol=1,
    )

    # Add workflow description
    description = (
        "Workflow Sequence:\n"
        "1. Customer request arrives\n"
        "2. Orchestrator parses and extracts items\n"
        "3. Phase 1: Inventory Agent checks stock availability\n"
        "4. Phase 2: Quoting Agent generates price quote\n"
        "5. Phase 3: Finance Agent verifies funds\n"
        "6. Phase 4: Sales Agent records transaction\n"
        "7. Result: Order status with quote (if approved)"
    )
    ax.text(
        5,
        -0.5,
        description,
        fontsize=8,
        ha="center",
        va="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"[OK] Workflow diagram generated: {output_file}")
    plt.close()


if __name__ == "__main__":
    generate_workflow_diagram()
