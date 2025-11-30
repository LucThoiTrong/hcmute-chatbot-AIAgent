import json
from langchain_core.tools import tool
from infrastructure.db_connector import get_mongo_db


# Helper để convert type của Python sang tên type dễ đọc cho AI
def get_type_name(value):
    return type(value).__name__


# --- 1. Tool: Liệt kê bảng kèm số lượng record ---
@tool
def list_collections_tool():
    """
    Liệt kê tên các bảng (collections) và số lượng bản ghi (documents).
    Hữu ích để biết bảng nào chứa dữ liệu chính.
    """
    try:
        db = get_mongo_db()
        collections_info = []
        names = db.list_collection_names()

        # Danh sách các từ khóa cần ẩn đi (Bảng hệ thống & LangGraph)
        ignored_keywords = ["system.", "checkpoint", "writes", "blobs"]

        for name in names:
            # Nếu tên bảng chứa bất kỳ từ khóa nào bên trên -> Bỏ qua
            if any(keyword in name for keyword in ignored_keywords):
                continue

            count = db[name].estimated_document_count()
            collections_info.append(f"{name} (count: {count})")

        return "Danh sách bảng:\n" + "\n".join(collections_info)
    except Exception as e:
        return f"Lỗi: {e}"


# --- 2. Tool: Lấy Schema kèm Data Type ---
@tool
def get_collection_schema_tool(collection_name: str):
    """
    Quét 50 documents gần nhất để tổng hợp toàn bộ các trường (fields) có thể có.
    Giúp AI biết chính xác tên trường và kiểu dữ liệu kể cả các trường ít xuất hiện.
    """
    try:
        db = get_mongo_db()
        collection = db[collection_name]

        # 1. Lấy 50 documents mới nhất để quét
        # Dùng sort DESCENDING để ưu tiên dữ liệu mới
        cursor = collection.find().sort([('_id', -1)]).limit(50)

        schema_map = {}
        sample_doc = None

        count = 0
        for doc in cursor:
            if sample_doc is None:
                sample_doc = doc  # Giữ lại 1 bản ghi làm mẫu

            # Quét từng trường trong document này
            for key, value in doc.items():
                # Nếu trường này chưa có trong map, thêm vào
                if key not in schema_map:
                    schema_map[key] = type(value).__name__
                # (Nâng cao) Có thể check nếu 1 trường có nhiều kiểu dữ liệu khác nhau
            count += 1

        if count == 0:
            return f"Bảng '{collection_name}' rỗng."

        # Convert sample thành JSON
        sample_json = json.dumps(sample_doc, default=str, ensure_ascii=False)

        return (
            f"Đã quét {count} documents gần nhất của bảng '{collection_name}'.\n"
            f"Tổng hợp Schema (Tên trường: Kiểu dữ liệu):\n"
            f"{json.dumps(schema_map, indent=2)}\n\n"
            f"Ví dụ 1 document đầy đủ nhất:\n{sample_json}"
        )

    except Exception as e:
        return f"Lỗi lấy schema bảng '{collection_name}': {e}"


# --- 3. Tool: Truy vấn nâng cao (Filter + Projection + Sort) ---
@tool
def query_database_tool(collection_name: str, query_json: str, projection_json: str = None, sort_json: str = None):
    """
    Thực thi truy vấn MongoDB (find).
    - collection_name: Tên bảng.
    - query_json: JSON điều kiện lọc (VD: '{"age": {"$gt": 20}}').
    - projection_json (Optional): JSON chọn trường cần lấy để tiết kiệm token (VD: '{"name": 1, "email": 1}').
      Nếu muốn lấy hết thì bỏ qua hoặc để 'None'.
    - sort_json (Optional): JSON sắp xếp (VD: '{"created_at": -1}' để lấy mới nhất).
    """
    try:
        print(f"DEBUG - AI Querying Collection: {collection_name}")
        print(f"DEBUG - Query JSON: {query_json}")

        db = get_mongo_db()

        # 1. Parse Query
        try:
            query_dict = json.loads(query_json) if query_json else {}
        except:
            return "Lỗi: query_json không phải JSON hợp lệ."

        # 2. Parse Projection (quan trọng để tiết kiệm token)
        projection_dict = None
        if projection_json and projection_json.lower() != "none":
            try:
                projection_dict = json.loads(projection_json)
            except:
                pass  # Nếu lỗi projection thì cứ lấy hết, không crash

        # 3. Parse Sort
        sort_list = []
        if sort_json and sort_json.lower() != "none":
            try:
                sort_dict = json.loads(sort_json)
                for k, v in sort_dict.items():
                    sort_list.append((k, int(v)))  # v là 1 hoặc -1
            except:
                pass

        # Thực thi
        cursor = db[collection_name].find(query_dict, projection_dict)

        if sort_list:
            cursor = cursor.sort(sort_list)

        # Giới hạn 5 - 10 kết quả
        results = list(cursor.limit(5))

        if not results:
            return "Không tìm thấy dữ liệu nào."

        return json.dumps(results, default=str, ensure_ascii=False)

    except Exception as e:
        return f"Lỗi database: {e}"


# --- 4. Tool: Aggregation ---
# Tool này dành cho các câu hỏi: "Đếm số lượng sinh viên...", "Tính tổng..."
@tool
def aggregate_database_tool(collection_name: str, pipeline_json: str):
    """
    Chạy Aggregation Pipeline của MongoDB để thống kê, gom nhóm dữ liệu.
    - pipeline_json: List JSON chứa các stage (VD: '[{"$match": ...}, {"$group": ...}]')
    """
    try:
        db = get_mongo_db()
        pipeline = json.loads(pipeline_json)

        results = list(db[collection_name].aggregate(pipeline))
        return json.dumps(results, default=str, ensure_ascii=False)
    except Exception as e:
        return f"Lỗi Aggregation: {e}"


def get_mongo_tools():
    return [list_collections_tool, get_collection_schema_tool, query_database_tool, aggregate_database_tool]
