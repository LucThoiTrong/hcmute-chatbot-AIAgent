import uvicorn
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from agent.graph import graph


# --- ĐỊNH NGHĨA REQUEST BODY ---
class ChatRequest(BaseModel):
    input: str
    thread_id: str = "default_thread"
    user_info: Dict[str, Any]


app = FastAPI()


@app.post("/chat")
async def stream_chat(request: ChatRequest):
    # 1. Chuẩn bị input cho Graph
    # Map dữ liệu từ Request của Client vào State của Graph
    inputs = {
        "messages": [HumanMessage(content=request.input)],
        "user_info": request.user_info
    }

    # 2. Cấu hình thread_id cho bộ nhớ (MongoDB)
    config = {"configurable": {"thread_id": request.thread_id}}

    async def event_generator():
        # Dùng astream_events để bắt mọi sự kiện trong graph
        async for event in graph.astream_events(inputs, config=config, version="v1"):

            # Lọc sự kiện: Chỉ lấy lúc Model đang sinh text (stream)
            if event["event"] == "on_chat_model_stream":
                # Lấy nội dung chunk
                chunk = event["data"]["chunk"]

                # Kiểm tra và yield nội dung
                if chunk.content:
                    yield chunk.content

    return StreamingResponse(event_generator(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
