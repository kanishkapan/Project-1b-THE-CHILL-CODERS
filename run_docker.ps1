#!/usr/bin/env pwsh
# PowerShell script for running the Document Intelligence System via Docker
# Supports both JSON input template and direct command-line arguments

param(
    [string]$BuildOnly = $false,
    [string]$Persona = "",
    [string]$Job = "",
    [string]$UseJson = $true,
    [string]$TestCase = ""
)

# Colors for output
$Green = "`e[92m"
$Red = "`e[91m"
$Yellow = "`e[93m"
$Blue = "`e[94m"
$Reset = "`e[0m"

Write-Host "${Blue}=== Adobe Hackathon 1B - Document Intelligence System ===${Reset}" -ForegroundColor Cyan
Write-Host "${Blue}Theme: Connect What Matters — For the User Who Matters${Reset}" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not found"
    }
} catch {
    Write-Host "${Red}❌ Docker is not installed or not running${Reset}" -ForegroundColor Red
    Write-Host "Please install Docker and ensure it's running" -ForegroundColor Red
    exit 1
}

# Build Docker image
Write-Host "${Yellow}🔨 Building Docker image...${Reset}" -ForegroundColor Yellow
$buildResult = docker build -t doc-intelligence .
if ($LASTEXITCODE -ne 0) {
    Write-Host "${Red}❌ Docker build failed${Reset}" -ForegroundColor Red
    exit 1
}
Write-Host "${Green}✅ Docker image built successfully${Reset}" -ForegroundColor Green

# If only building, exit here
if ($BuildOnly -eq $true) {
    Write-Host "${Green}Build complete. Image ready for use.${Reset}" -ForegroundColor Green
    exit 0
}

# Ensure directories exist
if (!(Test-Path "sample_docs")) {
    New-Item -ItemType Directory -Path "sample_docs" -Force
    Write-Host "${Yellow}📁 Created sample_docs directory${Reset}" -ForegroundColor Yellow
}

