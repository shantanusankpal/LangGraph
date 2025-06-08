from typing import TypedDict
import math
from langgraph.graph import StateGraph


class AgentState(TypedDict):
    name: str
    operation: str
    values: list[int]
    result: str


def processor(state: AgentState) -> AgentState:
    """This is a method that handles multiple input state"""

    if state["operation"] == "*":
        state["result"] = (
            f"Hello {state['name']} your result is {math.prod(state['values'])}"
        )
    else:
        state["result"] = f"Hello {state['name']} your result is {sum(state['values'])}"
    return state


graph = StateGraph(AgentState)
graph.add_node("processing_node", processor)
graph.set_entry_point("processing_node")
graph.set_finish_point("processing_node")
app = graph.compile()

result = app.invoke({"name": "raman", "operation": "+", "values": [1, 2, 3, 4]})

print(result)
