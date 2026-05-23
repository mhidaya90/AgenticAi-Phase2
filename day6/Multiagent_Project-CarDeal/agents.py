from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import pandas as pd
from utils import generate_pdf

cars = pd.read_csv("car_inventory.csv")
banks = pd.read_csv("car_bank_loan.csv")

class CarDealState(TypedDict):
    log: List[str]
    prompt: str
    selected_car: Optional[str]
    exchange: bool
    negotiated_price: float
    neg_rounds: int
    customer_happy: bool
    finance: bool
    selected_bank: Optional[str]
    draft: str
    pdf_bytes: bytes

def Agent_CarListing(state: CarDealState) -> CarDealState:
    log = state["log"]
    log.append(f"CarListingAgent: filtering cars for prompt '{state['prompt']}'")

    if state["selected_car"]:
        car = cars[cars['id'] == state['selected_car']].iloc[0]
        log.append(
            f"CarListingAgent: user selected {car['make']} {car['model']} ({car['year']}) "
            f"ID={car['id']} Price={car['price']}"
        )
        log.append("CarListingAgent: car list disabled after selection, exchange option enabled")
    else:
        log.append("CarListingAgent: no car selected yet")

    return {**state, "log": log}

def Agent_Exchange(state: CarDealState) -> CarDealState:
    log = state["log"]
    if state["exchange"]:
        log.append("ExchangeAgent: exchange selected, will apply 5% discount later")
    else:
        log.append("ExchangeAgent: no exchange selected")
    return {**state, "log": log}

def Agent_Negotiation(state: CarDealState) -> CarDealState:
    log = state["log"]
    if state["neg_rounds"] > 0:
        log.append(f"NegotiationAgent: round {state['neg_rounds']} completed, current price {state['negotiated_price']}")
    if state["customer_happy"]:
        log.append("NegotiationAgent: customer accepted price")
    elif state["neg_rounds"] >= 3:
        log.append("NegotiationAgent: max rounds reached, customer not satisfied")
    return {**state, "log": log}

def Agent_Finance(state: CarDealState) -> CarDealState:
    log = state["log"]
    if state["finance"]:
        log.append(f"FinanceAgent: customer chose {state['selected_bank']}")
    else:
        log.append("FinanceAgent: no finance selected")
    return {**state, "log": log}

def Agent_Closure(state: CarDealState) -> CarDealState:
    log = state["log"]
    car_details = cars[cars['id'] == state['selected_car']].iloc[0].to_dict()
    bank_info = None
    if state["finance"] and state["selected_bank"]:
        bank_info = banks[banks['bank_name'] == state['selected_bank']].iloc[0].to_dict()

    final_price = state["negotiated_price"]
    if state["exchange"]:
        final_price *= 0.95

    pdf_bytes = generate_pdf(car_details, final_price, state["exchange"], state["finance"], bank_info)
    draft = f"Car: {state['selected_car']} | Final Price: {final_price} | Bank: {state['selected_bank']}"
    log.append("ClosureAgent: generated deal draft and PDF")

    return {**state, "draft": draft, "pdf_bytes": pdf_bytes, "log": log}

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
