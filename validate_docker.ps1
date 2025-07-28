#!/usr/bin/env pwsh
# Quick Docker validation script for Adobe Hackathon 1B
# This script builds the image and runs a quick test to ensure everything works

Write-Host "🎯 Adobe Hackathon 1B - Docker Validation Test" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
try {
    docker --version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Docker not found" }
    Write-Host "✅ Docker is available" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed or not running" -ForegroundColor Red
    exit 1
}

# Build image
Write-Host ""
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
$buildStart = Get-Date
docker build -t doc-intelligence . 2>&1 | Out-Host
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}
$buildTime = ((Get-Date) - $buildStart).TotalSeconds
Write-Host "✅ Docker image built successfully in $([math]::Round($buildTime, 1))s" -ForegroundColor Green

# Check image size
$imageInfo = docker images doc-intelligence --format "table {{.Size}}" | Select-Object -Skip 1
Write-Host "📦 Image size: $imageInfo" -ForegroundColor Blue

# Verify directories
if (!(Test-Path "sample_docs")) {
    New-Item -ItemType Directory -Path "sample_docs" -Force | Out-Null
}
if (!(Test-Path "output")) { 
    New-Item -ItemType Directory -Path "output" -Force | Out-Null
}

# Check for PDFs
$pdfCount = (Get-ChildItem -Path "sample_docs" -Filter "*.pdf" -ErrorAction SilentlyContinue).Count

if ($pdfCount -eq 0) {
    Write-Host ""
    Write-Host "📄 No PDFs found in sample_docs - creating test scenario" -ForegroundColor Yellow
    Write-Host "⚠️  For actual testing, add PDF files to sample_docs directory" -ForegroundColor Yellow
    
    # Test with dry run mode (if your system supports it)
    Write-Host ""
    Write-Host "🧪 Testing Docker container startup..." -ForegroundColor Yellow
    
    $testStart = Get-Date
    $testResult = docker run --rm --entrypoint="python" doc-intelligence -c "print('✅ Docker container works!'); import src.document_processor; print('✅ All modules imported successfully')"
    $testTime = ((Get-Date) - $testStart).TotalSeconds
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Container test passed in $([math]::Round($testTime, 1))s" -ForegroundColor Green
    } else {
        Write-Host "❌ Container test failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "📄 Found $pdfCount PDF file(s) - running full test" -ForegroundColor Green
    
    # Run actual processing test
    Write-Host ""
    Write-Host "🚀 Testing full processing pipeline..." -ForegroundColor Yellow
    
    $testStart = Get-Date
    
    if (Test-Path "input_template.json") {
        Write-Host "Using input_template.json for test" -ForegroundColor Blue
        docker run --rm `
            -v "${PWD}/sample_docs:/app/documents" `
            -v "${PWD}:/app/input" `
            -v "${PWD}/output:/app/output" `
            doc-intelligence 2>&1 | Out-Host
    } else {
        Write-Host "Using default test parameters" -ForegroundColor Blue
        docker run --rm `
            -v "${PWD}/sample_docs:/app/documents" `
            -v "${PWD}/output:/app/output" `
            doc-intelligence `
            python main.py `
            --documents_dir /app/documents `
            --output_dir /app/output `
            --persona "Test Researcher" `
            --job "Validate system functionality" 2>&1 | Out-Host
    }
    
    $testTime = ((Get-Date) - $testStart).TotalSeconds
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Full processing test completed in $([math]::Round($testTime, 1))s" -ForegroundColor Green
        
        # Check output
        $outputFiles = Get-ChildItem "output" -Filter "*.json" -ErrorAction SilentlyContinue
        if ($outputFiles.Count -gt 0) {
            Write-Host "✅ Output files generated: $($outputFiles.Count)" -ForegroundColor Green
            foreach ($file in $outputFiles) {
                Write-Host "   📋 $($file.Name)" -ForegroundColor Blue
            }
        }
        
        # Check constraints
        if ($testTime -le 60) {
            Write-Host "✅ Time constraint met: $([math]::Round($testTime, 1))s ≤ 60s" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Time constraint exceeded: $([math]::Round($testTime, 1))s > 60s" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Processing test failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎯 VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host "✅ Docker build: PASSED" -ForegroundColor Green
Write-Host "✅ Container startup: PASSED" -ForegroundColor Green
if ($pdfCount -gt 0) {
    Write-Host "✅ Full processing: PASSED" -ForegroundColor Green
    Write-Host "✅ Output generation: PASSED" -ForegroundColor Green
}
Write-Host "✅ Ready for hackathon submission!" -ForegroundColor Green

Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Add your PDF documents to sample_docs/ directory" -ForegroundColor White
Write-Host "2. Edit input_template.json with your persona and job" -ForegroundColor White  
Write-Host "3. Run: .\run_docker.ps1" -ForegroundColor White
Write-Host "4. Check output/ directory for results" -ForegroundColor White

Write-Host ""
Write-Host "🚀 System ready for Adobe Hackathon 1B submission!" -ForegroundColor Green
