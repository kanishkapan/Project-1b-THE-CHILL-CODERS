import pdfplumber

pdf_path = 'sample_docs/file20.pdf'
print(f"Testing PDF: {pdf_path}")

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Number of pages: {len(pdf.pages)}")
        
        if len(pdf.pages) > 0:
            page = pdf.pages[0]
            text = page.extract_text()
            if text:
                print(f"First 300 characters:")
                print(text[:300])
                print(f"\nTotal text length: {len(text)}")
            else:
                print("No text could be extracted from first page")
                
            # Try with different extraction method
            text_lines = page.extract_text_lines()
            print(f"Number of text lines: {len(text_lines)}")
            
        else:
            print("PDF has no pages")
            
except Exception as e:
    print(f"Error: {e}")
