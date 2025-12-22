FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mở cổng 8000 cho AI Agent
EXPOSE 8000

# Lệnh chạy duy nhất để khởi động FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]