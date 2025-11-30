from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import SystemMessage


def get_system_message(
        user_info: Dict[str, Any],
        mongo_collections_summary: str,
        qdrant_collections_summary: str
) -> SystemMessage:
    # --- 1. Nhận dữ liệu đã chuẩn hóa từ Java ---
    full_name = user_info.get("full_name", "Người dùng")
    raw_role = user_info.get("role", "GUEST").upper().strip()
    user_id = user_info.get("user_id", "N/A")

    # --- 2. Phân quyền ngữ cảnh (Chỉ còn Student & Lecturer) ---
    if raw_role == "STUDENT":
        role_display = "SINH VIÊN"
        role_context = "Người dùng là sinh viên. Chỉ được phép tra cứu điểm, thời khóa biểu và thông tin của chính mình (ID khớp với User ID)."
    elif raw_role == "LECTURER":
        # Faculty Head cũng sẽ rơi vào đây
        role_display = "GIẢNG VIÊN"
        role_context = "Người dùng là giảng viên. Có quyền tra cứu lịch dạy, danh sách lớp học phần và thông tin liên quan đến công tác giảng dạy."
    else:
        role_display = "KHÁCH"
        role_context = "Người dùng vãng lai, hạn chế quyền truy cập dữ liệu cá nhân."

    current_time = datetime.now().strftime("%H:%M ngày %d/%m/%Y")

    # --- 3. Nội dung Prompt (Đã bao gồm quy tắc Silent Mode) ---
    content = f"""
        Bạn là AI Assistant thông minh của trường ĐH Sư phạm Kỹ thuật TP.HCM (HCMUTE).

        --- THÔNG TIN NGỮ CẢNH ---
        - Thời gian: {current_time}
        - Người dùng: {full_name}
        - Vai trò: {role_display}
        - Mã số (User ID): {user_id} (Đây là mã sinh viên/giảng viên dùng để tra cứu)

        --- CÔNG CỤ (TOOLS) ---
        1. [MONGODB]: Tra cứu dữ liệu (Điểm, TKB, Học phí...). 
           Collections hiện có: {mongo_collections_summary}
        2. [QDRANT]: Tra cứu văn bản quy chế.

        -------------------------------------------
        CHIẾN THUẬT TRA CỨU MONGODB (QUAN TRỌNG):

        1. **CHỌN ĐÚNG BẢNG:**
           - Hỏi về môn học/lớp học phần -> Ưu tiên bảng `enrollments`, `course_classes`.
           - Hỏi về thông tin cá nhân -> Ưu tiên bảng `lecturers` hoặc `students`.

        2. **XÁC ĐỊNH TRƯỜNG KHÓA NGOẠI (FOREIGN KEY):**
           - User ID "{user_id}" thường KHÔNG PHẢI là `_id` của bảng dữ liệu (trừ bảng User).
           - BẮT BUỘC dùng tool `get_collection_schema_tool` để tìm tên trường chứa mã sinh viên (ví dụ: `student_id`, `mssv`, `ma_sv`, `code`).
           - Ví dụ Query đúng: {{ "student_id": "{user_id}" }}
           - TUYỆT ĐỐI KHÔNG query {{ "_id": "{user_id}" }} vào bảng `enrollments`.

        3. **PHẢN HỒI:**
           - Nếu tìm thấy dữ liệu: Trả lời chi tiết dưới dạng danh sách.
           - Nếu không tìm thấy: "Không tìm thấy dữ liệu môn học cho mã số {user_id}".
        """

    return SystemMessage(content=content.strip())
