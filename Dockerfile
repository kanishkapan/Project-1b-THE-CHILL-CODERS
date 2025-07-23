FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create directories for input/output
RUN mkdir -p /app/documents /app/output

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_CACHE_DIR=/app/models

# Expose volume for documents
VOLUME ["/app/documents"]

# Default command
CMD ["python", "main.py", "--documents_dir", "/app/documents", "--output_dir", "/app/output", "--persona", "PhD Researcher", "--job", "Comprehensive analysis of document content"]
