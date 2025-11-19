import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

class AzureAIClient:
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.7,
            timeout=60,
        )

    async def ask(self, message):
        return await self.llm.ainvoke([message])


azure_ai_client = AzureAIClient()
