"""
Content Extractor Module
Extracts relevant content from documents based on persona context.
Uses lightweight NLP techniques optimized for CPU execution.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import math

from src.persona_analyzer import PersonaContext
from src.utils import clean_text, extract_keywords, calculate_text_similarity

logger = logging.getLogger(__name__)

@dataclass
class ExtractedSection:
    """Data class for extracted document sections."""
    document: str
    page_number: int
    section_title: str
    content: str
    content_preview: str
    relevance_score: float
    word_count: int
    char_count: int
    section_type: str
    key_concepts: List[str]

class ContentExtractor:
    """
    Extracts relevant content from documents based on persona context.
    Uses lightweight NLP for fast, CPU-only processing.
    """
    
    def __init__(self):
        """Initialize the content extractor."""
        self.min_section_length = 100  # Minimum characters for a section
        self.max_section_length = 2000  # Maximum characters to extract per section
        self.min_relevance_threshold = 0.01  # Minimum relevance score to include
        
        # Section type patterns
        self.section_patterns = {
            'abstract': [
                r'abstract\b', r'summary\b', r'overview\b'
            ],
            'introduction': [
                r'introduction\b', r'background\b', r'motivation\b'
            ],
            'methodology': [
                r'method(?:ology)?\b', r'approach\b', r'technique\b', 
                r'procedure\b', r'implementation\b'
            ],
            'results': [
                r'results?\b', r'findings?\b', r'outcome\b', r'analysis\b'
            ],
            'discussion': [
                r'discussion\b', r'interpretation\b', r'implications?\b'
            ],
            'conclusion': [
                r'conclusion\b', r'summary\b', r'final\b', r'closing\b'
            ],
            'literature_review': [
                r'literature\s+review\b', r'related\s+work\b', r'prior\s+work\b'
            ],
            'financial': [
                r'financial\b', r'revenue\b', r'profit\b', r'income\b', r'expense\b'
            ],
            'technical': [
                r'technical\b', r'specification\b', r'architecture\b', r'design\b'
            ]
        }
    
    def extract_sections(self, document: Dict[str, Any], persona_context: PersonaContext) -> List[ExtractedSection]:
        """
        Extract relevant sections from a document based on persona context.
        
        Args:
            document: Processed document dictionary
            persona_context: Analyzed persona context
            
        Returns:
            List of extracted sections with relevance scores
        """
        logger.info(f"Extracting content from {document['filename']}")
        
        extracted_sections = []
        
        for page_data in document['pages']:
            page_sections = self._extract_page_sections(
                page_data, 
                document['filename'], 
                persona_context
            )
            extracted_sections.extend(page_sections)
        
        # Filter by minimum relevance
        filtered_sections = [
            section for section in extracted_sections 
            if section.relevance_score >= self.min_relevance_threshold
        ]
        
        logger.info(f"Extracted {len(filtered_sections)} relevant sections from {document['filename']}")
        
        return filtered_sections
    
    def _extract_page_sections(self, page_data: Dict[str, Any], filename: str, 
                              persona_context: PersonaContext) -> List[ExtractedSection]:
        """Extract sections from a single page."""
        sections = []
        page_number = page_data['page_number']
        page_text = page_data['text']
        
        # If page has identified sections, process them
        if page_data['sections']:
            for section_info in page_data['sections']:
                section = self._create_section_from_info(
                    section_info, page_text, filename, page_number, persona_context
                )
                if section:
                    sections.append(section)
        else:
            # If no sections identified, treat entire page as one section
            section = self._create_section_from_text(
                page_text, filename, page_number, "Full Page Content", persona_context
            )
            if section:
                sections.append(section)
        
        return sections
    
    def _create_section_from_info(self, section_info: Dict[str, Any], page_text: str,
                                 filename: str, page_number: int, 
                                 persona_context: PersonaContext) -> Optional[ExtractedSection]:
        """Create an ExtractedSection from section info."""
        title = section_info['title']
        
        # Find the section content in the page text
        content = self._extract_section_content(title, page_text)
        
        if len(content) < self.min_section_length:
            return None
        
        return self._create_section_from_text(
            content, filename, page_number, title, persona_context
        )
    
    def _create_section_from_text(self, content: str, filename: str, page_number: int,
                                 title: str, persona_context: PersonaContext) -> Optional[ExtractedSection]:
        """Create an ExtractedSection from text content."""
        if len(content) < self.min_section_length:
            return None
        
        # Limit content length
        if len(content) > self.max_section_length:
            content = content[:self.max_section_length] + "..."
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(content, persona_context)
        
        # Extract key concepts
        key_concepts = extract_keywords(content, max_keywords=10)
        
        # Determine section type
        section_type = self._classify_section_type(title, content)
        
        # Create preview
        content_preview = content[:200] + "..." if len(content) > 200 else content
        
        return ExtractedSection(
            document=filename,
            page_number=page_number,
            section_title=title,
            content=content,
            content_preview=content_preview,
            relevance_score=relevance_score,
            word_count=len(content.split()),
            char_count=len(content),
            section_type=section_type,
            key_concepts=key_concepts
        )
    
    def _extract_section_content(self, title: str, page_text: str) -> str:
        """Extract content for a specific section from page text."""
        # Find the title in the text
        title_pattern = re.escape(title)
        match = re.search(title_pattern, page_text, re.IGNORECASE)
        
        if not match:
            return ""
        
        # Extract content from title position
        start_pos = match.end()
        
        # Find next section or end of text
        remaining_text = page_text[start_pos:]
        
        # Look for next heading (common patterns)
        next_heading_patterns = [
            r'\n\s*[A-Z][A-Z\s]{2,50}\n',  # ALL CAPS headings
            r'\n\s*\d+\.?\s+[A-Z][^.!?\n]{5,80}\n',  # Numbered headings
            r'\n\s*[A-Z][a-z\s]{3,50}\n'  # Title case headings
        ]
        
        end_pos = len(remaining_text)
        for pattern in next_heading_patterns:
            match = re.search(pattern, remaining_text)
            if match:
                end_pos = min(end_pos, match.start())
        
        content = remaining_text[:end_pos].strip()
        
        # Limit content length
        if len(content) > self.max_section_length:
            content = content[:self.max_section_length]
        
        return content
    
    def _calculate_relevance_score(self, content: str, persona_context: PersonaContext) -> float:
        """Calculate relevance score for content based on persona context."""
        if not content.strip():
            return 0.0
        
        content_lower = content.lower()
        score = 0.0
        
        # Score based on job keywords (40% weight)
        job_keyword_score = 0.0
        if persona_context.job_keywords:
            matches = sum(1 for keyword in persona_context.job_keywords if keyword in content_lower)
            job_keyword_score = matches / len(persona_context.job_keywords)
        score += job_keyword_score * 0.4
        
        # Score based on priority topics (30% weight)
        topic_score = 0.0
        if persona_context.priority_topics:
            matches = sum(1 for topic in persona_context.priority_topics if topic in content_lower)
            topic_score = matches / len(persona_context.priority_topics)
        score += topic_score * 0.3
        
        # Score based on expertise areas (20% weight)
        expertise_score = 0.0
        if persona_context.expertise_areas:
            matches = sum(1 for area in persona_context.expertise_areas 
                         if area.lower() in content_lower)
            expertise_score = matches / len(persona_context.expertise_areas)
        score += expertise_score * 0.2
        
        # Score based on relevant section types (10% weight)
        section_score = 0.0
        if persona_context.relevant_sections:
            matches = sum(1 for section in persona_context.relevant_sections 
                         if section in content_lower)
            section_score = matches / len(persona_context.relevant_sections)
        score += section_score * 0.1
        
        # Normalize score to 0-1 range
        return min(score, 1.0)
    
    def _classify_section_type(self, title: str, content: str) -> str:
        """Classify the type of section based on title and content."""
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Check title first
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, title_lower):
                    return section_type
        
        # Check content if title doesn't match
        section_scores = {}
        for section_type, patterns in self.section_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, content_lower))
            if score > 0:
                section_scores[section_type] = score
        
        if section_scores:
            return max(section_scores, key=section_scores.get)
        
        return "general"
    
    def filter_by_relevance(self, sections: List[ExtractedSection], 
                           min_score: float = 0.3, max_sections: int = 20) -> List[ExtractedSection]:
        """
        Filter sections by relevance score and limit count.
        
        Args:
            sections: List of extracted sections
            min_score: Minimum relevance score
            max_sections: Maximum number of sections to return
            
        Returns:
            Filtered and limited list of sections
        """
        # Filter by minimum score
        filtered = [s for s in sections if s.relevance_score >= min_score]
        
        # Sort by relevance score (descending)
        filtered.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit count
        return filtered[:max_sections]
    
    def group_by_document(self, sections: List[ExtractedSection]) -> Dict[str, List[ExtractedSection]]:
        """Group sections by document filename."""
        grouped = {}
        for section in sections:
            if section.document not in grouped:
                grouped[section.document] = []
            grouped[section.document].append(section)
        
        return grouped
    
    def get_extraction_summary(self, sections: List[ExtractedSection]) -> Dict[str, Any]:
        """Generate summary statistics for extracted sections."""
        if not sections:
            return {}
        
        total_sections = len(sections)
        avg_relevance = sum(s.relevance_score for s in sections) / total_sections
        total_words = sum(s.word_count for s in sections)
        
        # Count by section type
        section_types = {}
        for section in sections:
            section_types[section.section_type] = section_types.get(section.section_type, 0) + 1
        
        # Count by document
        documents = set(s.document for s in sections)
        
        return {
            'total_sections': total_sections,
            'average_relevance_score': avg_relevance,
            'total_words': total_words,
            'unique_documents': len(documents),
            'section_types': section_types,
            'highest_relevance': max(s.relevance_score for s in sections),
            'lowest_relevance': min(s.relevance_score for s in sections)
        }
