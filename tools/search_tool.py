from typing import List
from langchain_core.tools import tool
from infrastructure.db_connector import get_vector_store


# --- 1. Helper Function: Tìm kiếm Vector ---
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


# --- 2. Tool: AI Agent Interface (Đã nâng cấp) ---
@tool
def lookup_knowledge_base(query: str):
    """
    Sử dụng công cụ này để tra cứu thông tin về trường Đại học Sư phạm Kỹ thuật (HCMUTE),
    quy chế đào tạo, thông tin sinh viên, hoặc các tài liệu chuyên ngành đã được học.
    Đầu vào là câu hỏi cụ thể của người dùng.
    """
    try:
        # Ngưỡng lọc
        threshold = 0.5

        # 1. Tìm kiếm lấy top 5 nội dung tìm được
        raw_results = search_dense(query, k=5)

        # 2. Lọc bỏ các kết quả có điểm số thấp (Rác / Không liên quan)
        valid_results = []
        for item in raw_results:
            if item['score'] >= threshold:
                valid_results.append(item)

        # 3. Kiểm tra nếu không còn kết quả nào sau khi lọc
        if not valid_results:
            return "Xin lỗi, không tìm thấy thông tin đủ độ tin cậy trong tài liệu nội bộ."

        # 4. Chỉ lấy Top 3 kết quả tốt nhất để gửi cho LLM.
        final_results = valid_results[:3]

        # 5. Format dạng chuỗi văn bản để LLM đọc hiểu
        response_text = f"Tìm thấy {len(final_results)} tài liệu phù hợp (Ngưỡng > {threshold}):\n"

        for i, item in enumerate(final_results, 1):
            response_text += f"\n[Tài liệu {i} | Nguồn: {item['source']} | Độ khớp: {item['score']:.2f}]\n"
            response_text += f"Nội dung: {item['content']}\n"
            response_text += "-" * 30

        return response_text

    except Exception as e:
        # Bắt lỗi để Agent không bị crash giữa chừng
        return f"Lỗi hệ thống tìm kiếm (Vector Search Error): {str(e)}"
