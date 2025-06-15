from operator import add as add_messages
from typing import Annotated, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def llm_chat(state: AgentState) -> AgentState:
    """This method calls llm model based on human query"""
    systemMessage = SystemMessage(
        content="You are a helpfull AI assitant that responds to the User propmpts in a witty way. You are very witty."
    )
    messages = list(state["messages"])
    messages = [systemMessage] + messages
    message = llm.invoke(messages)
    return {"messages": [message]}


graph = StateGraph(AgentState)

graph.add_node("llm", llm_chat)
graph.add_edge(START, "llm")
graph.add_edge("llm", END)


agent = graph.compile()

messages = []


def running_agent():
    print("====Talking to your smart AI assistant=====")
    global messages
    while True:
        user_input = input("What is your question?")
        if user_input == "exit":
            break
        messages.append(HumanMessage(content=user_input))
        airesponse = agent.invoke({"messages": messages})
        print(airesponse)
        messages.append(AIMessage(content=airesponse["messages"][-1].content))


running_agent()
