from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    number1: int
    operation: str
    number2: int
    number3: int
    number4: int
    operation2: str
    finalNumber: int
    finalNumber2: int


def routrer2(state: AgentState) -> AgentState:
    if state["operation"] == "+":
        return "addition_operation2"
    else:
        return "substraction_operation2"


def routrer1(state: AgentState) -> AgentState:
    if state["operation"] == "+":
        return "addition_operation1"
    else:
        return "substraction_operation1"


def substraction_node2(state: AgentState) -> AgentState:
    state["finalNumber2"] = state["number3"] - state["number4"]
    return state


def substraction_node1(state: AgentState) -> AgentState:
    state["finalNumber"] = state["number1"] - state["number2"]
    return state


def addition_node2(state: AgentState) -> AgentState:
    state["finalNumber2"] = state["number3"] + state["number4"]
    return state


def addition_node1(state: AgentState) -> AgentState:
    state["finalNumber"] = state["number1"] + state["number2"]
    return state


graph = StateGraph(AgentState)


graph.add_node("add_node", addition_node1)
graph.add_node("add_node2", addition_node2)
graph.add_node("substraction_node", substraction_node1)
graph.add_node("substraction_node2", substraction_node2)
graph.add_node("router", lambda state: state)
graph.add_node("router2", lambda state: state)

graph.add_edge(START, "router")
graph.add_edge("add_node2", END)
graph.add_edge("substraction_node2", END)
graph.add_edge("substraction_node", "router2")
graph.add_edge("add_node", "router2")


graph.add_conditional_edges(
    "router2",
    routrer2,
    {
        "addition_operation2": "add_node2",
        "substraction_operation2": "substraction_node2",
    },
)

graph.add_conditional_edges(
    "router",
    routrer1,
    {"addition_operation1": "add_node", "substraction_operation1": "substraction_node"},
)


app = graph.compile()


result = app.invoke(
    {
        "number1": 10,
        "number2": 5,
        "operation": "-",
        "operation2": "+",
        "number3": 7,
        "number4": 2,
        "finalNumber": 0,
        "finalNumber2": 0,
    }
)

print(result)
