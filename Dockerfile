FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app.py .

# Expose port
EXPOSE 7860

# Start FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]