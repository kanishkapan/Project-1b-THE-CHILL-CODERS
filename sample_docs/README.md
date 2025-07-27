# 📁 Sample Documents Directory

## 🎯 Purpose

This directory is where you place your PDF documents for analysis by the Document Intelligence System.

## 📋 Instructions

### **Step 1: Add Your PDF Documents**
Place your PDF files in this directory. The system supports:
- ✅ **Text-based PDFs**: Regular PDF documents with selectable text
- ✅ **Scanned PDFs**: Image-based PDFs (OCR will be applied automatically)
- ✅ **Mixed Content**: PDFs with both text and images
- ✅ **Multiple Pages**: Documents of any length

### **Step 2: Update Input JSON**
Make sure your `input_*.json` file references the correct filenames:

```json
{
    "documents": [
        {
            "filename": "your_document1.pdf",
            "title": "Your Document 1 Title"
        },
        {
            "filename": "your_document2.pdf", 
            "title": "Your Document 2 Title"
        }
    ]
}
```

### **Step 3: Run Analysis**
```bash
python main.py --input_json your_input.json
```

## 📊 Supported File Types

- **PDF Files**: Primary format (required)
- **File Size**: Up to 100MB per document
- **Document Count**: 1-20 documents recommended
- **Languages**: English text processing optimized

## 🔍 Example Use Cases

### **Business Analysis**
- Financial reports, market analysis, business plans
- Strategic documents, competitive intelligence

### **Academic Research** 
- Research papers, literature reviews, technical reports
- Educational materials, course content

### **Legal/Compliance**
- Contracts, policy documents, regulatory materials
- Compliance reports, legal briefs

### **Technical Documentation**
- User manuals, API documentation, technical specifications
- Process documentation, system guides

## 🚨 Important Notes

1. **File Names**: Use descriptive filenames without special characters
2. **Document Quality**: Higher quality PDFs yield better results
3. **Content Language**: System optimized for English content
4. **Privacy**: Ensure documents don't contain sensitive information

## 🆘 Troubleshooting

**No PDFs Found Error**: 
- Check this directory contains `.pdf` files
- Verify filenames match your input JSON exactly

**Poor Extraction Quality**:
- Try higher resolution scans for image-based PDFs
- Ensure text is clearly readable

**Processing Slow**:
- Reduce number of documents for faster processing
- Use smaller file sizes when possible

---
**Ready to Process!** Add your PDF documents here and run the system.
