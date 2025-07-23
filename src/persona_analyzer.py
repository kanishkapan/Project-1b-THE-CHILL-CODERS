"""
Persona Analyzer Module
Analyzes persona definitions and job-to-be-done to create context for content extraction.
Uses lightweight NLP models optimized for CPU execution.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from src.utils import extract_keywords, clean_text

logger = logging.getLogger(__name__)

@dataclass
class PersonaContext:
    """Data class to hold analyzed persona information."""
    role: str
    domain: str
    expertise_areas: List[str]
    job_keywords: List[str]
    job_intent: str
    priority_topics: List[str]
    relevant_sections: List[str]
    analysis_depth: str  # 'comprehensive', 'focused', 'overview'

class PersonaAnalyzer:
    """
    Analyzes persona and job-to-be-done to create extraction context.
    Uses lightweight NLP for CPU-only execution.
    """
    
    def __init__(self):
        """Initialize the persona analyzer with lightweight models."""
        self.nlp = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            max_df=0.8,
            min_df=2
        )
        self._load_models()
        
        # Domain-specific keyword mappings
        self.domain_keywords = {
            'research': ['methodology', 'literature', 'analysis', 'study', 'findings', 'results', 'conclusion'],
            'business': ['revenue', 'strategy', 'market', 'performance', 'growth', 'analysis', 'trends'],
            'education': ['concepts', 'principles', 'examples', 'exercises', 'theory', 'practice', 'learning'],
            'technical': ['implementation', 'architecture', 'specifications', 'documentation', 'procedures'],
            'finance': ['financial', 'investment', 'returns', 'risk', 'portfolio', 'market', 'analysis']
        }
        
        # Job intent patterns
        self.intent_patterns = {
            'comprehensive_review': ['comprehensive', 'complete', 'thorough', 'detailed', 'full'],
            'summary': ['summarize', 'overview', 'brief', 'key points', 'main'],
            'comparison': ['compare', 'contrast', 'versus', 'difference', 'similar'],
            'analysis': ['analyze', 'examine', 'evaluate', 'assess', 'investigate'],
            'extraction': ['extract', 'identify', 'find', 'locate', 'list'],
            'preparation': ['prepare', 'study', 'learn', 'understand', 'review']
        }
    
    def _load_models(self):
        """Load lightweight NLP models."""
        try:
            # Load spaCy model (small, CPU-optimized)
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ Loaded spaCy model successfully")
        except OSError:
            logger.warning("⚠️  spaCy model not found, using fallback processing")
            self.nlp = None
    
    def analyze_persona(self, persona: str, job_description: str) -> PersonaContext:
        """
        Analyze persona and job description to create extraction context.
        
        Args:
            persona: Persona description (e.g., "PhD Researcher in Computational Biology")
            job_description: Job-to-be-done (e.g., "Prepare comprehensive literature review")
            
        Returns:
            PersonaContext with analyzed information
        """
        logger.info(f"Analyzing persona: {persona}")
        logger.info(f"Job description: {job_description}")
        
        # Clean inputs
        persona_clean = clean_text(persona)
        job_clean = clean_text(job_description)
        
        # Extract role and domain
        role = self._extract_role(persona_clean)
        domain = self._extract_domain(persona_clean)
        
        # Extract expertise areas
        expertise_areas = self._extract_expertise_areas(persona_clean)
        
        # Analyze job intent and keywords
        job_intent = self._analyze_job_intent(job_clean)
        job_keywords = self._extract_job_keywords(job_clean)
        
        # Determine priority topics
        priority_topics = self._determine_priority_topics(persona_clean, job_clean, domain)
        
        # Identify relevant section types
        relevant_sections = self._identify_relevant_sections(job_intent, domain)
        
        # Determine analysis depth
        analysis_depth = self._determine_analysis_depth(job_clean)
        
        context = PersonaContext(
            role=role,
            domain=domain,
            expertise_areas=expertise_areas,
            job_keywords=job_keywords,
            job_intent=job_intent,
            priority_topics=priority_topics,
            relevant_sections=relevant_sections,
            analysis_depth=analysis_depth
        )
        
        logger.info(f"✅ Persona analysis complete: {role} in {domain}")
        logger.info(f"📋 Job intent: {job_intent}, Analysis depth: {analysis_depth}")
        
        return context
    
    def _extract_role(self, persona: str) -> str:
        """Extract the primary role from persona description."""
        # Common role patterns
        role_patterns = [
            r'(phd|doctoral|postdoc|graduate)\s+(?:student|researcher)',
            r'(undergraduate|bachelor|masters?)\s+student',
            r'(researcher|scientist|analyst|engineer|developer)',
            r'(professor|instructor|teacher|lecturer)',
            r'(manager|director|executive|lead)',
            r'(consultant|advisor|specialist)',
            r'(student|learner|trainee)'
        ]
        
        persona_lower = persona.lower()
        
        for pattern in role_patterns:
            match = re.search(pattern, persona_lower)
            if match:
                return match.group(0).title()
        
        # Fallback: extract first noun-like word
        words = persona.split()
        for word in words:
            if len(word) > 3 and word.lower() not in ['the', 'and', 'or', 'in', 'at', 'for']:
                return word.title()
        
        return "Professional"
    
    def _extract_domain(self, persona: str) -> str:
        """Extract the domain/field from persona description."""
        # Domain keywords mapping
        domain_mapping = {
            'research': ['research', 'academic', 'scientific', 'study'],
            'business': ['business', 'financial', 'investment', 'corporate', 'commercial'],
            'education': ['education', 'student', 'learning', 'academic', 'school', 'university'],
            'technical': ['technical', 'engineering', 'software', 'computer', 'technology'],
            'medical': ['medical', 'healthcare', 'clinical', 'pharmaceutical', 'biology'],
            'finance': ['finance', 'banking', 'investment', 'economic', 'financial']
        }
        
        persona_lower = persona.lower()
        
        for domain, keywords in domain_mapping.items():
            if any(keyword in persona_lower for keyword in keywords):
                return domain
        
        # Try to extract specific field mentions
        field_patterns = [
            r'in\s+([a-zA-Z\s]+?)(?:\s|$)',
            r'of\s+([a-zA-Z\s]+?)(?:\s|$)',
            r'([a-zA-Z]+)\s+(?:researcher|analyst|student)'
        ]
        
        for pattern in field_patterns:
            match = re.search(pattern, persona_lower)
            if match:
                field = match.group(1).strip()
                if len(field.split()) <= 3:  # Reasonable field name length
                    return field.title()
        
        return "general"
    
    def _extract_expertise_areas(self, persona: str) -> List[str]:
        """Extract specific expertise areas from persona."""
        expertise_areas = []
        
        # Look for specific mentions
        expertise_patterns = [
            r'specializ(?:ing|ed)\s+in\s+([^,.]+)',
            r'expert\s+in\s+([^,.]+)',
            r'focus(?:ing|ed)\s+on\s+([^,.]+)',
            r'working\s+(?:in|on)\s+([^,.]+)'
        ]
        
        persona_lower = persona.lower()
        
        for pattern in expertise_patterns:
            matches = re.findall(pattern, persona_lower)
            expertise_areas.extend([match.strip().title() for match in matches])
        
        # Extract field-specific keywords
        if self.nlp:
            doc = self.nlp(persona)
            # Extract named entities and noun phrases
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'TECHNOLOGY']:
                    expertise_areas.append(ent.text)
            
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:
                    expertise_areas.append(chunk.text.title())
        
        # Remove duplicates and filter
        expertise_areas = list(set(expertise_areas))
        expertise_areas = [area for area in expertise_areas if len(area) > 3]
        
        return expertise_areas[:10]  # Limit to top 10
    
    def _analyze_job_intent(self, job_description: str) -> str:
        """Analyze the intent behind the job-to-be-done."""
        job_lower = job_description.lower()
        
        # Check for intent patterns
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in job_lower for pattern in patterns):
                return intent
        
        # Default intent based on common verbs
        if any(verb in job_lower for verb in ['prepare', 'create', 'write']):
            return 'preparation'
        elif any(verb in job_lower for verb in ['understand', 'learn', 'study']):
            return 'learning'
        else:
            return 'analysis'
    
    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract important keywords from job description."""
        # Use utility function to extract keywords
        keywords = extract_keywords(job_description, max_keywords=15)
        
        # Add domain-specific keywords if NLP is available
        if self.nlp:
            doc = self.nlp(job_description)
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'TECHNOLOGY']:
                    keywords.append(ent.text.lower())
            
            # Extract important noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:
                    keywords.append(chunk.text.lower())
        
        # Remove duplicates and return
        return list(set(keywords))[:20]
    
    def _determine_priority_topics(self, persona: str, job_description: str, domain: str) -> List[str]:
        """Determine priority topics based on persona and job."""
        priority_topics = []
        
        # Add domain-specific keywords
        if domain in self.domain_keywords:
            priority_topics.extend(self.domain_keywords[domain])
        
        # Extract specific topics from job description
        combined_text = f"{persona} {job_description}"
        keywords = extract_keywords(combined_text, max_keywords=10)
        priority_topics.extend(keywords)
        
        # Remove duplicates
        return list(set(priority_topics))[:15]
    
    def _identify_relevant_sections(self, job_intent: str, domain: str) -> List[str]:
        """Identify types of sections that are most relevant."""
        section_mapping = {
            'comprehensive_review': ['methodology', 'results', 'discussion', 'conclusion', 'introduction'],
            'summary': ['abstract', 'summary', 'conclusion', 'key findings', 'overview'],
            'comparison': ['results', 'analysis', 'comparison', 'evaluation', 'performance'],
            'analysis': ['analysis', 'results', 'data', 'findings', 'discussion'],
            'extraction': ['methodology', 'approach', 'implementation', 'procedure'],
            'preparation': ['introduction', 'background', 'concepts', 'principles', 'theory']
        }
        
        relevant_sections = section_mapping.get(job_intent, ['introduction', 'results', 'conclusion'])
        
        # Add domain-specific sections
        domain_sections = {
            'research': ['literature review', 'methodology', 'results', 'discussion'],
            'business': ['executive summary', 'financial analysis', 'market analysis', 'strategy'],
            'education': ['concepts', 'examples', 'exercises', 'summary'],
            'technical': ['specifications', 'implementation', 'architecture', 'procedures']
        }
        
        if domain in domain_sections:
            relevant_sections.extend(domain_sections[domain])
        
        return list(set(relevant_sections))
    
    def _determine_analysis_depth(self, job_description: str) -> str:
        """Determine the required depth of analysis."""
        job_lower = job_description.lower()
        
        if any(word in job_lower for word in ['comprehensive', 'detailed', 'thorough', 'complete', 'full']):
            return 'comprehensive'
        elif any(word in job_lower for word in ['brief', 'summary', 'overview', 'quick', 'key']):
            return 'overview'
        else:
            return 'focused'
    
    def calculate_relevance_score(self, text: str, context: PersonaContext) -> float:
        """
        Calculate relevance score for a text segment based on persona context.
        
        Args:
            text: Text to score
            context: Persona context
            
        Returns:
            Relevance score between 0 and 1
        """
        if not text.strip():
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        # Score based on job keywords
        job_keyword_matches = sum(1 for keyword in context.job_keywords if keyword in text_lower)
        score += (job_keyword_matches / max(len(context.job_keywords), 1)) * 0.3
        
        # Score based on priority topics
        topic_matches = sum(1 for topic in context.priority_topics if topic in text_lower)
        score += (topic_matches / max(len(context.priority_topics), 1)) * 0.3
        
        # Score based on expertise areas
        expertise_matches = sum(1 for area in context.expertise_areas if area.lower() in text_lower)
        score += (expertise_matches / max(len(context.expertise_areas), 1)) * 0.2
        
        # Score based on relevant section types
        section_matches = sum(1 for section in context.relevant_sections if section in text_lower)
        score += (section_matches / max(len(context.relevant_sections), 1)) * 0.2
        
        # Normalize score to 0-1 range
        return min(score, 1.0)
