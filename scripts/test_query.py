import sys
import json
from pathlib import Path

# Thêm đường dẫn root để import được modules trong project
sys.path.append(str(Path(__file__).resolve().parent.parent))

from tools.database_tool import get_collection_schema_tool, query_database_tool


def run_test():
    target_collection = "accounts"  # Bạn có thể đổi thành 'courses' hay 'accounts' tuỳ ý

    print(f"🚀 Bắt đầu test với bảng: {target_collection}")
    print("=" * 60)

    # --- TEST 1: Lấy Schema (Cấu trúc bảng) ---
    print(f"1️⃣  Testing: get_collection_schema_tool cho '{target_collection}'")
    try:
        # Gọi tool
        res_schema = get_collection_schema_tool.invoke({
            "collection_name": target_collection
        })
        print("👉 KẾT QUẢ SCHEMA:")
        print(res_schema)
    except Exception as e:
        print(f"❌ Lỗi schema: {e}")

    print("\n" + "=" * 60)

    # --- TEST 2: Query dữ liệu (Lấy 5 dòng đầu tiên) ---
    print(f"2️⃣  Testing: query_database_tool (Select All limit 5)")

    # Giả lập input của AI: query_json phải là chuỗi String, không phải Dict
    # "{}" nghĩa là lấy tất cả (tương đương SELECT * trong SQL)
    query_input = json.dumps({})

    try:
        res_query = query_database_tool.invoke({
            "collection_name": target_collection,
            "query_json": query_input
        })
        print("👉 KẾT QUẢ QUERY:")
        # Format lại JSON in ra cho đẹp dễ nhìn
        try:
            parsed = json.loads(res_query)
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except:
            print(res_query)  # Nếu kết quả là thông báo lỗi string thì in thẳng ra

    except Exception as e:
        print(f"❌ Lỗi query: {e}")


if __name__ == "__main__":
    run_test()