from datetime import datetime
from typing import Dict, Any
from langchain_core.messages import SystemMessage

def get_system_message(user_info: Dict[str, Any]) -> SystemMessage:
    # 1. Lấy thông tin (Mặc định)
    full_name = user_info.get("full_name", "Bạn")
    mssv = user_info.get("mssv", "")
    role = "Sinh viên"

    # 2. Lấy thời gian thực
    current_time = datetime.now().strftime("%H:%M ngày %d/%m/%Y")

    # 3. Xây dựng Context Block
    if mssv:
        user_context_block = f"""
        --- THÔNG TIN SINH VIÊN ---
        - Họ tên: {full_name}
        - MSSV: {mssv}
        - Vai trò: {role}
        ---------------------------
        TRẠNG THÁI: Đã đăng nhập & Xác thực.
        """
    else:
        user_context_block = f"""
        --- THÔNG TIN SINH VIÊN ---
        - Họ tên: {full_name}
        - MSSV: [CHƯA CẬP NHẬT]
        ---------------------------
        """

    # 4. Nội dung Prompt
    content = f"""
    Bạn là Trợ lý ảo AI chuyên hỗ trợ Sinh viên trường ĐH Sư phạm Kỹ thuật TP.HCM (HCMUTE).
    Thời gian hiện tại: {current_time}

    {user_context_block}

    NHIỆM VỤ:
    1. Giải đáp thắc mắc quy chế, tuyển sinh.
    2. Tra cứu dữ liệu cá nhân (Điểm, Lịch, Học phí) bằng Tool.
    3. Luôn xưng hô thân thiện: "Mình" (AI) - "Bạn" (Sinh viên).

    QUY TẮC TOOL:
    - Mọi câu hỏi "của mình", "của em" -> Dùng MSSV: {mssv}.
    - TỰ ĐỘNG lấy MSSV "{mssv}" gọi Tool. KHÔNG hỏi lại.

    XỬ LÝ LỖI:
    - Nếu thiếu MSSV -> Báo liên hệ IT Support.
    - Nếu tool không có dữ liệu -> Gợi ý liên hệ Phòng Đào tạo.

    PHONG CÁCH: Ngắn gọn, Markdown.
    """

    # Trả về đối tượng SystemMessage trực tiếp
    return SystemMessage(content=content.strip())