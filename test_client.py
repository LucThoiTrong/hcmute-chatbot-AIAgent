import requests
import sys

# URL của FastAPI Server
url = "http://127.0.0.1:8000/chat"

# --- CẤU HÌNH HARDCODE (Cố định) ---
# Giả lập thông tin Session và User như yêu cầu
THREAD_ID = "test_session_fixed_01"
USER_INFO_MOCK = {
    "full_name": "Lục Thới Trọng",
    "role": "ROLE_STUDENT",
    "user_id": "22110254",
}

print(f"--- KẾT NỐI TỚI AI SERVER: {url} ---")
print(f"--- User: {USER_INFO_MOCK['full_name']} ({USER_INFO_MOCK['role']}) ---")
print("Gõ 'quit' hoặc 'exit' để thoát.\n")

while True:
    # 1. Nhập liệu từ người dùng (Dynamic Input)
    try:
        user_input = input("User: ")
    except EOFError:
        break

    if user_input.lower() in ["quit", "exit"]:
        print("--- Kết thúc phiên chat ---")
        break

    if not user_input.strip():
        continue

    # 2. Tạo Payload gửi đi
    payload = {
        "input": user_input,  # Nội dung chat thay đổi
        "thread_id": THREAD_ID,  # Session cố định
        "user_info": USER_INFO_MOCK  # User Info cố định
    }

    # 3. Gửi Request và Stream phản hồi
    print("Bot: ", end="")
    try:
        with requests.post(url, json=payload, stream=True) as response:
            if response.status_code == 200:
                # Nhận từng chunk và in ra ngay lập tức
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        text = chunk.decode('utf-8')
                        sys.stdout.write(text)
                        sys.stdout.flush()
                print("")  # Xuống dòng khi kết thúc câu trả lời
            else:
                print(f"\n[Lỗi Server]: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"\n[Lỗi Kết Nối]: {e}")

    print("-" * 30)
