# Docker Execution Instructions for Document Intelligence System

## Quick Start Guide

### 🚀 One-Command Execution (Recommended)

Simply run the PowerShell script to build and execute everything automatically:

```powershell
# Navigate to project directory
cd "g:\IET DAVV\hackethon\adobe\project 1b final\Project-1b-copilot"

# Run with automatic detection (uses input_template.json if available)
.\run_docker.ps1

# Or run specific test cases
.\run_docker.ps1 -TestCase academic
.\run_docker.ps1 -TestCase business  
.\run_docker.ps1 -TestCase student
.\run_docker.ps1 -TestCase forms

# Or run with custom persona/job
.\run_docker.ps1 -Persona "Data Scientist" -Job "Extract key insights from research data"
```

### 📂 Input Setup

The system supports two input methods:

1. **JSON Template Input** (Recommended for hackathon submissions):
   - Edit `input_template.json` with your persona and job requirements
   - Add PDF files to `sample_docs/` directory
   - Run `.\run_docker.ps1` - it will automatically detect and use the JSON

2. **Command Line Input**:
   - Add PDF files to `sample_docs/` directory  
   - Use parameters: `.\run_docker.ps1 -Persona "Your Role" -Job "Your Task"`

### 🔄 Dynamic Usage (No Rebuild Required)

**Key Feature**: You can change inputs without rebuilding the Docker image!

1. **Change Documents**: Simply replace PDF files in `sample_docs/` folder
2. **Change Persona/Job**: Edit `input_template.json` or use different parameters
3. **Re-run**: Execute `.\run_docker.ps1` again - uses existing Docker image

## Building the Docker Image

### 1. Build the Image
```bash
# Manual build (if needed)
docker build -t doc-intelligence .

# Build only (without running)
.\run_docker.ps1 -BuildOnly $true

# Verify image was created
docker images | grep doc-intelligence
```

### 2. Alternative: Build with Custom Tag
```bash
# Build with specific tag for hackathon submission
docker build -t adobe-hackathon-1b:latest .
```

## Manual Docker Commands (Advanced)

### 1. With JSON Input Template
```powershell
# Windows PowerShell - Automatic JSON detection
docker run --rm `
    -v "${PWD}/sample_docs:/app/documents" `
    -v "${PWD}:/app/input" `
    -v "${PWD}/output:/app/output" `
    doc-intelligence

# Linux/Mac - Automatic JSON detection  
docker run --rm \
    -v "$(pwd)/sample_docs:/app/documents" \
    -v "$(pwd):/app/input" \
    -v "$(pwd)/output:/app/output" \
    doc-intelligence
```

### 2. With Command Line Arguments
```powershell
# Windows PowerShell - Custom persona/job
docker run --rm `
    -v "${PWD}/sample_docs:/app/documents" `
    -v "${PWD}/output:/app/output" `
    doc-intelligence `
    python main.py `
    --documents_dir /app/documents `
    --output_dir /app/output `
    --persona "Investment Analyst" `
    --job "Analyze revenue trends and market positioning"

# Linux/Mac - Custom persona/job
docker run --rm \
    -v "$(pwd)/sample_docs:/app/documents" \
    -v "$(pwd)/output:/app/output" \
    doc-intelligence \
    python main.py \
    --documents_dir /app/documents \
    --output_dir /app/output \
    --persona "Investment Analyst" \
    --job "Analyze revenue trends and market positioning"
```

## Hackathon Test Cases

### Test Case 1: Academic Research
```powershell
# Using JSON template (recommended)
# Edit input_template.json to set:
# - persona.role: "PhD Researcher in Computational Biology" 
# - job_to_be_done.task: "Prepare comprehensive literature review..."
.\run_docker.ps1 -TestCase academic

# Or direct command:
.\run_docker.ps1 -Persona "PhD Researcher in Computational Biology" -Job "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
```

### Test Case 2: Business Analysis  
```powershell
# Using predefined test case
.\run_docker.ps1 -TestCase business

# Or direct command:
.\run_docker.ps1 -Persona "Investment Analyst" -Job "Analyze revenue trends, R&D investments, and market positioning strategies"
```

### Test Case 3: Educational Content
```powershell
# Using predefined test case
.\run_docker.ps1 -TestCase student

# Or direct command:
.\run_docker.ps1 -Persona "Undergraduate Chemistry Student" -Job "Identify key concepts and mechanisms for exam preparation on reaction kinetics"
```

### Test Case 4: Forms Management (JSON Template)
```powershell
# This automatically uses the input_template.json provided
.\run_docker.ps1 -TestCase forms
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
