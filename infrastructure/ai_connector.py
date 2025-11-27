from functools import lru_cache
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from core.config import settings


@lru_cache(maxsize=1)
def get_llm() -> AzureChatOpenAI:
    llm = AzureChatOpenAI(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        api_key=settings.AZURE_OPENAI_API_KEY,
        temperature=0.7,
        timeout=60,
        streaming=True,
    )

    return llm


@lru_cache(maxsize=1)
def get_embeddings() -> AzureOpenAIEmbeddings:
    """
    Trả về model Embedding để chuyển text thành vector (dùng cho RAG).
    """
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_deployment=settings.AZURE_EMBEDDING_DEPLOYMENT_NAME,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        api_key=settings.AZURE_OPENAI_API_KEY,
    )

    return embeddings