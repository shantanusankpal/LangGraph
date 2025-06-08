from typing import TypedDict
import math
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    name: str
    operation: str
    values: list[int]
    result: int
    isValid: str


def processor(state: AgentState) -> AgentState:
    """This is a method that handles multiple input state"""

    if state["operation"] == "*":
        state["result"] = math.prod(state["values"])
    else:
        state["result"] = sum(state["values"])
    return state


def validator(state: AgentState) -> AgentState:
    if state["result"] > 50:
        state["isValid"] = f"The result is {state['result']}, and it is valid"
    else:
        state["isValid"] = f"The result is {state['result']}, and it is not valid"
    return state


graph = StateGraph(AgentState)
graph.add_node("processing_node", processor)
graph.add_node("validator_node", validator)
graph.set_entry_point("processing_node")
graph.set_finish_point("validator_node")
graph.add_edge("processing_node", "validator_node")
app = graph.compile()

result = app.invoke({"name": "raman", "operation": "*", "values": [1, 2, 3, 4, 5]})

print(result)
