# 🚀 Complete Setup Guide - Adobe Hackathon Round 1B

## 📋 Prerequisites

- **Python 3.8+** (Python 3.12 recommended)
- **4GB RAM minimum** (8GB recommended)
- **2GB disk space** for dependencies
- **Windows/Linux/macOS** supported

## 🔧 Method 1: From Scratch Setup (Recommended)

### **Step 1: Download Project**
```bash
# Option A: Git Clone
git clone https://github.com/kanishkapan/Project-1b-copilot.git
cd Project-1b-copilot

# Option B: Download ZIP
# Download from GitHub, extract, and navigate to folder
```

### **Step 2: Create Virtual Environment**

**Windows (PowerShell/CMD):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### **Step 4: Verify Installation**
```bash
# Test Python packages
python -c "import spacy, sklearn, pdfplumber, nltk; print('✅ All dependencies installed!')"

# Test spaCy model
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy model loaded!')"
```

### **Step 5: Add Your Documents & Configure**
```bash
# Add your PDF files to sample_docs/ directory
# Edit input_template.json with your information:
# - Update document filenames to match your PDFs
# - Set your persona (role)
# - Define your job-to-be-done (task)
```

### **Step 6: Run Test**
```bash
# Run with your customized input
python main.py --input_json input_template.json

# Should complete in ~15 seconds and create output file
```

### **Step 7: Check Results**
```bash
# View generated output (filename based on your test_case_name)
cat output/your_test_name_output.json

# Or open in your editor
code output/your_test_name_output.json
```

## 🐳 Method 2: Docker Setup (Alternative)

### **Step 1: Install Docker**
- **Windows**: Docker Desktop from docker.com
- **Linux**: `sudo apt install docker.io`
- **macOS**: Docker Desktop from docker.com

### **Step 2: Build Image**
```bash
cd Project-1b-copilot
docker build -t doc-intelligence .
```

### **Step 3: Run Container**
```bash
# Basic run
docker run --rm -v $(pwd)/output:/app/output doc-intelligence

# With custom input
docker run --rm \
  -v $(pwd)/sample_docs:/app/sample_docs \
  -v $(pwd)/output:/app/output \
  doc-intelligence python main.py --input_json input_defense_analysis.json
```

## 🎯 Quick Testing Guide

### **Test 1: Your Custom Analysis**
```bash
# 1. Add your PDFs to sample_docs/
# 2. Edit input_template.json with your persona and job
# 3. Run the system
python main.py --input_json input_template.json
# Expected: {your_test_name}_output.json in output/
```

### **Test 2: Cross-Domain Validation**
```bash
# Try different domain by changing persona in input_template.json
# Example: Change from "Business Analyst" to "Research Scientist"
python main.py --input_json input_template.json  
# Expected: Different relevance ranking based on new persona
```

### **Test 3: Multiple Document Types**
```bash
# Add diverse document types to sample_docs/
# Mix reports, papers, manuals, etc.
python main.py --input_json input_template.json
```

## 📊 Expected Output Structure

After successful run, you should see:
```
output/
├── README.md                          # Output format explanation  
└── your_test_name_output.json         # Your analysis results
```

Each JSON contains:
- **metadata**: Input info and processing timestamp
- **extracted_sections**: Top 5 ranked sections with page numbers
- **subsection_analysis**: Detailed content excerpts

## 🛠️ Troubleshooting

### **Issue: spaCy Model Missing**
```bash
# Error: Can't find model 'en_core_web_sm'
# Solution:
python -m spacy download en_core_web_sm
```

### **Issue: Permission Denied (Windows)**
```bash
# Error: execution policy restricted
# Solution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Issue: Memory Error**
```bash
# Error: Memory allocation failed
# Solutions:
# 1. Close other applications
# 2. Use Docker with memory limit:
docker run --memory=1g doc-intelligence
```

### **Issue: PDF Processing Fails**
```bash
# Error: PDF extraction failed
# Solution: Check sample_docs folder has PDFs:
dir sample_docs/
# Should show .pdf files
```

### **Issue: Import Errors**
```bash
# Error: ModuleNotFoundError
# Solution: Reinstall dependencies:
pip install -r requirements.txt --force-reinstall
```

## 🔍 Verification Checklist

### **✅ Installation Verification**
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Virtual environment activated (prompt shows `.venv`)
- [ ] All packages installed (`pip list | grep spacy`)
- [ ] spaCy model downloaded (`python -m spacy info en_core_web_sm`)

### **✅ Functionality Verification**  
- [ ] Test run completes without errors
- [ ] Output JSON file generated in output/
- [ ] Processing time under 30 seconds
- [ ] JSON contains expected structure (metadata, extracted_sections)

### **✅ Performance Verification**
- [ ] System handles 15+ PDF documents
- [ ] Memory usage stays under 1GB
- [ ] Works with scanned PDFs (OCR fallback)
- [ ] Cross-domain testing successful

## 📝 Input Format Guide

Create custom input JSON files:

```json
{
    "challenge_info": {
        "challenge_id": "round_1b_003",
        "test_case_name": "your_test_name",
        "description": "Brief description of your test"
    },
    "documents": [
        {
            "filename": "document1.pdf",
            "title": "Document 1 Title"
        },
        {
            "filename": "document2.pdf", 
            "title": "Document 2 Title"
        }
    ],
    "persona": {
        "role": "Your Professional Role (e.g., Data Scientist, Legal Advisor)"
    },
    "job_to_be_done": {
        "task": "Specific task description (e.g., Extract methodology for research review)"
    }
}
```

## 🏁 Ready for Submission

Once setup is complete, your system should:
- ✅ Process any domain (tested: Food, Adobe/PDF, HR)
- ✅ Generate results in <20 seconds  
- ✅ Work offline without internet
- ✅ Handle 15+ documents with OCR
- ✅ Produce structured JSON output
- ✅ Achieve 60% F1 score on test cases

## 📞 Need Help?

1. **Check logs**: System prints detailed progress information
2. **Review files**: Ensure sample_docs/ contains PDF files
3. **Test environment**: Run verification commands above
4. **Docker alternative**: If local setup fails, use Docker method

---
**Setup Complete!** 🎉 Your document intelligence system is ready for Adobe Hackathon Round 1B evaluation.
