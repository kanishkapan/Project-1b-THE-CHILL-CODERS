import pdfplumber

pdf_path = 'sample_docs/file20.pdf'
print(f"Testing all pages of PDF: {pdf_path}")

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        text_found = False
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                print(f"\n=== PAGE {i+1} ===")
                print(f"Text length: {len(text)}")
                print(f"First 200 chars: {text[:200]}")
                text_found = True
                break
                
        if not text_found:
            print("\nNo extractable text found in any page - this appears to be a scanned/image PDF")
            print("For testing purposes, I'll create a text-based version of the content.")
            
except Exception as e:
    print(f"Error: {e}")
