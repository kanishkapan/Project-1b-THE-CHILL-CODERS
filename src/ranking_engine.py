"""
Optimized Ranking Engine Module
Winning approach for hackathon - proven rule-based ranking with high-impact pattern matching.
Focuses on m        # Combine scores using enhanced weights
        final_score = (
            relevance_score * self.weights['relevance'] +
            priority_boost * self.weights['priority_boost'] +
            diversity_bonus * self.weights['diversity'] +
            coverage_score * self.weights['coverage'] +
            section_type_score * self.weights['section_type'] +
            length_score * self.weights['length']
        )ccuracy and speed for the specific test cases.
"""

import logging
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from src.content_extractor import ExtractedSection
from src.persona_analyzer import PersonaContext
from src.utils import calculate_text_similarity

logger = logging.getLogger(__name__)

@dataclass
class RankedSection:
    """Data class for ranked sections with importance metrics."""
    document: str
    page_number: int
    section_title: str
    content: str
    content_preview: str
    importance_rank: int
    relevance_score: float
    diversity_bonus: float
    coverage_score: float
    final_score: float
    word_count: int
    char_count: int
    section_type: str
    key_concepts: List[str]
    ranking_factors: Dict[str, float]

class RankingEngine:
    """
    Optimized ranking engine focused on hackathon winning performance.
    Uses proven rule-based approach with intelligent pattern matching.
    """
    
    def __init__(self):
        """Initialize the ranking engine with optimized parameters."""
        # Enhanced ranking weights - optimized for better F1 score
        self.weights = {
            'relevance': 0.35,     # Direct relevance to persona/job
            'priority_boost': 0.25,  # NEW: Actionable content boost
            'diversity': 0.15,     # Content diversity bonus (reduced)
            'coverage': 0.15,      # Topic coverage completeness (reduced)
            'section_type': 0.05,  # Section type importance (reduced)
            'length': 0.05         # Content length bonus (reduced)
        }
        
        # Universal section type importance mapping
        self.section_importance = {
            'abstract': 0.9,
            'summary': 0.85,
            'introduction': 0.7,
            'methodology': 0.8,
            'results': 0.9,
            'discussion': 0.8,
            'conclusion': 0.85,
            'content': 0.75,
            'general': 0.6,
            'default': 0.5  # For unknown section types
        }
        
        # Dynamic job intent to section type mapping - universal patterns
        self.intent_section_preference = {
            'comprehensive_review': ['methodology', 'results', 'discussion', 'conclusion', 'introduction'],
            'summary': ['abstract', 'summary', 'conclusion', 'overview'],
            'comparison': ['results', 'discussion', 'analysis', 'evaluation'],
            'analysis': ['results', 'discussion', 'methodology', 'data'],
            'extraction': ['methodology', 'content', 'details', 'information'],
            'preparation': ['introduction', 'summary', 'overview', 'background'],
            'implementation': ['methodology', 'procedure', 'process', 'steps'],
            'optimization': ['results', 'performance', 'analysis', 'evaluation']
        }
    
    def rank_sections(self, sections: List[ExtractedSection], 
                     persona_context: PersonaContext) -> List[RankedSection]:
        """
        Rank sections using optimized rule-based approach.
        
        Args:
            sections: List of extracted sections
            persona_context: Analyzed persona context
            
        Returns:
            List of ranked sections sorted by importance
        """
        logger.info(f"🎯 Optimized ranking of {len(sections)} sections for persona: {persona_context.role}")
        
        if not sections:
            return []
        
        # Calculate ranking factors for all sections
        ranked_sections = []
        
        for section in sections:
            ranked_section = self._calculate_section_ranking(section, persona_context, sections)
            ranked_sections.append(ranked_section)
        
        # Sort by final score (descending)
        ranked_sections.sort(key=lambda x: x.final_score, reverse=True)
        
        # Assign importance ranks
        for i, section in enumerate(ranked_sections):
            section.importance_rank = i + 1
        
        logger.info(f"✅ Optimized ranking complete: {len(ranked_sections)} sections")
        logger.info(f"📊 Top section score: {ranked_sections[0].final_score:.3f}")
        logger.info(f"📊 Average score: {sum(s.final_score for s in ranked_sections) / len(ranked_sections):.3f}")
        
        return ranked_sections
    
    def _calculate_section_ranking(self, section: ExtractedSection, 
                                  persona_context: PersonaContext,
                                  all_sections: List[ExtractedSection]) -> RankedSection:
        """Calculate comprehensive ranking for a single section."""
        
        # Base relevance score (already calculated in content extractor)
        relevance_score = section.relevance_score
        
        # Calculate diversity bonus
        diversity_bonus = self._calculate_diversity_bonus(section, all_sections)
        
        # Calculate coverage score
        coverage_score = self._calculate_coverage_score(section, persona_context)
        
        # Calculate section type importance
        section_type_score = self.section_importance.get(section.section_type, 0.5)
        
        # Apply job intent preference
        intent_bonus = self._calculate_intent_bonus(section, persona_context)
        section_type_score += intent_bonus
        
        # Calculate length bonus (moderate length preferred)
        length_score = self._calculate_length_score(section)
        
        # Calculate priority boost for target sections (WINNING FACTOR)
        priority_boost = self._calculate_priority_boost(section, persona_context)
        
        # Combine scores using weights
        final_score = (
            relevance_score * self.weights['relevance'] +
            diversity_bonus * self.weights['diversity'] +
            coverage_score * self.weights['coverage'] +
            section_type_score * self.weights['section_type'] +
            length_score * self.weights['length'] +
            priority_boost  # Add priority boost directly to final score
        )
        
        # Store ranking factors for analysis
        ranking_factors = {
            'relevance': relevance_score,
            'diversity': diversity_bonus,
            'coverage': coverage_score,
            'section_type': section_type_score,
            'length': length_score,
            'intent_bonus': intent_bonus,
            'priority_boost': priority_boost
        }
        
        return RankedSection(
            document=section.document,
            page_number=section.page_number,
            section_title=section.section_title,
            content=section.content,
            content_preview=section.content_preview,
            importance_rank=0,  # Will be set after sorting
            relevance_score=relevance_score,
            diversity_bonus=diversity_bonus,
            coverage_score=coverage_score,
            final_score=final_score,
            word_count=section.word_count,
            char_count=section.char_count,
            section_type=section.section_type,
            key_concepts=section.key_concepts,
            ranking_factors=ranking_factors
        )
    
    def _calculate_diversity_bonus(self, section: ExtractedSection, 
                                  all_sections: List[ExtractedSection]) -> float:
        """Calculate diversity bonus based on content uniqueness."""
        if len(all_sections) <= 1:
            return 1.0
        
        # Calculate similarity with other sections
        similarities = []
        for other_section in all_sections:
            if other_section != section:
                similarity = calculate_text_similarity(section.content, other_section.content)
                similarities.append(similarity)
        
        if not similarities:
            return 1.0
        
        # Diversity bonus = 1 - average similarity
        avg_similarity = sum(similarities) / len(similarities)
        diversity_bonus = 1.0 - avg_similarity
        
        return max(0.0, min(1.0, diversity_bonus))
    
    def _calculate_coverage_score(self, section: ExtractedSection, 
                                 persona_context: PersonaContext) -> float:
        """Calculate how well the section covers important topics."""
        if not persona_context.priority_topics:
            return 0.5
        
        content_lower = section.content.lower()
        
        # Count topic coverage
        covered_topics = 0
        for topic in persona_context.priority_topics:
            if topic.lower() in content_lower:
                covered_topics += 1
        
        # Coverage score based on proportion of topics covered
        coverage_score = covered_topics / len(persona_context.priority_topics)
        
        # Bonus for covering multiple topics
        if covered_topics > 1:
            coverage_score *= 1.1
        
        return min(1.0, coverage_score)
    
    def _calculate_intent_bonus(self, section: ExtractedSection, 
                               persona_context: PersonaContext) -> float:
        """Calculate bonus based on job intent and section type alignment."""
        job_intent = persona_context.job_intent
        section_type = section.section_type
        
        if job_intent in self.intent_section_preference:
            preferred_sections = self.intent_section_preference[job_intent]
            
            if section_type in preferred_sections:
                # Higher bonus for earlier in preference list
                index = preferred_sections.index(section_type)
                bonus = 0.3 * (1.0 - index / len(preferred_sections))
                return bonus
        
        return 0.0
    
    def _calculate_length_score(self, section: ExtractedSection) -> float:
        """Calculate length score favoring moderate-length sections."""
        word_count = section.word_count
        
        # Optimal range: 50-300 words
        if 50 <= word_count <= 300:
            return 1.0
        elif word_count < 50:
            # Penalty for very short sections
            return word_count / 50.0
        else:
            # Diminishing returns for very long sections
            return 1.0 - min(0.5, (word_count - 300) / 1000.0)
    
    def _calculate_priority_boost(self, section: ExtractedSection, persona_context: PersonaContext) -> float:
        """
        Enhanced priority boost with universal content quality detection.
        
        Improvements for better F1 score (domain-agnostic):
        - Better content relevance scoring
        - Universal quality indicators
        - Improved persona-job matching
        
        Returns:
            Priority boost score (0.0 to 10.0)
        """
        content = section.content.lower()
        title = section.section_title.lower()
        
        # IMPROVEMENT 1: Universal quality indicators (not domain-specific)
        quality_boost = 0.0
        
        # High-quality content indicators (universal)
        quality_indicators = [
            ('specific examples', 1.5),
            ('detailed information', 1.2),
            ('step-by-step', 2.0),
            ('comprehensive', 1.0),
            ('practical', 1.5),
            ('essential', 1.3),
            ('important', 1.0),
            ('key', 1.2),
            ('critical', 1.4),
            ('main', 1.1),
            ('primary', 1.1),
            ('best', 1.3)
        ]
        
        for indicator, boost in quality_indicators:
            if indicator in content or indicator in title:
                quality_boost += boost
        
        # IMPROVEMENT 2: Enhanced persona-job matching (universal)
        relevance_boost = 0.0
        
        # Extract job context keywords universally
        job_keywords = []
        if persona_context.job_keywords:
            job_keywords.extend(persona_context.job_keywords[:10])  # Top 10 relevant keywords
        
        # Add persona-related keywords
        if persona_context.role:
            role_words = persona_context.role.lower().split()
            job_keywords.extend([word for word in role_words if len(word) > 3])
        
        # Calculate relevance based on keyword presence
        keyword_matches = 0
        for keyword in job_keywords:
            if keyword in content:
                keyword_matches += 2  # Content match
            if keyword in title:
                keyword_matches += 3  # Title match (more important)
        
        relevance_boost = min(4.0, keyword_matches * 0.3)
        
        # IMPROVEMENT 3: Content structure scoring (universal)
        structure_boost = 0.0
        
        # Well-structured content indicators
        if len(content.split('\n')) > 3:  # Multi-paragraph content
            structure_boost += 0.5
        if '•' in content or '-' in content:  # Lists/bullets
            structure_boost += 0.8
        if any(num in content for num in ['1.', '2.', '3.']):  # Numbered lists
            structure_boost += 1.0
        if len(content.split()) > 50:  # Substantial content
            structure_boost += 0.7
        
        # IMPROVEMENT 4: Position and document context (universal)
        context_boost = 0.0
        
        # Early pages often have important content
        if section.page_number <= 3:
            context_boost += 1.0
        elif section.page_number <= 6:
            context_boost += 0.5
            
        # Document filename relevance (universal pattern)
        if hasattr(section, 'document'):
            doc_name = section.document.lower()
            for keyword in job_keywords[:5]:  # Top keywords only
                if keyword in doc_name:
                    context_boost += 0.8
        
        # IMPROVEMENT 5: Avoid over-generic content (universal)
        generic_penalty = 0.0
        generic_patterns = [
            'general overview', 'introduction to', 'background information',
            'theoretical framework', 'abstract concepts', 'preliminary discussion'
        ]
        
        for pattern in generic_patterns:
            if pattern in title:
                generic_penalty = -1.0  # Moderate penalty for generic titles
                break
        
        # Combine all improvements
        total_boost = quality_boost + relevance_boost + structure_boost + context_boost + generic_penalty
        
        # Cap the boost to reasonable range
        return max(0.0, min(10.0, total_boost))
    
    def _calculate_relevance_score(self, section: ExtractedSection, persona_context: PersonaContext) -> float:
        """
        Calculate enhanced relevance score using universal content analysis.
        
        Returns:
            Relevance score (0.0 to 1.0)
        """
        content = section.content.lower()
        title = section.section_title.lower()
        
        # Universal relevance indicators
        relevance_score = 0.0
        
        # 1. Persona role matching
        if persona_context.role:
            role_words = persona_context.role.lower().split()
            for word in role_words:
                if len(word) > 3:  # Skip short words
                    if word in content:
                        relevance_score += 0.1
                    if word in title:
                        relevance_score += 0.2
        
        # 2. Job keywords matching (use job_keywords instead of job_description)
        if persona_context.job_keywords:
            for keyword in persona_context.job_keywords:
                if len(keyword) > 3:  # Skip short words
                    if keyword.lower() in content:
                        relevance_score += 0.05
                    if keyword.lower() in title:
                        relevance_score += 0.1
        
        # 3. Content quality indicators
        if len(content.split()) > 30:  # Substantial content
            relevance_score += 0.1
        if any(char in content for char in ['•', '-', '1.', '2.']):  # Structured content
            relevance_score += 0.1
        
        # Cap at 1.0
        return min(1.0, relevance_score)
    
    def filter_top_sections(self, ranked_sections: List[RankedSection], 
                           max_sections: int = 15,
                           min_score_threshold: float = 0.3) -> List[RankedSection]:
        """
        Filter to top sections based on score and count limits.
        
        Args:
            ranked_sections: List of ranked sections
            max_sections: Maximum number of sections to return
            min_score_threshold: Minimum score threshold
            
        Returns:
            Filtered list of top sections
        """
        # Filter by minimum score
        filtered = [s for s in ranked_sections if s.final_score >= min_score_threshold]
        
        # Ensure diversity across documents
        filtered = self._ensure_document_diversity(filtered, max_sections)
        
        # Limit to max sections
        return filtered[:max_sections]
    
    def _ensure_document_diversity(self, sections: List[RankedSection], 
                                  max_sections: int) -> List[RankedSection]:
        """Ensure representation from multiple documents."""
        if len(sections) <= max_sections:
            return sections
        
        # Group by document
        by_document = defaultdict(list)
        for section in sections:
            by_document[section.document].append(section)
        
        # Calculate sections per document
        num_documents = len(by_document)
        base_per_doc = max_sections // num_documents
        remainder = max_sections % num_documents
        
        result = []
        
        # Take sections from each document
        for i, (doc, doc_sections) in enumerate(by_document.items()):
            # Give extra section to first 'remainder' documents
            sections_for_doc = base_per_doc + (1 if i < remainder else 0)
            result.extend(doc_sections[:sections_for_doc])
        
        # Sort the result by final score again
        result.sort(key=lambda x: x.final_score, reverse=True)
        
        return result
    
    def get_ranking_summary(self, ranked_sections: List[RankedSection]) -> Dict[str, Any]:
        """Generate summary statistics for the ranking results."""
        if not ranked_sections:
            return {}
        
        # Score statistics
        scores = [s.final_score for s in ranked_sections]
        
        # Document distribution
        doc_counts = defaultdict(int)
        for section in ranked_sections:
            doc_counts[section.document] += 1
        
        # Section type distribution
        type_counts = defaultdict(int)
        for section in ranked_sections:
            type_counts[section.section_type] += 1
        
        # Ranking factors analysis
        factor_averages = defaultdict(list)
        for section in ranked_sections:
            for factor, value in section.ranking_factors.items():
                factor_averages[factor].append(value)
        
        factor_stats = {}
        for factor, values in factor_averages.items():
            factor_stats[factor] = {
                'average': sum(values) / len(values),
                'max': max(values),
                'min': min(values)
            }
        
        return {
            'total_sections': len(ranked_sections),
            'score_statistics': {
                'average': sum(scores) / len(scores),
                'max': max(scores),
                'min': min(scores),
                'range': max(scores) - min(scores)
            },
            'document_distribution': dict(doc_counts),
            'section_type_distribution': dict(type_counts),
            'ranking_factor_statistics': factor_stats,
            'top_3_scores': scores[:3] if len(scores) >= 3 else scores
        }
