FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create directories
RUN mkdir -p /app/uploads /app/chroma_db

# Expose port
EXPOSE 6789

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6789"]