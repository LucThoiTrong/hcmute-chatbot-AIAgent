from typing import List
from langchain_core.tools import tool

from infrastructure.db_connector import get_vector_store


def search_dense(query: str, k: int = 5) -> List[dict]:
    """
    Thực hiện tìm kiếm ngữ nghĩa (Dense Search) trong Qdrant.

    Args:
        query: Câu hỏi hoặc từ khóa tìm kiếm.
        k: Số lượng kết quả trả về (mặc định 5).

    Returns:
        List các dict chứa nội dung và metadata.
    """
    # 1. Lấy Vector Store từ cấu hình đã duyệt
    vector_store = get_vector_store()

    # 2. Thực hiện tìm kiếm
    # Mặc định khi có 'embedding' thì QdrantVectorStore chạy ở chế độ DENSE.
    # similarity_search_with_score trả về (Document, score)
    results = vector_store.similarity_search_with_score(
        query=query,
        k=k
    )

    # 3. Chuẩn hóa kết quả trả về cho dễ đọc
    parsed_results = []
    for doc, score in results:
        parsed_results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Unknown"),
            "score": score  # Độ tương đồng (0 đến 1)
        })

    return parsed_results


# --- ĐÓNG GÓI THÀNH TOOL CHO AI AGENT ---

@tool
def lookup_knowledge_base(query: str):
    """
    Sử dụng công cụ này để tra cứu thông tin về trường Đại học Sư phạm Kỹ thuật (HCMUTE),
    quy chế đào tạo, thông tin sinh viên, hoặc các tài liệu chuyên ngành đã được học.
    Đầu vào là câu hỏi cụ thể của người dùng.
    """
    results = search_dense(query, k=3)

    if not results:
        return "Xin lỗi, không tìm thấy thông tin liên quan trong cơ sở dữ liệu."

    # Format dạng chuỗi văn bản để LLM đọc hiểu
    response_text = ""
    for i, item in enumerate(results, 1):
        response_text += f"\n[Tài liệu {i} - Nguồn: {item['source']} - Độ khớp: {item['score']:.2f}]:\n"
        response_text += f"{item['content']}\n"
        response_text += "-" * 30

    return response_text