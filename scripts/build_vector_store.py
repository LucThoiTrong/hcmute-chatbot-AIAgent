import sys
import os
import glob
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import VectorParams, Distance

# Import từ hạ tầng
from core.config import settings
from infrastructure.db_connector import get_qdrant_client, get_vector_store
from infrastructure.ai_connector import get_embeddings

# Cấu hình đường dẫn dữ liệu
DATA_FOLDER = r"E:\NCKH_TLCN_KLTN\Data"


def import_documents():
    print(f"📂 Đang quét dữ liệu từ folder: {DATA_FOLDER}")

    # --- BƯỚC 1: LOAD VÀ SPLIT DATA ---
    docx_files = glob.glob(os.path.join(DATA_FOLDER, "*.docx"))

    if not docx_files:
        print("❌ Không tìm thấy file .docx nào!")
        return

    print(f"🔎 Tìm thấy {len(docx_files)} files.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    all_chunks = []

    for file_path in docx_files:
        file_name = os.path.basename(file_path)
        print(f"   -> Processing: {file_name}...")

        try:
            loader = Docx2txtLoader(file_path)
            documents = loader.load()

            chunks = text_splitter.split_documents(documents)

            # Gán metadata để truy xuất nguồn gốc sau này
            for chunk in chunks:
                chunk.metadata["source"] = file_name
                all_chunks.append(chunk)

        except Exception as e:
            print(f"⚠️ Lỗi khi đọc file {file_name}: {e}")

    if not all_chunks:
        print("⚠️ Không có dữ liệu nào để import.")
        return

    print(f"📦 Tổng cộng đã tạo ra {len(all_chunks)} chunks dữ liệu.")

    # --- BƯỚC 2: CHUẨN BỊ COLLECTION (Dùng Raw Client) ---
    # Mục đích: Đảm bảo Collection tồn tại với đúng cấu hình trước khi LangChain đẩy data vào
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME

    # Lấy kích thước vector mẫu từ model Azure
    embeddings_model = get_embeddings()
    sample_embedding = embeddings_model.embed_query("test")
    vector_size = len(sample_embedding)

    if not client.collection_exists(collection_name):
        print(f"🆕 Tạo mới Collection '{collection_name}' (size={vector_size}, distance=Cosine)...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    else:
        print(f"ℹ️ Collection '{collection_name}' đã tồn tại. Sẵn sàng ghi thêm dữ liệu.")

    # --- BƯỚC 3: EMBED VÀ STORE (Dùng LangChain Vector Store) ---
    print("🚀 Bắt đầu Embedding và Upload lên Qdrant thông qua LangChain...")

    try:
        vector_store = get_vector_store()

        # Hàm này làm tất cả: Embed -> Tạo ID -> Batching -> Upsert
        # Nó trả về list các ID đã lưu thành công
        ids = vector_store.add_documents(documents=all_chunks)

        print(f"✅ Hoàn tất! Đã lưu thành công {len(ids)} vectors vào Qdrant.")

    except Exception as e:
        print(f"❌ Lỗi trong quá trình lưu vector: {e}")


if __name__ == "__main__":
    import_documents()
