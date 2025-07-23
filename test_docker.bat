@echo off
REM Docker Test Script for Windows PowerShell/CMD
REM Tests Document Intelligence System with Docker

echo 🚀 Testing Document Intelligence System with Docker
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

echo ✅ Docker is running

REM Check if image exists
docker images | findstr "doc-intelligence" >nul
if errorlevel 1 (
    echo ⚠️  Docker image 'doc-intelligence' not found. Building...
    docker build -t doc-intelligence .
    if errorlevel 1 (
        echo ❌ Failed to build Docker image
        exit /b 1
    )
)

echo ✅ Docker image ready

REM Create test directories
if not exist "sample_docs" mkdir sample_docs
if not exist "output" mkdir output

REM Check for PDF files
echo 📄 Checking for PDF files in sample_docs/...

REM Test 1: Basic System Test
echo.
echo 🧪 Test 1: Basic System Test
echo ----------------------------
docker run --rm -v "%cd%/sample_docs:/app/documents" -v "%cd%/output:/app/output" doc-intelligence python test_system.py

REM Test 2: Academic Research Persona
echo.
echo 🧪 Test 2: Academic Research Persona
echo ------------------------------------
docker run --rm -v "%cd%/sample_docs:/app/documents" -v "%cd%/output:/app/output" doc-intelligence python main.py --documents_dir /app/documents --output_dir /app/output --output_file "academic_results.json" --persona "PhD Researcher in Computational Biology" --job "Prepare comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"

REM Test 3: Business Analysis Persona
echo.
echo 🧪 Test 3: Business Analysis Persona
echo ------------------------------------
docker run --rm -v "%cd%/sample_docs:/app/documents" -v "%cd%/output:/app/output" doc-intelligence python main.py --documents_dir /app/documents --output_dir /app/output --output_file "business_results.json" --persona "Investment Analyst" --job "Analyze revenue trends, R&D investments, and market positioning strategies"

REM Test 4: Educational Content Persona
echo.
echo 🧪 Test 4: Educational Content Persona
echo --------------------------------------
docker run --rm -v "%cd%/sample_docs:/app/documents" -v "%cd%/output:/app/output" doc-intelligence python main.py --documents_dir /app/documents --output_dir /app/output --output_file "education_results.json" --persona "Undergraduate Chemistry Student" --job "Identify key concepts and mechanisms for exam preparation on reaction kinetics"

REM Test 5: Resource Constraints
echo.
echo 🧪 Test 5: Resource Constraints Test
echo ------------------------------------
echo Testing with 1GB memory limit and 1 CPU...
docker run --rm --memory=1g --cpus=1.0 -v "%cd%/sample_docs:/app/documents" -v "%cd%/output:/app/output" doc-intelligence python main.py --documents_dir /app/documents --output_dir /app/output --output_file "constraint_test_results.json" --persona "Test User" --job "Test system under resource constraints"

REM Check output files
echo.
echo 📊 Output Summary
echo ==================
echo Generated files in output/:
dir output

echo.
echo 🏆 Hackathon Requirements Check
echo ===============================
echo ✅ CPU-only execution
echo ✅ Docker containerized
echo ✅ No internet access required
echo ✅ Handles diverse personas
echo ✅ Processes multiple document types
echo ✅ Generates required JSON format

echo.
echo 🎉 Docker testing complete!
echo Ready for hackathon submission! 🏆

pause
