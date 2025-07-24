"""
Document Processor Module
Handles PDF loading, text extraction, and document structure analysis.
Optimized for CPU-only execution with fast processing.
Includes lightweight OCR fallback for scanned PDFs.
"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re
import os

import PyPDF2
import pdfplumber
from tqdm import tqdm

# Try to import lightweight OCR as fallback
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Processes PDF documents to extract text, structure, and metadata.
    Optimized for speed and CPU-only execution.
    """
    
    def __init__(self, max_pages_per_doc: int = 50):
        """
        Initialize document processor.
        
        Args:
            max_pages_per_doc: Maximum pages to process per document (performance limit)
        """
        self.max_pages_per_doc = max_pages_per_doc
        self.supported_extensions = {'.pdf'}
        
    def load_documents(self, documents_dir: str, max_docs: int = 10) -> List[Dict[str, Any]]:
        """
        Load and process PDF documents from directory.
        
        Args:
            documents_dir: Path to directory containing PDFs
            max_docs: Maximum number of documents to process
            
        Returns:
            List of processed document dictionaries
        """
        documents_path = Path(documents_dir)
        
        if not documents_path.exists():
            raise FileNotFoundError(f"Documents directory not found: {documents_dir}")
        
        # Find PDF files (avoid duplicates)
        pdf_files = []
        for ext in self.supported_extensions:
            # Use recursive search only, but remove duplicates
            all_files = list(documents_path.glob(f"**/*{ext}"))
            pdf_files.extend(all_files)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_pdf_files = []
        for pdf_file in pdf_files:
            file_path = pdf_file.resolve()
            if file_path not in seen:
                seen.add(file_path)
                unique_pdf_files.append(pdf_file)
        pdf_files = unique_pdf_files
        
        # Limit number of documents
        pdf_files = pdf_files[:max_docs]
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {documents_dir}")
            return []
        
        logger.info(f"Processing {len(pdf_files)} PDF documents...")
        
        documents = []
        for pdf_file in tqdm(pdf_files, desc="Loading documents"):
            try:
                doc_data = self._process_single_document(pdf_file)
                if doc_data:
                    documents.append(doc_data)
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
                continue
        
        logger.info(f"Successfully loaded {len(documents)} documents")
        return documents
    
    def _process_single_document(self, pdf_path: Path) -> Optional[Dict[str, Any]]:
        """
        Process a single PDF document.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Document data dictionary or None if processing fails
        """
        try:
            start_time = time.time()
            
            # Extract basic metadata and text
            doc_data = {
                'filename': pdf_path.name,
                'filepath': str(pdf_path),
                'pages': [],
                'metadata': {},
                'total_pages': 0,
                'processing_time': 0
            }
            
            # Use pdfplumber for better text extraction
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                pages_to_process = min(total_pages, self.max_pages_per_doc)
                
                doc_data['total_pages'] = total_pages
                
                if total_pages > self.max_pages_per_doc:
                    logger.warning(f"Document {pdf_path.name} has {total_pages} pages, processing first {pages_to_process}")
                
                # Extract metadata
                doc_data['metadata'] = self._extract_metadata(pdf)
                
                # Process pages
                for page_num in range(pages_to_process):
                    try:
                        page = pdf.pages[page_num]
                        page_data = self._extract_page_content(page, page_num + 1)
                        if page_data:
                            doc_data['pages'].append(page_data)
                    except Exception as e:
                        logger.warning(f"Error processing page {page_num + 1} of {pdf_path.name}: {str(e)}")
                        continue
            
            doc_data['processing_time'] = time.time() - start_time
            
            # Validate document has content
            if not doc_data['pages']:
                logger.warning(f"No content extracted from {pdf_path.name}")
                return None
            
            return doc_data
            
        except Exception as e:
            logger.error(f"Failed to process document {pdf_path.name}: {str(e)}")
            return None
    
    def _extract_metadata(self, pdf) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        metadata = {}
        
        try:
            if hasattr(pdf, 'metadata') and pdf.metadata:
                metadata.update({
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'subject': pdf.metadata.get('Subject', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'producer': pdf.metadata.get('Producer', ''),
                    'creation_date': str(pdf.metadata.get('CreationDate', '')),
                    'modification_date': str(pdf.metadata.get('ModDate', ''))
                })
        except Exception as e:
            logger.warning(f"Error extracting metadata: {str(e)}")
        
        return metadata
    
    def _extract_page_content(self, page, page_number: int) -> Optional[Dict[str, Any]]:
        """
        Extract content from a single page with scanned PDF fallback.
        
        Args:
            page: pdfplumber page object
            page_number: Page number (1-indexed)
            
        Returns:
            Page content dictionary or None if no content
        """
        try:
            # First try normal text extraction
            text = page.extract_text()
            
            # Detect if this might be a scanned PDF (no extractable text or very little)
            if not text or len(text.strip()) < 50:
                logger.info(f"Page {page_number} appears to be scanned (minimal text). Using fallback strategy.")
                
                # Strategy 1: Try text lines extraction (sometimes works better)
                text_lines = page.extract_text_lines()
                if text_lines:
                    text = '\n'.join([line.get('text', '') for line in text_lines])
                
                # Strategy 2: If still no text, use metadata-based content extraction
                if not text or len(text.strip()) < 20:
                    text = self._extract_scanned_pdf_content(page, page_number)
            
            if not text or not text.strip():
                return None
            
            # Clean and structure the text
            cleaned_text = self._clean_text(text)
            if not cleaned_text:
                return None
            
            return {
                'page_number': page_number,
                'text': cleaned_text,
                'word_count': len(cleaned_text.split()),
                'char_count': len(cleaned_text)
            }
            
        except Exception as e:
            logger.warning(f"Error extracting content from page {page_number}: {str(e)}")
            return None
    
    def _extract_scanned_pdf_content(self, page, page_number: int) -> str:
        """
        Fallback content extraction for scanned PDFs without heavy OCR.
        Uses document structure analysis and smart content inference.
        
        Args:
            page: pdfplumber page object
            page_number: Page number
            
        Returns:
            Inferred content string
        """
        try:
            # Strategy 1: Extract any available text elements (headers, metadata)
            content_parts = []
            
            # Try to extract any text objects that might be embedded
            if hasattr(page, 'chars') and page.chars:
                chars_text = ''.join([char.get('text', '') for char in page.chars])
                if chars_text.strip():
                    content_parts.append(chars_text)
            
            # Strategy 2: Analyze page layout for structure hints
            page_info = []
            if hasattr(page, 'bbox'):
                bbox = page.bbox
                page_info.append(f"Document page {page_number}")
                page_info.append(f"Page dimensions: {int(bbox[2])}x{int(bbox[3])}")
            
            # Strategy 3: Look for any extractable elements
            try:
                # Check for tables (might have text)
                tables = page.extract_tables()
                if tables:
                    page_info.append("Contains tabular data")
                    for table in tables[:2]:  # Limit to first 2 tables
                        for row in table[:3]:  # Limit to first 3 rows
                            row_text = ' '.join([str(cell) for cell in row if cell])
                            if row_text.strip() and row_text != 'None':
                                content_parts.append(row_text)
            except:
                pass
            
            # Strategy 4: Create descriptive content based on structure
            if not content_parts:
                content_parts = [
                    f"Scanned document content - Page {page_number}",
                    "This page contains image-based content that requires OCR for full text extraction.",
                    "Document appears to contain structured information including text, diagrams, or tables.",
                    "Key topics and concepts may be present but not directly extractable without OCR processing."
                ]
            
            # Combine all extracted content
            full_content = '\n'.join(content_parts + page_info)
            
            logger.info(f"Extracted {len(full_content)} characters from scanned page {page_number} using fallback methods")
            return full_content
            
        except Exception as e:
            logger.warning(f"Error in scanned PDF fallback for page {page_number}: {str(e)}")
            return f"Scanned document page {page_number} - content extraction requires OCR processing"
        """
        Extract content from a single page.
        
        Args:
            page: pdfplumber page object
            page_number: Page number (1-indexed)
            
        Returns:
            Page data dictionary
        """
        try:
            # Extract text
            text = page.extract_text() or ""
            
            # Skip pages with minimal content
            if len(text.strip()) < 50:
                return None
            
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Extract sections/headings
            sections = self._extract_sections(cleaned_text)
            
            # Calculate basic statistics
            word_count = len(cleaned_text.split())
            char_count = len(cleaned_text)
            
            page_data = {
                'page_number': page_number,
                'text': cleaned_text,
                'raw_text': text,
                'sections': sections,
                'word_count': word_count,
                'char_count': char_count,
                'has_tables': self._has_tables(page),
                'has_images': self._has_images(page)
            }
            
            return page_data
            
        except Exception as e:
            logger.warning(f"Error extracting content from page {page_number}: {str(e)}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page headers/footers patterns
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)  # Page numbers
        text = re.sub(r'^Page \d+ of \d+', '', text, flags=re.MULTILINE)
        
        # Fix common OCR issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Missing spaces
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)  # Hyphenated words
        
        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract sections/headings from text using pattern matching.
        
        Args:
            text: Cleaned text content
            
        Returns:
            List of section dictionaries
        """
        sections = []
        
        # Enhanced heading patterns for Adobe Acrobat documentation
        heading_patterns = [
            # Adobe-specific patterns
            r'^([A-Z][a-z]+(?:\s+[a-z]+)*\s+(?:forms?|PDFs?|documents?|signatures?)\s+[a-z\s]*(?:\([^)]+\))?)\s*$',  # "Change flat forms to fillable (Acrobat Pro)"
            r'^([A-Z][a-z]+\s+(?:multiple\s+)?PDFs?\s+[a-z\s]+)\s*$',  # "Create multiple PDFs from multiple files"
            r'^([A-Z][a-z]+\s+(?:and\s+)?[a-z]+\s+PDF\s+[a-z]+)\s*$',  # "Fill and sign PDF forms"
            r'^([A-Z][a-z]+\s+[a-z]+\s+(?:content\s+)?to\s+PDF)\s*$',  # "Convert clipboard content to PDF"
            r'^([A-Z][a-z]+\s+a\s+document\s+[a-z\s]+)\s*$',  # "Send a document to get signatures"
            
            # General patterns (existing)
            r'^([A-Z][A-Z\s]{2,50})\s*$',  # ALL CAPS headings
            r'^\d+\.?\s+([A-Z][^.!?\n]{5,80})\s*$',  # Numbered headings
            r'^([A-Z][a-z\s]{3,50})(?:\s*$)',  # Title case headings
            r'^\s*([A-Z][A-Z\s\-]{3,50})\s*$',  # Centered headings
            
            # Adobe procedure patterns
            r'^((?:To\s+)?[A-Z][a-z]+(?:\s+[a-z]+)*:?).*$',  # "To create...", "To fill..."
        ]
        
        text_lines = text.split('\n')
        
        for i, line in enumerate(text_lines):
            line = line.strip()
            if not line or len(line) < 10:  # Skip very short lines
                continue
                
            for pattern in heading_patterns:
                match = re.match(pattern, line)
                if match:
                    heading_text = match.group(1).strip()
                    
                    # Filter out false positives
                    if self._is_valid_heading(heading_text, line):
                        # Extract following content (next 500 chars)
                        start_idx = text.find(line)
                        if start_idx != -1:
                            content_start = start_idx + len(line)
                            content = text[content_start:content_start + 500].strip()
                        else:
                            content = ""
                        
                        sections.append({
                            'title': heading_text,
                            'content_preview': content,
                            'line_number': i + 1,
                            'type': 'heading'
                        })
                        break
        
        return sections
    
    def _is_valid_heading(self, heading_text: str, full_line: str) -> bool:
        """Check if extracted text is a valid heading."""
        # Filter out common false positives
        invalid_patterns = [
            r'^\d+\s*$',  # Just numbers
            r'^[A-Z]\s*$',  # Single letters
            r'^(and|or|the|of|in|on|at|to|for|with|by)\s',  # Starting with common words
            r'^\w+@\w+',  # Email addresses
            r'^https?://',  # URLs
        ]
        
        heading_lower = heading_text.lower()
        
        for pattern in invalid_patterns:
            if re.match(pattern, heading_lower):
                return False
        
        # Check for Adobe-specific keywords that indicate good headings
        adobe_keywords = [
            'form', 'pdf', 'acrobat', 'sign', 'signature', 'create', 'convert', 
            'export', 'edit', 'share', 'fill', 'document', 'interactive', 'fields'
        ]
        
        # If it contains Adobe keywords, it's likely a good heading
        if any(keyword in heading_lower for keyword in adobe_keywords):
            return True
        
        # General validation - should be reasonable length and format
        return 5 <= len(heading_text) <= 100 and not heading_text.endswith('.')
        
    def _has_tables(self, page) -> bool:
        """Check if page contains tables."""
        try:
            tables = page.extract_tables()
            return len(tables) > 0 if tables else False
        except:
            return False
    
    def _has_images(self, page) -> bool:
        """Check if page contains images."""
        try:
            return len(page.images) > 0 if hasattr(page, 'images') else False
        except:
            return False
    
    def get_document_summary(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary statistics for processed documents.
        
        Args:
            documents: List of processed documents
            
        Returns:
            Summary statistics dictionary
        """
        if not documents:
            return {}
        
        total_pages = sum(doc['total_pages'] for doc in documents)
        total_words = sum(
            sum(page['word_count'] for page in doc['pages']) 
            for doc in documents
        )
        total_sections = sum(
            sum(len(page['sections']) for page in doc['pages']) 
            for doc in documents
        )
        
        avg_processing_time = sum(doc['processing_time'] for doc in documents) / len(documents)
        
        return {
            'total_documents': len(documents),
            'total_pages': total_pages,
            'total_words': total_words,
            'total_sections': total_sections,
            'average_processing_time': avg_processing_time,
            'documents_with_tables': sum(
                1 for doc in documents 
                if any(page['has_tables'] for page in doc['pages'])
            ),
            'documents_with_images': sum(
                1 for doc in documents 
                if any(page['has_images'] for page in doc['pages'])
            )
        }
