from typing import List, Annotated, Dict, Any
from langchain_core.messages import BaseMessage
from langgraph.constants import START, END
from langgraph.graph import StateGraph, add_messages
from typing_extensions import TypedDict

from infrastructure.ai_connector import get_llm


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


async def call_model(state: AgentState) -> Dict[str, Any]:
    user_input = state["messages"]

    llm = get_llm()

    response = await llm.ainvoke(user_input)

    return {"messages": [response]}


builder = StateGraph(state_schema=AgentState)
builder.add_node("agent", call_model)

builder.add_edge(START, "agent")
builder.add_edge("agent", END)

workflow = builder.compile()
