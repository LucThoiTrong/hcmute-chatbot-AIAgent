from pymongo import MongoClient
from qdrant_client import QdrantClient
from core.config import settings


class DatabaseConnector:
    def __init__(self):
        # --- Setup MongoDB ---
        # Lấy trực tiếp từ settings đã load
        self.mongo_client = MongoClient(settings.MONGO_URI)
        self.mongo_db = self.mongo_client[settings.MONGO_DB_NAME]

        # --- Setup Qdrant ---
        self.qdrant_client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

        print(f"✅ Database Connected: MongoDB ({settings.MONGO_DB_NAME}) & Qdrant")


# Singleton instance
# Instance này sẽ được tạo 1 lần duy nhất khi chương trình chạy
db = DatabaseConnector()


def get_mongo_db():
    """Trả về database object của MongoDB để các tool khác query"""
    return db.mongo_db


def get_qdrant_client():
    """Trả về client của Qdrant để thực hiện vector search"""
    return db.qdrant_client
