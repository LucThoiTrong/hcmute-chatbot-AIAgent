from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Xác định đường dẫn tuyệt đối từ thư mục gốc của project.
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Nhóm AzureOpenAI
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str
    AZURE_EMBEDDING_DEPLOYMENT_NAME: str
    AZURE_OPENAI_API_VERSION: str

    # MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str

    # Qdrant
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_NAME: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )


settings = Settings()
