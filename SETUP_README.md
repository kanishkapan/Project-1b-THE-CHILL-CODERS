# Document Intelligence System - Setup Guide

## Quick Start Guide for New Users

This document intelligence system extracts and prioritizes relevant sections from PDF documents based on specific personas and their job requirements. This guide will walk you through setup and execution from scratch.

## 📋 Prerequisites

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher
- **Available Memory**: At least 2GB RAM
- **Disk Space**: 1GB free space

## 🚀 Installation Steps

### Step 1: Clone or Download the Project
```bash
git clone [repository-url]
cd Project-1b-copilot
```

### Step 2: Set Up Python Environment
#### Option A: Using Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv document-intel-env

# Activate environment
# Windows:
document-intel-env\Scripts\activate
# macOS/Linux:
source document-intel-env/bin/activate
```

#### Option B: Using the Pre-configured Environment
```bash
# Activate the included sklearn environment
.\sklearn-env\Scripts\activate  # Windows
source sklearn-env/bin/activate  # macOS/Linux
```

### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements-cpu.txt
```

**Note**: This project is optimized for CPU-only execution to meet hackathon constraints.

### Step 4: Verify Installation
```bash
# Run the setup script to verify all dependencies
python setup.py
```

## 📄 Preparing Your Documents

### Document Setup
1. Place your PDF documents in the `sample_docs/` folder
2. Ensure all PDFs are readable and not password-protected
3. File names should be descriptive (they're used in analysis)

### Input Configuration
Create an input JSON file following this structure:

```json
{
    "challenge_info": {
        "challenge_id": "your_test_case",
        "test_case_name": "descriptive_name",
        "description": "Brief description"
    },
    "documents": [
        {
            "filename": "document1.pdf",
            "title": "Document 1 Title"
        }
    ],
    "persona": {
        "role": "Your Persona Role"
    },
    "job_to_be_done": {
        "task": "Describe the specific job/task"
    }
}
```

## ▶️ Running the System

### Basic Execution
```bash
# Run with your input file
python main.py --input_json your_input_file.json
```

### Example Commands
```bash
# Test with HR professional scenario
python main.py --input_json input_business_analysis.json

# Process research documents
python main.py --input_json input_research_review.json

# Analyze travel planning documents  
python main.py --input_json input_travel_planner.json
```

## 📊 Understanding the Output

### Output Location
Results are saved in the `output/` folder with descriptive filenames based on your test case.

### Output Structure
```json
{
    "metadata": {
        "input_documents": ["list of processed files"],
        "persona": "Your persona",
        "job_to_be_done": "Your job description",
        "processing_timestamp": "ISO timestamp"
    },
    "extracted_sections": [
        {
            "document": "source file",
            "section_title": "descriptive title",
            "importance_rank": 1,
            "page_number": 5
        }
    ],
    "subsection_analysis": [
        {
            "document": "source file",
            "refined_text": "detailed content",
            "page_number": 5
        }
    ]
}
```

## 🔧 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'spacy'`
**Solution**: The system uses fallback processing. This warning is normal and doesn't affect functionality.

**Issue**: Slow processing
**Solution**: 
- Reduce number of documents
- Ensure PDFs are text-based (not scanned images)
- Check available memory

**Issue**: Empty output
**Solution**:
- Verify PDFs contain readable text
- Check that persona and job are well-defined
- Ensure documents are relevant to the task

### Performance Optimization
- **Document Count**: System tested with 7-15 documents
- **File Size**: Optimal with PDFs under 50MB each
- **Processing Time**: Expect 15-20 seconds for 15 documents

## 📈 Performance Constraints

This system is designed to meet specific hackathon constraints:
- ✅ **CPU-only execution** (no GPU required)
- ✅ **Under 60 seconds** processing time
- ✅ **Under 1GB** model memory usage
- ✅ **No internet access** required

## 🎯 Usage Examples

### Business Analysis
```json
{
    "persona": {"role": "Investment Analyst"},
    "job_to_be_done": {"task": "Analyze market trends and opportunities"}
}
```

### Research Review
```json
{
    "persona": {"role": "PhD Researcher"},
    "job_to_be_done": {"task": "Conduct literature review on methodologies"}
}
```

### Travel Planning
```json
{
    "persona": {"role": "Travel Planner"},
    "job_to_be_done": {"task": "Plan 4-day trip for college friends"}
}
```

### HR Forms Management
```json
{
    "persona": {"role": "HR professional"},
    "job_to_be_done": {"task": "Create fillable forms for onboarding"}
}
```

## 🆘 Support

For issues or questions:
1. Check this README for common solutions
2. Verify your input JSON format
3. Ensure all PDFs are in the correct folder
4. Check Python environment activation

## 🏁 Success Indicators

You'll know the system is working correctly when:
- ✅ Processing completes under 60 seconds
- ✅ Output JSON file is generated in `output/` folder
- ✅ Console shows section extraction progress
- ✅ Extracted sections are relevant to your persona/job

The system is now ready for use! 🚀
