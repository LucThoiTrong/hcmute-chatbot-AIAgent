from fastapi import FastAPI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from infrastructure.ai_connector import azure_ai_client


class ChatRequest(BaseModel):
    input: str


app = FastAPI()


@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = HumanMessage(content=request.input)

    response = await azure_ai_client.ask(user_input)

    return {"response": response.content}
