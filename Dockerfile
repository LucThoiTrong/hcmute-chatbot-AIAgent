FROM python:3.10-slim

WORKDIR /app

# Copy file thư viện trước để tận dụng cache
COPY requirements.txt .

# Cài đặt thư viện
# --no-cache-dir: Không lưu cache bộ cài, giảm dung lượng image
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mở cổng 8000
EXPOSE 8000

# Lệnh chạy app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]