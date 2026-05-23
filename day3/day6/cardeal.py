import os

from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import pandas as pd
import os

path=os.getcwd()
print(path)
# Load datasets
INSURANCE = pd.read_csv(path + r"\day 1_day2\foundational_capabilities\dataset\car_inventory.csv")

cars = pd.read_csv(" car_inventory.csv")
banks = pd.read_csv("car_bank_loan.csv")

# Define shared state
class CarDealState(TypedDict):
    log: List[str]
    selected_car: Optional[str]
    exchange: bool
    negotiated_price: float
    customer_happy: bool
    finance: bool
    selected_bank: Optional[str]
    draft: str

# --- Agents ---
def Agent_CarListing(state: CarDealState) -> CarDealState:
    log = state["log"]
    log.append("Car Listing Agent: showing available cars")
    # (in Streamlit you’d filter cars and let user pick one)
    return {**state, "log": log}

def Agent_Exchange(state: CarDealState) -> CarDealState:
    log = state["log"]
    log.append("Exchange Agent: checking exchange status")
    if state["exchange"]:
        state["negotiated_price"] *= 0.95
        log.append("Applied 5% exchange discount")
    return {**state, "log": log}

def Agent_Negotiation(state: CarDealState) -> CarDealState:
    log = state["log"]
    log.append("Negotiation Agent: handling negotiation rounds")
    # (simulate negotiation logic here)
    return {**state, "log": log}

def Agent_Finance(state: CarDealState) -> CarDealState:
    log = state["log"]
    if state["finance"]:
        log.append(f"Finance Agent: customer chose {state['selected_bank']}")
    return {**state, "log": log}

def Agent_Closure(state: CarDealState) -> CarDealState:
    log = state["log"]
    log.append("Deal Closure Agent: generating draft")
    draft = f"Car: {state['selected_car']}, Final Price: {state['negotiated_price']}, Bank: {state['selected_bank']}"
    return {**state, "draft": draft, "log": log}

# --- Build Graph ---
def BuildGraph():
    g = StateGraph(CarDealState)
    g.add_node("carlisting", Agent_CarListing)
    g.add_node("exchange", Agent_Exchange)
    g.add_node("negotiation", Agent_Negotiation)
    g.add_node("finance", Agent_Finance)
    g.add_node("closure", Agent_Closure)

    g.set_entry_point("carlisting")
    g.add_edge("carlisting", "exchange")
    g.add_edge("exchange", "negotiation")
    g.add_edge("negotiation", "finance")
    g.add_edge("finance", "closure")
    g.add_edge("closure", END)

    return g.compile()

graph = BuildGraph()

# --- Run Example ---
state: CarDealState = {
    "log": [],
    "selected_car": "TO-005",
    "exchange": True,
    "negotiated_price": 23091,
    "customer_happy": True,
    "finance": True,
    "selected_bank": "HDFC Bank",
    "draft": ""
}

result = graph.invoke(state)
print(result["draft"])
print("\n".join(result["log"]))
