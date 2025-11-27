import json
from langchain_core.tools import tool, StructuredTool
from infrastructure.db_connector import get_mongo_db


# --- 1. Tool: Liệt kê danh sách bảng (Collections) ---
@tool
def list_collections_tool():
    """
    Liệt kê tên các bảng (collections) có trong cơ sở dữ liệu MongoDB.
    Dùng tool này đầu tiên để biết hệ thống có dữ liệu gì.
    """
    try:
        db = get_mongo_db()
        # Lấy danh sách, loại bỏ các bảng hệ thống
        collections = [name for name in db.list_collection_names() if not name.startswith("system.")]
        return f"Các bảng hiện có: {', '.join(collections)}"
    except Exception as e:
        return f"Lỗi khi lấy danh sách bảng: {e}"


# --- 2. Tool: Xem cấu trúc bảng (Schema) ---
@tool
def get_collection_schema_tool(collection_name: str):
    """
    Lấy thông tin cấu trúc (các trường/fields) và dữ liệu mẫu của một bảng cụ thể.
    Đầu vào: Tên bảng (ví dụ: 'students', 'tuition').
    """
    try:
        db = get_mongo_db()
        # Lấy mẫu 1 document để phân tích cấu trúc
        sample = db[collection_name].find_one()

        if not sample:
            return f"Bảng '{collection_name}' hiện đang rỗng."

        # Trả về danh sách keys để AI biết cách query
        keys = list(sample.keys())

        # --- FIX LỖI DATETIME TẠI ĐÂY ---
        # Thêm default=str để tự động convert datetime, ObjectId thành string
        sample_json = json.dumps(sample, default=str, ensure_ascii=False)

        return f"Cấu trúc bảng '{collection_name}':\n- Các trường (fields): {keys}\n- Ví dụ dữ liệu: {sample_json}"
    except Exception as e:
        return f"Lỗi khi lấy schema bảng '{collection_name}': {e}"


# --- 3. Tool: Thực thi truy vấn (Query) ---
@tool
def query_database_tool(collection_name: str, query_json: str):
    """
    Thực thi truy vấn tìm kiếm dữ liệu trong MongoDB.
    Đầu vào:
    - collection_name: Tên bảng cần tìm.
    - query_json: Chuỗi JSON chứa điều kiện lọc (MQL). Ví dụ: '{"student_id": "20110394"}' hoặc '{}' để lấy tất cả.
    """
    try:
        db = get_mongo_db()

        # Parse chuỗi JSON thành Dict
        try:
            query_dict = json.loads(query_json)
        except:
            return "Lỗi cú pháp JSON trong query. Hãy đảm bảo query là chuỗi JSON hợp lệ."

        # Thực thi query
        # Giới hạn 5 kết quả để tránh tràn context window
        cursor = db[collection_name].find(query_dict).limit(5)

        results = []
        for doc in cursor:
            # Không cần convert thủ công _id nữa vì default=str sẽ lo hết
            results.append(doc)

        if not results:
            return "Không tìm thấy dữ liệu nào phù hợp với điều kiện."

        # --- FIX LỖI DATETIME TẠI ĐÂY ---
        return json.dumps(results, default=str, ensure_ascii=False)

    except Exception as e:
        return f"Lỗi database: {e}"


# --- Hàm tập hợp (dùng để bind vào Agent) ---
def get_mongo_tools():
    return [list_collections_tool, get_collection_schema_tool, query_database_tool]


# --- Test nhanh ---
if __name__ == "__main__":
    print("Test list collections:", list_collections_tool.invoke({}))