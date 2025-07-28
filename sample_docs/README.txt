📁 SAMPLE DOCUMENTS FOLDER

This folder is designated for placing PDF documents that will be processed by the Document Intelligence System.

🔧 USAGE INSTRUCTIONS:
1. Place your PDF files directly in this folder
2. The system will automatically detect and process all PDF files
3. Supported formats: .pdf files only
4. Maximum recommended: 10 documents for optimal performance

📋 FOR ADOBE JUDGES:
- Place your test PDF documents here before running the system
- The system is designed to work with any domain (Travel, Food, HR, Tech, Academic, Legal, etc.)
- Files will be automatically discovered and processed

🚀 QUICK TEST:
After placing PDFs here, run either:
- Python: python main.py --input_json input_template.json
- Docker: docker run --rm -v "${PWD}/sample_docs:/app/documents" -v "${PWD}:/app/input" -v "${PWD}/output:/app/output" doc-intelligence

✅ This folder is currently empty and ready for your test documents!