if (!(Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" -Force
    Write-Host "${Yellow}📁 Created output directory${Reset}" -ForegroundColor Yellow
}

# Check for PDFs in sample_docs
$pdfFiles = Get-ChildItem -Path "sample_docs" -Filter "*.pdf"
if ($pdfFiles.Count -eq 0) {
    Write-Host "${Red}❌ No PDF files found in sample_docs directory${Reset}" -ForegroundColor Red
    Write-Host "Please add PDF files to the sample_docs directory before running" -ForegroundColor Red
    exit 1
}

Write-Host "${Green}📄 Found $($pdfFiles.Count) PDF file(s) in sample_docs${Reset}" -ForegroundColor Green

# Check execution mode
if ($UseJson -eq $true -and (Test-Path "input_template.json")) {
    Write-Host "${Blue}🔄 Running with JSON input template...${Reset}" -ForegroundColor Blue
    
    # Read the JSON to show what will be processed
    $jsonContent = Get-Content "input_template.json" | ConvertFrom-Json
    Write-Host "${Yellow}Persona:${Reset} $($jsonContent.persona.role)" -ForegroundColor Yellow
    Write-Host "${Yellow}Job:${Reset} $($jsonContent.job_to_be_done.task)" -ForegroundColor Yellow
    Write-Host "${Yellow}Test Case:${Reset} $($jsonContent.challenge_info.test_case_name)" -ForegroundColor Yellow
    Write-Host ""
    
    # Run with JSON input
    Write-Host "${Blue}🚀 Starting document processing...${Reset}" -ForegroundColor Blue
    $startTime = Get-Date
    
    docker run --rm `
        -v "${PWD}/sample_docs:/app/documents" `
        -v "${PWD}:/app/input" `
        -v "${PWD}/output:/app/output" `
        doc-intelligence
        
} elseif ($Persona -ne "" -and $Job -ne "") {
    Write-Host "${Blue}🔄 Running with command-line arguments...${Reset}" -ForegroundColor Blue
    Write-Host "${Yellow}Persona:${Reset} $Persona" -ForegroundColor Yellow
    Write-Host "${Yellow}Job:${Reset} $Job" -ForegroundColor Yellow
    Write-Host ""
    
    # Run with command line arguments
    Write-Host "${Blue}🚀 Starting document processing...${Reset}" -ForegroundColor Blue
    $startTime = Get-Date
    
    docker run --rm `
        -v "${PWD}/sample_docs:/app/documents" `
        -v "${PWD}/output:/app/output" `
        doc-intelligence `
        python main.py `
        --documents_dir /app/documents `
        --output_dir /app/output `
        --persona "$Persona" `
        --job "$Job"
        
} else {
    # Run predefined test cases
    if ($TestCase -eq "") {
        Write-Host "${Yellow}Available test cases:${Reset}" -ForegroundColor Yellow
        Write-Host "1. academic - PhD Researcher analyzing research papers"
        Write-Host "2. business - Investment Analyst reviewing financial reports" 
        Write-Host "3. student - Undergraduate studying chemistry concepts"
        Write-Host "4. forms - HR Professional creating fillable forms (uses JSON template)"
        Write-Host ""
        $TestCase = Read-Host "Enter test case number or name (1-4, or academic/business/student/forms)"
    }
    
    switch ($TestCase.ToLower()) {
        {$_ -in "1", "academic"} {
            $selectedPersona = "PhD Researcher in Computational Biology"
            $selectedJob = "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
        }
        {$_ -in "2", "business"} {
            $selectedPersona = "Investment Analyst" 
            $selectedJob = "Analyze revenue trends, R&D investments, and market positioning strategies"
        }
        {$_ -in "3", "student"} {
            $selectedPersona = "Undergraduate Chemistry Student"
            $selectedJob = "Identify key concepts and mechanisms for exam preparation on reaction kinetics"
        }
        {$_ -in "4", "forms"} {
            if (Test-Path "input_template.json") {
                Write-Host "${Blue}🔄 Running forms test case with JSON template...${Reset}" -ForegroundColor Blue
                $jsonContent = Get-Content "input_template.json" | ConvertFrom-Json
                Write-Host "${Yellow}Persona:${Reset} $($jsonContent.persona.role)" -ForegroundColor Yellow
                Write-Host "${Yellow}Job:${Reset} $($jsonContent.job_to_be_done.task)" -ForegroundColor Yellow
                
                $startTime = Get-Date
                docker run --rm `
                    -v "${PWD}/sample_docs:/app/documents" `
                    -v "${PWD}:/app/input" `
                    -v "${PWD}/output:/app/output" `
                    doc-intelligence
                    
                $endTime = Get-Date
                $duration = ($endTime - $startTime).TotalSeconds
                
                Write-Host ""
                Write-Host "${Green}✅ Processing completed in $([math]::Round($duration, 2)) seconds${Reset}" -ForegroundColor Green
                
                if (Test-Path "output/challenge1b_output.json") {
                    Write-Host "${Green}📋 Results saved to: output/challenge1b_output.json${Reset}" -ForegroundColor Green
                } elseif (Test-Path "output/*_output.json") {
                    $outputFile = Get-ChildItem "output/*_output.json" | Select-Object -First 1
                    Write-Host "${Green}📋 Results saved to: $($outputFile.Name)${Reset}" -ForegroundColor Green
                }
                
                # Show constraint compliance
                if ($duration -le 60) {
                    Write-Host "${Green}✅ Time constraint met: $([math]::Round($duration, 2))s ≤ 60s${Reset}" -ForegroundColor Green
                } else {
                    Write-Host "${Red}❌ Time constraint exceeded: $([math]::Round($duration, 2))s > 60s${Reset}" -ForegroundColor Red
                }
                
                Write-Host "${Blue}🎯 Hackathon submission ready!${Reset}" -ForegroundColor Blue
                return
            } else {
                Write-Host "${Red}❌ input_template.json not found for forms test case${Reset}" -ForegroundColor Red
                exit 1
            }
        }
        default {
            Write-Host "${Red}❌ Invalid test case: $TestCase${Reset}" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "${Blue}🔄 Running test case: $TestCase${Reset}" -ForegroundColor Blue
    Write-Host "${Yellow}Persona:${Reset} $selectedPersona" -ForegroundColor Yellow  
    Write-Host "${Yellow}Job:${Reset} $selectedJob" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "${Blue}🚀 Starting document processing...${Reset}" -ForegroundColor Blue
    $startTime = Get-Date
    
    docker run --rm `
        -v "${PWD}/sample_docs:/app/documents" `
        -v "${PWD}/output:/app/output" `
        doc-intelligence `
        python main.py `
        --documents_dir /app/documents `
        --output_dir /app/output `
        --persona "$selectedPersona" `
        --job "$selectedJob" `
        --output_file "test_case_${TestCase}_results.json"
}

if ($null -eq $startTime) { return }

$endTime = Get-Date  
$duration = ($endTime - $startTime).TotalSeconds

Write-Host ""
Write-Host "${Green}✅ Processing completed in $([math]::Round($duration, 2)) seconds${Reset}" -ForegroundColor Green

# Check results
if (Test-Path "output/results.json") {
    Write-Host "${Green}📋 Results saved to: output/results.json${Reset}" -ForegroundColor Green
} elseif (Test-Path "output/*_results.json") {
    $outputFile = Get-ChildItem "output/*_results.json" | Select-Object -First 1
    Write-Host "${Green}📋 Results saved to: $($outputFile.Name)${Reset}" -ForegroundColor Green
}

# Show constraint compliance
if ($duration -le 60) {
    Write-Host "${Green}✅ Time constraint met: $([math]::Round($duration, 2))s ≤ 60s${Reset}" -ForegroundColor Green
} else {
    Write-Host "${Red}❌ Time constraint exceeded: $([math]::Round($duration, 2))s > 60s${Reset}" -ForegroundColor Red
}

Write-Host "${Blue}🎯 Processing complete! Check the output directory for results.${Reset}" -ForegroundColor Blue
