# Docker Execution Instructions for Document Intelligence System

## Building the Docker Image

### 1. Build the Image
```bash
# Navigate to project directory
cd "g:\IET DAVV\hackethon\adobe\Project 1b-copilot"

# Build the Docker image
docker build -t doc-intelligence .

# Verify image was created
docker images | grep doc-intelligence
```

### 2. Alternative: Build with Custom Tag
```bash
# Build with specific tag for hackathon submission
docker build -t adobe-hackathon-1b:latest .
```

## Running the Docker Container

### 1. Basic Run (Default Persona)
```bash
# Run with default settings
docker run --rm -v "$(pwd)/sample_docs:/app/documents" -v "$(pwd)/output:/app/output" doc-intelligence

# For Windows PowerShell
docker run --rm -v "${PWD}/sample_docs:/app/documents" -v "${PWD}/output:/app/output" doc-intelligence
```

### 2. Custom Persona and Job
```bash
# Academic Research Example
docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence \
  python main.py \
  --documents_dir /app/documents \
  --output_dir /app/output \
  --persona "PhD Researcher in Computational Biology" \
  --job "Prepare comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"

# Business Analysis Example  
docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence \
  python main.py \
  --documents_dir /app/documents \
  --output_dir /app/output \
  --persona "Investment Analyst" \
  --job "Analyze revenue trends, R&D investments, and market positioning strategies"

# Educational Content Example
docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence \
  python main.py \
  --documents_dir /app/documents \
  --output_dir /app/output \
  --persona "Undergraduate Chemistry Student" \
  --job "Identify key concepts and mechanisms for exam preparation on reaction kinetics"
```

### 3. Interactive Mode (for Testing)
```bash
# Run container interactively
docker run -it --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence bash

# Inside container, you can run:
python main.py --documents_dir /app/documents --persona "Your Persona" --job "Your Job"
python test_system.py
python demo.py
```

## Testing the Docker System

### 1. Prepare Test Documents
```bash
# Create test documents directory
mkdir -p sample_docs

# Add your PDF files to sample_docs/
# Example structure:
# sample_docs/
# ├── research_paper_1.pdf
# ├── business_report_2023.pdf
# ├── technical_documentation.pdf
# └── educational_content.pdf
```

### 2. Run System Tests
```bash
# Test with multiple documents
docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence \
  python test_system.py

# Test with demo script
docker run -it --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence \
  python demo.py
```

### 3. Verify Output
```bash
# Check generated output files
ls -la output/
cat output/results.json

# Verify constraint compliance
# - Processing time < 60 seconds ✓
# - CPU-only execution ✓  
# - No internet access ✓
# - Model size < 1GB ✓
```

## Hackathon Submission Commands

### Test Case 1: Academic Research
```bash
docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence \
  python main.py \
  --documents_dir /app/documents \
  --output_dir /app/output \
  --output_file "test_case_1_results.json" \
  --persona "PhD Researcher in Computational Biology" \
  --job "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
```

### Test Case 2: Business Analysis  
```bash
docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence \
  python main.py \
  --documents_dir /app/documents \
  --output_dir /app/output \
  --output_file "test_case_2_results.json" \
  --persona "Investment Analyst" \
  --job "Analyze revenue trends, R&D investments, and market positioning strategies"
```

### Test Case 3: Educational Content
```bash
docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence \
  python main.py \
  --documents_dir /app/documents \
  --output_dir /app/output \
  --output_file "test_case_3_results.json" \
  --persona "Undergraduate Chemistry Student" \
  --job "Identify key concepts and mechanisms for exam preparation on reaction kinetics"
```

## Performance Monitoring

### 1. Monitor Resource Usage
```bash
# Monitor CPU and memory usage during execution
docker stats

# Run with resource limits (hackathon constraints)
docker run --rm \
  --memory=1g \
  --cpus=1.0 \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence
```

### 2. Timing Tests
```bash
# Time the execution
time docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  doc-intelligence
```

## Troubleshooting

### Common Issues

1. **No PDF files found:**
   ```bash
   # Ensure PDFs are in sample_docs directory
   ls sample_docs/*.pdf
   ```

2. **Permission issues:**
   ```bash
   # Fix directory permissions
   chmod -R 755 sample_docs output
   ```

3. **Memory issues:**
   ```bash
   # Run with memory limit
   docker run --memory=1g --rm ...
   ```

4. **Slow performance:**
   ```bash
   # Check if running too many documents
   # System optimized for 3-10 documents
   ```

### Debug Mode
```bash
# Run with verbose logging
docker run --rm \
  -v "$(pwd)/sample_docs:/app/documents" \
  -v "$(pwd)/output:/app/output" \
  -e PYTHONPATH=/app \
  doc-intelligence \
  python -u main.py --documents_dir /app/documents --persona "Debug Test" --job "System testing"
```

## Output Verification

After running, check these files:
- `output/results.json` - Main output file
- `output/` directory - Contains all generated files
- Console output shows:
  - Processing time (should be < 60s)
  - Number of documents processed
  - Relevance scores and rankings
  - Constraint compliance status

## Hackathon Submission Checklist

✅ **Docker image builds successfully**
✅ **Runs without internet access**  
✅ **Processes 3-10 PDFs under 60 seconds**
✅ **Uses less than 1GB memory**
✅ **CPU-only execution**
✅ **Generates challenge1b_output.json format**
✅ **Handles diverse document types**
✅ **Works with different personas and jobs**
