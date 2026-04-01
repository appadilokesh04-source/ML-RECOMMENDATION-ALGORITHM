FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ✅ Fix — set PYTHONPATH so Python finds app.data module
ENV PYTHONPATH=/app

# Train models at build time
RUN python -c "
from app.ml.hybrid import HybridEngine
engine = HybridEngine()
engine.train()
print('Models trained and saved!')
"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]