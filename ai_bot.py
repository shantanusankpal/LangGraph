from langchain_core import messages
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


# Use api_key explicitly or rely on environment variable
class AgentState(TypedDict):
    messages: list[HumanMessage]


llm = ChatOpenAI(model="gpt-4o")


def process(state: AgentState) -> AgentState:
    response = llm.invoke(state["messages"])
    print(response.content)
    return state


graph_compile = StateGraph(AgentState)
graph_compile.add_node("process", process)
graph_compile.add_edge(START, "process")
graph_compile.add_edge("process", END)

agent = graph_compile.compile()

user_input = input("Enter Your Query: ")
while user_input != "exit":
    agent.invoke({"messages": [HumanMessage(content=user_input)]})
    user_input = input("Enter Your Query: ")
