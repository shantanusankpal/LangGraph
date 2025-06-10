from urllib import response
from langchain_core import messages
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")


class AgentState(TypedDict):
    messages: list[Union[HumanMessage, AIMessage]]


def process(state: AgentState) -> AgentState:
    """This method will invoke llm to get response to user query"""
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print(f"\nAI : {response.content}")
    return state


graph_compile = StateGraph(AgentState)
graph_compile.add_node("process", process)
graph_compile.add_edge(START, "process")
graph_compile.add_edge("process", END)

agent = graph_compile.compile()

conversation_history = []

user_input = input("Enter Your Query: ")
while user_input != "exit":
    conversation_history.append(HumanMessage(content=user_input))
    result = agent.invoke({"messages": conversation_history})
    conversation_history = result["messages"]
    user_input = input("Enter Your Query: ")
