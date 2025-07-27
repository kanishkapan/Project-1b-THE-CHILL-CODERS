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
        
        # Dynamic domain keyword extraction - no hardcoded domains
        self.common_stopwords = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'here', 'there', 'where', 'when', 'why', 'how'
        }
        
        # Dynamic job intent patterns - flexible for any domain
        self.intent_patterns = {
            'comprehensive_review': ['comprehensive', 'complete', 'thorough', 'detailed', 'full', 'extensive', 'in-depth'],
            'summary': ['summarize', 'overview', 'brief', 'key points', 'main', 'highlights', 'synopsis'],
            'comparison': ['compare', 'contrast', 'versus', 'difference', 'similar', 'evaluate', 'assessment'],
            'analysis': ['analyze', 'examine', 'evaluate', 'assess', 'investigate', 'study', 'research'],
            'extraction': ['extract', 'identify', 'find', 'locate', 'list', 'collect', 'gather'],
            'preparation': ['prepare', 'study', 'learn', 'understand', 'review', 'plan', 'develop', 'create', 'design'],
            'implementation': ['implement', 'execute', 'apply', 'build', 'construct', 'develop'],
            'optimization': ['optimize', 'improve', 'enhance', 'maximize', 'minimize', 'streamline']
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
        """Extract the domain/field from persona description using dynamic NLP."""
        if not persona.strip():
            return "general"
            
        # Extract meaningful keywords from persona using NLP
        domain_keywords = self._extract_domain_keywords(persona)
        
        if domain_keywords:
            # Return the most prominent domain keyword as the domain
            return domain_keywords[0].lower()
        
        # Fallback: extract specific field mentions using patterns
        field_patterns = [
            r'in\s+([a-zA-Z\s]+?)(?:\s|$)',
            r'of\s+([a-zA-Z\s]+?)(?:\s|$)',
            r'([a-zA-Z]+)\s+(?:specialist|expert|professional|analyst|researcher|student|manager|director)'
        ]
        
        persona_lower = persona.lower()
        for pattern in field_patterns:
            match = re.search(pattern, persona_lower)
            if match:
                field = match.group(1).strip()
                if len(field.split()) <= 3 and len(field) > 2:  # Reasonable field name
                    return field.replace(' ', '_')
        
        return "general"
    
    def _extract_domain_keywords(self, text: str) -> List[str]:
        """Extract domain-specific keywords using NLP."""
        keywords = []
        
        if self.nlp:
            doc = self.nlp(text)
            # Extract nouns, proper nouns, and adjectives that could indicate domain
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                    len(token.text) > 2 and 
                    token.text.lower() not in self.common_stopwords and
                    not token.is_punct and not token.is_space):
                    keywords.append(token.lemma_)
        else:
            # Fallback: simple word extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
            keywords = [word for word in words if word.lower() not in self.common_stopwords]
        
        return keywords[:5]  # Return top 5 keywords
    
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
        """Determine priority topics dynamically from persona and job description."""
        priority_topics = []
        
        # Extract keywords directly from the combined text using NLP
        combined_text = f"{persona} {job_description}"
        
        if self.nlp:
            doc = self.nlp(combined_text)
            
            # Extract important nouns and entities
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    len(token.text) > 2 and
                    token.text.lower() not in self.common_stopwords and
                    not token.is_punct and not token.is_space):
                    priority_topics.append(token.lemma_.lower())
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'TECHNOLOGY', 'NORP']:
                    priority_topics.append(ent.text.lower())
            
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if 2 <= len(chunk.text.split()) <= 3:
                    priority_topics.append(chunk.text.lower())
        
        # Fallback: use keyword extraction utility
        keywords = extract_keywords(combined_text, max_keywords=15)
        priority_topics.extend([kw.lower() for kw in keywords])
        
        # Remove duplicates and filter out very short terms
        unique_topics = list(set(priority_topics))
        filtered_topics = [topic for topic in unique_topics if len(topic) > 2]
        
        return filtered_topics[:20]  # Return top 20 priority topics
    
    def _identify_relevant_sections(self, job_intent: str, domain: str) -> List[str]:
        """Identify types of sections that are most relevant based on job intent."""
        # Base section mapping - these are universal across domains
        section_mapping = {
            'comprehensive_review': ['methodology', 'results', 'discussion', 'conclusion', 'introduction', 'analysis'],
            'summary': ['abstract', 'summary', 'conclusion', 'key findings', 'overview', 'highlights'],
            'comparison': ['results', 'analysis', 'comparison', 'evaluation', 'performance', 'assessment'],
            'analysis': ['analysis', 'results', 'data', 'findings', 'discussion', 'evaluation'],
            'extraction': ['methodology', 'approach', 'implementation', 'procedure', 'methods', 'techniques'],
            'preparation': ['introduction', 'background', 'concepts', 'principles', 'theory', 'fundamentals'],
            'implementation': ['procedure', 'steps', 'process', 'implementation', 'execution', 'application'],
            'optimization': ['improvement', 'optimization', 'enhancement', 'performance', 'efficiency']
        }
        
        # Get base relevant sections for the job intent
        relevant_sections = section_mapping.get(job_intent, ['introduction', 'results', 'conclusion'])
        
        # Add universal section types that are generally useful
        universal_sections = ['overview', 'summary', 'key points', 'important', 'main', 'primary']
        relevant_sections.extend(universal_sections)
        
        return list(set(relevant_sections))[:15]  # Limit to 15 most relevant section types
    
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
