from typing import List, Annotated, Dict, Any

from langgraph.checkpoint.mongodb import MongoDBSaver
from typing_extensions import TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from core.config import settings
from infrastructure.ai_connector import get_llm
from .prompts import get_system_message
from infrastructure.db_connector import get_mongo_client

# Import Tools
from tools.search_tool import lookup_knowledge_base
from tools.database_tool import get_mongo_tools, list_collections_tool


# --- 1. ĐỊNH NGHĨA STATE ---
class AgentState(TypedDict):
    # 'add_messages' giúp tự động nối tin nhắn mới vào lịch sử cũ
    messages: Annotated[List[BaseMessage], add_messages]
    # Lưu thông tin user (role, id, name) để dùng xuyên suốt session
    user_info: Dict[str, Any]


# --- 2. CHUẨN BỊ TOOLS ---
# Gộp tool Qdrant và bộ tool MongoDB
tools = [lookup_knowledge_base] + get_mongo_tools()
tool_node = ToolNode(tools)


# --- 3. LOGIC NODE "AGENT" ---
async def call_model(state: AgentState, config: RunnableConfig):
    """
    Node chính xử lý logic của AI
    """
    # 1. Lấy thông tin từ State
    messages = state["messages"]
    user_info = state.get("user_info", {})

    # 2. Lấy thông tin sơ bộ về Database để nạp vào Context
    try:
        mongo_summary = list_collections_tool.invoke({})
    except Exception:
        mongo_summary = "Không thể lấy danh sách bảng."

    # 3. Tạo System Message động dựa trên User Info
    sys_msg = get_system_message(
        user_info=user_info,
        mongo_collections_summary=mongo_summary,
        qdrant_collections_summary="Chứa quy chế đào tạo, sổ tay sinh viên, và các văn bản hướng dẫn."
    )

    # 4. Khởi tạo LLM và Bind Tools
    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)

    # 5. Gọi Model
    response = await llm_with_tools.ainvoke([sys_msg] + messages)

    # Trả về tin nhắn mới để cập nhật vào State
    return {"messages": [response]}


# --- 4. XÂY DỰNG GRAPH ---
builder = StateGraph(AgentState)

# Thêm các Nodes
builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)

# Định nghĩa luồng (Edges)
builder.add_edge(START, "agent")

# Logic rẽ nhánh (Conditional Edge):
# - Nếu AI trả về tool_calls -> đi qua node "tools"
# - Nếu AI trả về text thường -> đi tới END
builder.add_conditional_edges(
    "agent",
    tools_condition,
)

# Từ tool quay lại agent để AI đọc kết quả và trả lời user
builder.add_edge("tools", "agent")

# --- 5. TÍCH HỢP PERSISTENCE (BỘ NHỚ) ---
# Checkpointer giúp lưu lại state dựa trên thread_id
client = get_mongo_client()
memory = MongoDBSaver(client=client, db_name=settings.MONGO_DB_NAME)

# Compile Graph
graph = builder.compile(checkpointer=memory)