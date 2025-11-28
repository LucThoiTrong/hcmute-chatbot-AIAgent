import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from tools.search_tool import search_dense, lookup_knowledge_base


def run_test():
    # --- CẤU HÌNH CÂU HỎI TEST ---
    # Hãy thay đổi câu này bằng một nội dung có thật trong tài liệu bạn đã upload
    query = "Điểm tiếng anh đầu ra"

    print(f"🚀 Đang bắt đầu kiểm tra hệ thống tìm kiếm...")
    print(f"🔎 Câu hỏi test: '{query}'")
    print("=" * 60)

    # ---------------------------------------------------------
    # TEST 1: Kiểm tra hàm Search Raw (Dùng để debug dữ liệu)
    # ---------------------------------------------------------
    print("\n[TEST 1] Kết quả từ hàm 'search_dense' (Raw Data):")
    try:
        raw_results = search_dense(query, k=6)

        if not raw_results:
            print("❌ Không tìm thấy kết quả nào! (Check lại DB hoặc keyword)")
        else:
            for i, item in enumerate(raw_results, 1):
                print(f"  📄 Document #{i}")
                print(f"     • Score  : {item['score']:.4f}")  # Điểm càng gần 1 càng giống
                print(f"     • Source : {item['source']}")
                print("     " + "-" * 20)

    except Exception as e:
        print(f"❌ Lỗi khi chạy search_dense: {e}")

    print("\n" + "=" * 60)

    # ---------------------------------------------------------
    # TEST 2: Kiểm tra Tool Agent (Dùng để xem AI sẽ đọc gì)
    # ---------------------------------------------------------
    print("\n[TEST 2] Kết quả từ Tool 'lookup_knowledge_base' (Agent View):")
    try:
        # Tool trong LangChain được gọi thông qua phương thức .invoke()
        agent_response = lookup_knowledge_base.invoke(query)

        print("🤖 Đây là nội dung text mà LLM sẽ nhận được:")
        print("-" * 30)
        print(agent_response)
        print("-" * 30)

    except Exception as e:
        print(f"❌ Lỗi khi chạy tool: {e}")


if __name__ == "__main__":
    run_test()