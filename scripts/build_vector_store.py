import sys
import os
import glob
import uuid
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from langchain_community.document_loaders import Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client.models import PointStruct, VectorParams, Distance

# Import các module hạ tầng đã xây dựng
from core.config import settings
from infrastructure.db_connector import get_qdrant_client
from infrastructure.ai_connector import get_embeddings

# Cấu hình đường dẫn dữ liệu
DATA_FOLDER = r"E:\NCKH_TLCN_KLTN\Data"


def import_documents():
    print(f"📂 Đang quét dữ liệu từ folder: {DATA_FOLDER}")

    # 1. Tìm tất cả file .docx trong thư mục
    docx_files = glob.glob(os.path.join(DATA_FOLDER, "*.docx"))

    if not docx_files:
        print("❌ Không tìm thấy file .docx nào!")
        return

    print(f"🔎 Tìm thấy {len(docx_files)} files.")

    # 2. Load và Split text
    # Splitter giúp chia văn bản dài thành đoạn nhỏ (khoảng 1000 ký tự), chồng lấn 200 ký tự để giữ ngữ cảnh
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    all_chunks = []

    for file_path in docx_files:
        file_name = os.path.basename(file_path)
        print(f"   -> Processing: {file_name}...")

        try:
            # Python equivalent của DocxLoader
            loader = Docx2txtLoader(file_path)
            documents = loader.load()

            # Cắt nhỏ văn bản
            chunks = text_splitter.split_documents(documents)

            # Thêm metadata (tên file) để sau này biết nguồn trích dẫn
            for chunk in chunks:
                chunk.metadata["source"] = file_name
                all_chunks.append(chunk)

        except Exception as e:
            print(f"⚠️ Lỗi khi đọc file {file_name}: {e}")

    print(f"📦 Tổng cộng đã tạo ra {len(all_chunks)} chunks dữ liệu.")

    # 3. Kết nối & Embed
    client = get_qdrant_client()
    embeddings_model = get_embeddings()
    collection_name = settings.QDRANT_COLLECTION_NAME

    # Kiểm tra kích thước vector
    sample_embedding = embeddings_model.embed_query("test")
    vector_size = len(sample_embedding)

    # Tạo collection nếu chưa có
    if not client.collection_exists(collection_name):
        print(f"🆕 Tạo mới Collection '{collection_name}' (size={vector_size})...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    # 4. Upload lên Qdrant (Batching để chạy nhanh hơn)
    print("🚀 Bắt đầu Embedding và Upload lên Qdrant...")

    batch_size = 50  # Xử lý 50 đoạn một lúc
    points = []

    for i, chunk in enumerate(all_chunks):
        # Embed nội dung
        vector = embeddings_model.embed_query(chunk.page_content)

        # Tạo payload (dữ liệu lưu trữ)
        payload = {
            "content": chunk.page_content,
            "source": chunk.metadata.get("source"),
            "chunk_index": i
        }

        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=payload
        ))

        # Nếu đủ batch hoặc là phần tử cuối cùng thì upload
        if len(points) >= batch_size or i == len(all_chunks) - 1:
            client.upsert(
                collection_name=collection_name,
                points=points,
                wait=True
            )
            print(f"   Đã upload {len(points)} chunks...")
            points = []  # Reset batch

    print("✅ Hoàn tất quá trình nhập dữ liệu!")


if __name__ == "__main__":
    import_documents()
