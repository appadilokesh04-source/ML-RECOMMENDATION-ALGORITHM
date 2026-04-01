# Base image — Python 3.11 slim (smaller size)
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for scikit-surprise
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker caches this layer)
# If requirements don't change, Docker skips reinstalling
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to run when container starts
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]