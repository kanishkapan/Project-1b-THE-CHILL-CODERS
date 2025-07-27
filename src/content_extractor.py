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
        
        # Dynamic section type patterns - universal across domains
        self.section_patterns = {
            'abstract': [
                r'abstract\b', r'summary\b', r'overview\b', r'synopsis\b'
            ],
            'introduction': [
                r'introduction\b', r'background\b', r'motivation\b', r'overview\b', r'purpose\b'
            ],
            'methodology': [
                r'method(?:ology)?\b', r'approach\b', r'technique\b', r'procedure\b', 
                r'implementation\b', r'process\b', r'strategy\b'
            ],
            'results': [
                r'results?\b', r'findings?\b', r'outcome\b', r'analysis\b', r'data\b', 
                r'performance\b', r'evaluation\b'
            ],
            'discussion': [
                r'discussion\b', r'interpretation\b', r'implications?\b', r'analysis\b',
                r'evaluation\b', r'assessment\b'
            ],
            'conclusion': [
                r'conclusion\b', r'summary\b', r'final\b', r'closing\b', r'recommendations?\b'
            ],
            'content': [
                r'content\b', r'details?\b', r'information\b', r'description\b', r'explanation\b'
            ],
            'general': [
                r'important\b', r'key\b', r'main\b', r'primary\b', r'essential\b', r'critical\b'
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
        if page_data.get('sections'):
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
        
        # Generate descriptive title based on content and context
        descriptive_title = self._generate_descriptive_title(title, content, filename, persona_context)
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(content, persona_context)
        
        # Extract key concepts
        key_concepts = extract_keywords(content, max_keywords=10)
        
        # Determine section type
        section_type = self._classify_section_type(descriptive_title, content)
        
        # Create preview
        content_preview = content[:200] + "..." if len(content) > 200 else content
        
        return ExtractedSection(
            document=filename,
            page_number=page_number,
            section_title=descriptive_title,
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
    
    def _generate_descriptive_title(self, original_title: str, content: str, 
                                   filename: str, persona_context: PersonaContext) -> str:
        """Generate descriptive title based on content analysis - GENERALIZABLE approach."""
        content_lower = content.lower()
        
        # STEP 1: If original title is already good and descriptive, use it
        if (10 <= len(original_title) <= 80 and 
            original_title not in ["Full Page Content", "General", "Introduction", "Conclusion"] and
            not original_title.endswith(":")):
            return original_title
        
        # STEP 2: Extract meaningful titles from content structure
        # Look for section headers in the content
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if (15 <= len(line) <= 100 and 
                not line.lower().startswith(('the ', 'this ', 'that ', 'it ', 'as ', 'in ', 'on ', 'at ')) and
                line.count('.') <= 2 and  # Not a long sentence
                any(c.isupper() for c in line)):  # Has some capital letters
                return line
        
        # STEP 3: Content-based intelligent title generation (GENERALIZABLE)
        content_themes = self._analyze_content_themes(content_lower, persona_context)
        
        if content_themes:
            # Pick the most relevant theme based on persona
            primary_theme = content_themes[0]
            return self._format_theme_as_title(primary_theme, filename)
        
        # STEP 4: Fallback - extract file theme and create descriptive title
        file_base = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        # Remove common prefixes/suffixes
        for prefix in ['South of France - ', 'Research Paper ', 'Document ', 'Report ']:
            if file_base.startswith(prefix):
                file_base = file_base[len(prefix):]
        
        # If content has substantial information, create descriptive title
        if len(content) > 500:
            return f"{file_base} - Comprehensive Overview"
        else:
            return file_base
    
    def _analyze_content_themes(self, content_lower: str, persona_context: PersonaContext) -> List[str]:
        """Analyze content to identify major themes - GENERALIZABLE."""
        themes = []
        
        # Define theme patterns that work across domains
        theme_patterns = {
            'methodology': ['method', 'approach', 'technique', 'procedure', 'process', 'framework'],
            'analysis': ['analysis', 'evaluation', 'assessment', 'comparison', 'study', 'examination'],
            'results': ['results', 'findings', 'outcomes', 'performance', 'metrics', 'benchmarks'],
            'implementation': ['implementation', 'development', 'construction', 'building', 'creation'],
            'guidelines': ['guidelines', 'recommendations', 'best practices', 'tips', 'advice', 'suggestions'],
            'overview': ['overview', 'introduction', 'background', 'summary', 'guide', 'primer'],
            'technical': ['architecture', 'design', 'specification', 'technical', 'engineering'],
            'data': ['data', 'dataset', 'database', 'information', 'statistics', 'metrics'],
            'business': ['business', 'market', 'financial', 'economic', 'commercial', 'industry'],
            'activities': ['activities', 'things to do', 'experiences', 'attractions', 'adventures'],
            'planning': ['planning', 'preparation', 'organization', 'scheduling', 'coordination'],
            'culture': ['culture', 'tradition', 'heritage', 'history', 'historical', 'cultural'],
            'practical': ['practical', 'tips', 'tricks', 'how-to', 'guide', 'instructions']
        }
        
        # Score each theme based on content
        theme_scores = {}
        for theme, keywords in theme_patterns.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                theme_scores[theme] = score
        
        # Dynamic relevance boosting based on persona context
        if theme_scores and persona_context:
            # Use persona priority topics to boost relevant themes
            for priority_topic in persona_context.priority_topics:
                topic_lower = priority_topic.lower()
                
                # Boost themes that match priority topics
                for theme, keywords in theme_patterns.items():
                    if any(keyword in topic_lower for keyword in keywords):
                        theme_scores[theme] = theme_scores.get(theme, 0) * 1.5
                        
            # Boost themes based on job intent
            intent_boost = {
                'analysis': ['analysis', 'results', 'data'],
                'preparation': ['planning', 'guidelines', 'overview', 'practical'],
                'comprehensive_review': ['methodology', 'analysis', 'results'],
                'implementation': ['implementation', 'technical', 'practical'],
                'extraction': ['data', 'analysis', 'methodology']
            }
            
            if persona_context.job_intent in intent_boost:
                for theme in intent_boost[persona_context.job_intent]:
                    if theme in theme_scores:
                        theme_scores[theme] = theme_scores.get(theme, 0) * 1.3
            
            # Return top themes
            sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
            themes = [theme for theme, score in sorted_themes if score > 0]
        
        return themes
    
    def _format_theme_as_title(self, theme: str, filename: str) -> str:
        """Format theme as a proper title - GENERALIZABLE."""
        # Extract subject from filename
        file_subject = filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ')
        
        # Remove common prefixes
        for prefix in ['South of France - ', 'Research Paper ', 'Document ', 'Report ']:
            if file_subject.startswith(prefix):
                file_subject = file_subject[len(prefix):]
        
        # Create title based on theme
        theme_titles = {
            'methodology': f"{file_subject} - Methodology and Approach",
            'analysis': f"{file_subject} - Analysis and Evaluation", 
            'results': f"{file_subject} - Results and Findings",
            'implementation': f"{file_subject} - Implementation Guide",
            'guidelines': f"{file_subject} - Guidelines and Best Practices",
            'overview': f"{file_subject} - Comprehensive Overview",
            'technical': f"{file_subject} - Technical Specifications",
            'data': f"{file_subject} - Data and Metrics",
            'business': f"{file_subject} - Business Analysis",
            'activities': f"{file_subject} - Activities and Experiences",
            'planning': f"{file_subject} - Planning Guide",
            'culture': f"{file_subject} - Cultural and Historical Context",
            'practical': f"{file_subject} - Practical Tips and Guidelines"
        }
        
        return theme_titles.get(theme, f"{file_subject} - {theme.title()}")
    
    
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
