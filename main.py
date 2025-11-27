import sys
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from agent.graph import workflow


class ChatRequest(BaseModel):
    input: str


app = FastAPI()


@app.post("/chat")
async def stream_chat(request: ChatRequest):
    user_input = {"messages": [HumanMessage(content=request.input)]}

    async def event_generator():
        async for event in workflow.astream_events(user_input, version="v1"):
            if event["event"] == "on_chat_model_stream":
                chunk_content = event["data"]["chunk"].content
                if chunk_content:
                    sys.stdout.write(chunk_content)
                    sys.stdout.flush()

                    yield chunk_content

    # Giữ nguyên header này
    return StreamingResponse(event_generator(), media_type="text/plain")