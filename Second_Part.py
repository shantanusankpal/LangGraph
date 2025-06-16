import os
from operator import add as add_messages
from typing import Annotated, Sequence, TypedDict

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph

load_dotenv()

llm_non_tool = ChatOpenAI(model="gpt-4o")

embeddings_my = OpenAIEmbeddings(model="text-embedding-3-small")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

pdfLoader = PyMuPDFLoader("./information.pdf")
pdf = pdfLoader.load()

data_split = text_splitter.split_documents(pdf)

if not os.path.exists("./chromaStore"):
    os.mkdir("./chromaStore")

vectorstore = Chroma.from_documents(
    data_split,
    embeddings_my,
    collection_name="Second_try",
    persist_directory="./chromaStore",
)

retriver = vectorstore.as_retriever(search_type="similarity")


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def retriver_tool(query: str) -> str:
    """This tool retrives relevenat context from vector database"""
    print("\n\nTool Called.\n\n")
    docs = retriver.get_relevant_documents(query=query)
    if not docs:
        return "I found no relevent context documents"
    result = []
    i = 1
    for doc in docs:
        result.append(f"{i}.{doc.page_content}")
        i += 1
    return "\n\n".join(result)


mytools = [retriver_tool]
llm = llm_non_tool.bind_tools(mytools)


def llm_chat(state: AgentState) -> AgentState:
    """This method calls llm model based on human query"""
    systemMessage = SystemMessage(
        content="You are a helpfull AI assitant that responds to the User propmpts in a witty way. You are very witty."
    )
    messages = list(state["messages"])
    messages = [systemMessage] + messages
    message = llm.invoke(messages)
    return {"messages": [message]}


def should_countinue_conditional_edge(state: AgentState):
    print("\n\n Determining Conditional Edge \n\n")
    messages = state["messages"]
    ai_message = messages[-1]
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, state: AgentState):
        messages = state["messages"]
        if not messages:
            raise ValueError("No message found in input")
        message = messages[-1]
        print("\n\n Calling Tools \n\n")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"].get("query", "")
            )
            outputs.append(
                ToolMessage(
                    content=str(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}


graph = StateGraph(AgentState)
tool_node = BasicToolNode(tools=mytools)
graph.add_node("node_tools", tool_node)
graph.add_node("llm", llm_chat)
graph.add_edge(START, "llm")
graph.add_edge("node_tools", "llm")
graph.add_conditional_edges(
    "llm",
    should_countinue_conditional_edge,
    {"tools": "node_tools", END: END},
)

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
        #        print(airesponse)
        print(airesponse["messages"][-1].content)
        messages.append(AIMessage(content=airesponse["messages"][-1].content))


running_agent()
