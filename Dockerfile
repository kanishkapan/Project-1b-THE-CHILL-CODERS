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

# Copy application code (excluding input directories to allow dynamic mounting)
COPY src/ ./src/
COPY main.py .
COPY *.md ./
COPY challenge1b_output.json ./
COPY test_content.txt ./

# Create directories for input/output
RUN mkdir -p /app/documents /app/output /app/input

# Set environment variables
ENV PYTHONPATH=/app
ENV MODEL_CACHE_DIR=/app/models

# Expose volumes for documents and input template
VOLUME ["/app/documents", "/app/input", "/app/output"]

# Default command - check for input_template.json first, then fallback to command args
CMD ["sh", "-c", "if [ -f /app/input/input_template.json ]; then python main.py --input_json /app/input/input_template.json --documents_dir /app/documents --output_dir /app/output; else python main.py --documents_dir /app/documents --output_dir /app/output --persona 'PhD Researcher' --job 'Comprehensive analysis of document content'; fi"]
