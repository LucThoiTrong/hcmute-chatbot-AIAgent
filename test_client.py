import requests
import sys

url = "http://127.0.0.1:8000/chat"
data = {"input": "Hãy viết cho tui 3 đoạn văn mô tả mùa thu (Mỗi đoạn 100 từ)"}

print(f"--- Đang kết nối tới {url} ---")

# stream=True là mấu chốt để client nhận dữ liệu từng chút một
with requests.post(url, json=data, stream=True) as response:
    if response.status_code == 200:
        print("--- Bắt đầu nhận stream ---\n")
        for chunk in response.iter_content(chunk_size=None):
            if chunk:
                # Decode bytes sang string và in ngay lập tức
                text = chunk.decode('utf-8')
                sys.stdout.write(text)
                sys.stdout.flush() # Ép hiển thị ngay lập tức
        print("\n\n--- Kết thúc stream ---")
    else:
        print(f"Lỗi: {response.status_code}")
        print(response.text)