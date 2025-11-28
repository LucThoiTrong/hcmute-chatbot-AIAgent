from pymongo import MongoClient
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore

from core.config import settings
from infrastructure.ai_connector import get_embeddings


class DatabaseConnector:
    def __init__(self):
        # --- Setup MongoDB ---
        self.mongo_client = MongoClient(settings.MONGO_URI)
        self.mongo_db = self.mongo_client[settings.MONGO_DB_NAME]

        # --- Setup Qdrant Client (Raw) ---
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

        print(f"✅ Database Connected: MongoDB ({settings.MONGO_DB_NAME}) & Qdrant")

# Singleton instance
db = DatabaseConnector()


def get_mongo_db():
    return db.mongo_db


def get_qdrant_client():
    return db.qdrant_client


def get_vector_store() -> QdrantVectorStore:
    vector_store = QdrantVectorStore(
        client=db.qdrant_client,
        collection_name=settings.QDRANT_COLLECTION_NAME,
        embedding=get_embeddings(),
    )
    return vector_store