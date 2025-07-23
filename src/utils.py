"""
Utility functions for the document intelligence system.
Common helper functions used across modules.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common PDF artifacts
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)  # Page numbers
    text = re.sub(r'^Page \d+ of \d+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Standalone numbers
    
    # Fix hyphenated words across lines
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    
    # Normalize quotation marks
    text = re.sub(r'["""]', '"', text)
    text = re.sub(r"[''']", "'", text)
    
    # Remove extra newlines
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()

def extract_keywords(text: str, max_keywords: int = 20) -> List[str]:
    """
    Extract important keywords from text using simple frequency analysis.
    
    Args:
        text: Text to analyze
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of important keywords
    """
    if not text:
        return []
    
    # Convert to lowercase and split into words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'through', 'during',
        'this', 'that', 'these', 'those', 'was', 'were', 'been', 'have',
        'has', 'had', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'must', 'shall', 'such', 'very', 'more', 'most', 'some',
        'any', 'all', 'each', 'every', 'other', 'another', 'same', 'different'
    }
    
    # Filter out stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in keywords[:max_keywords]]

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate basic text similarity using word overlap.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0 and 1
    """
    if not text1 or not text2:
        return 0.0
    
    # Extract words
    words1 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text1.lower()))
    words2 = set(re.findall(r'\b[a-zA-Z]{3,}\b', text2.lower()))
    
    if not words1 or not words2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0

def validate_output_format(output_data: Dict[str, Any]) -> bool:
    """
    Validate output data matches the required format.
    
    Args:
        output_data: Output dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = {
        'metadata': ['input_documents', 'persona', 'job_to_be_done', 'processing_timestamp'],
        'extracted_sections': ['document', 'page_number', 'section_title', 'importance_rank'],
        'sub_section_analysis': ['document', 'refined_text', 'page_number']
    }
    
    try:
        # Check top-level keys
        for key in required_keys:
            if key not in output_data:
                logger.error(f"Missing required key: {key}")
                return False
        
        # Check metadata
        metadata = output_data['metadata']
        for key in required_keys['metadata']:
            if key not in metadata:
                logger.error(f"Missing metadata key: {key}")
                return False
        
        # Check extracted sections structure
        if output_data['extracted_sections']:
            section = output_data['extracted_sections'][0]
            for key in required_keys['extracted_sections']:
                if key not in section:
                    logger.error(f"Missing section key: {key}")
                    return False
        
        # Check sub-section analysis structure
        if output_data['sub_section_analysis']:
            subsection = output_data['sub_section_analysis'][0]
            for key in required_keys['sub_section_analysis']:
                if key not in subsection:
                    logger.error(f"Missing sub-section key: {key}")
                    return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating output format: {str(e)}")
        return False

def estimate_processing_time(num_documents: int, avg_pages_per_doc: int = 10) -> float:
    """
    Estimate processing time based on document count and size.
    
    Args:
        num_documents: Number of documents to process
        avg_pages_per_doc: Average pages per document
        
    Returns:
        Estimated processing time in seconds
    """
    # Base time estimates (in seconds)
    time_per_page = 0.5  # Conservative estimate for CPU processing
    model_loading_time = 5.0  # One-time model loading
    analysis_overhead = 2.0  # Per document analysis overhead
    
    total_pages = num_documents * avg_pages_per_doc
    estimated_time = (
        model_loading_time + 
        (total_pages * time_per_page) + 
        (num_documents * analysis_overhead)
    )
    
    return estimated_time

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"

def create_safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing/replacing problematic characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove or replace problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_name = re.sub(r'\s+', '_', safe_name)
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # Ensure reasonable length
    if len(safe_name) > 100:
        name_part, ext = safe_name.rsplit('.', 1) if '.' in safe_name else (safe_name, '')
        safe_name = name_part[:95] + ('.' + ext if ext else '')
    
    return safe_name
