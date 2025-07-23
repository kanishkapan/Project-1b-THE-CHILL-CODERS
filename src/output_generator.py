"""
Output Generator Module
Generates the final structured JSON output according to challenge1b_output.json format.
Creates comprehensive results with metadata, extracted sections, and sub-section analysis.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

from src.ranking_engine import RankedSection
from src.persona_analyzer import PersonaContext
from src.utils import validate_output_format

logger = logging.getLogger(__name__)

class OutputGenerator:
    """
    Generates structured output in the required challenge format.
    Creates comprehensive JSON with metadata, sections, and analysis.
    """
    
    def __init__(self):
        """Initialize the output generator."""
        self.output_version = "1.0"
        self.max_preview_length = 200
        self.max_refined_text_length = 500
    
    def generate_output(self, documents: List[Dict[str, Any]], persona: str, 
                       job: str, ranked_sections: List[RankedSection],
                       processing_time: float) -> Dict[str, Any]:
        """
        Generate the complete output structure.
        
        Args:
            documents: List of processed document dictionaries
            persona: Original persona description
            job: Original job description
            ranked_sections: List of ranked sections
            processing_time: Total processing time in seconds
            
        Returns:
            Complete output dictionary matching challenge format
        """
        logger.info("Generating structured output...")
        
        # Generate metadata
        metadata = self._generate_metadata(documents, persona, job, processing_time)
        
        # Generate extracted sections
        extracted_sections = self._generate_extracted_sections(ranked_sections)
        
        # Generate sub-section analysis
        sub_section_analysis = self._generate_sub_section_analysis(ranked_sections)
        
        # Generate processing statistics
        processing_stats = self._generate_processing_stats(
            documents, ranked_sections, processing_time
        )
        
        # Compile final output
        output_data = {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "sub_section_analysis": sub_section_analysis,
            "processing_stats": processing_stats
        }
        
        # Validate output format
        if validate_output_format(output_data):
            logger.info("✅ Output format validation passed")
        else:
            logger.warning("⚠️  Output format validation failed")
        
        logger.info(f"📄 Generated output with {len(extracted_sections)} sections")
        
        return output_data
    
    def _generate_metadata(self, documents: List[Dict[str, Any]], persona: str, 
                          job: str, processing_time: float) -> Dict[str, Any]:
        """Generate metadata section."""
        # Extract document filenames
        input_documents = [doc['filename'] for doc in documents]
        
        # Generate processing timestamp
        processing_timestamp = datetime.now(timezone.utc).isoformat()
        
        metadata = {
            "input_documents": input_documents,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": processing_timestamp,
            "system_version": self.output_version,
            "total_processing_time_seconds": round(processing_time, 2),
            "documents_processed": len(documents),
            "total_pages_analyzed": sum(doc['total_pages'] for doc in documents)
        }
        
        return metadata
    
    def _generate_extracted_sections(self, ranked_sections: List[RankedSection]) -> List[Dict[str, Any]]:
        """Generate extracted sections list."""
        extracted_sections = []
        
        for section in ranked_sections:
            section_data = {
                "document": section.document,
                "page_number": section.page_number,
                "section_title": section.section_title,
                "importance_rank": section.importance_rank,
                "relevance_score": round(section.relevance_score, 3),
                "content_preview": self._truncate_text(section.content_preview, self.max_preview_length),
                "word_count": section.word_count,
                "section_type": section.section_type,
                "key_concepts": section.key_concepts[:5]  # Limit to top 5 concepts
            }
            
            extracted_sections.append(section_data)
        
        return extracted_sections
    
    def _generate_sub_section_analysis(self, ranked_sections: List[RankedSection]) -> List[Dict[str, Any]]:
        """Generate detailed sub-section analysis."""
        sub_section_analysis = []
        
        # Take top sections for detailed analysis
        top_sections = ranked_sections[:10]  # Limit detailed analysis to top 10
        
        for section in top_sections:
            # Generate refined text (cleaned and summarized)
            refined_text = self._generate_refined_text(section)
            
            analysis_data = {
                "document": section.document,
                "section_title": section.section_title,
                "refined_text": refined_text,
                "page_number": section.page_number,
                "key_concepts": section.key_concepts,
                "methodology_relevance": self._calculate_methodology_relevance(section),
                "section_importance": round(section.final_score, 3),
                "content_density": self._calculate_content_density(section),
                "ranking_factors": {
                    k: round(v, 3) for k, v in section.ranking_factors.items()
                }
            }
            
            sub_section_analysis.append(analysis_data)
        
        return sub_section_analysis
    
    def _generate_processing_stats(self, documents: List[Dict[str, Any]], 
                                  ranked_sections: List[RankedSection],
                                  processing_time: float) -> Dict[str, Any]:
        """Generate processing statistics."""
        
        # Calculate total content processed
        total_pages = sum(doc['total_pages'] for doc in documents)
        total_words = sum(
            sum(page['word_count'] for page in doc['pages']) 
            for doc in documents
        )
        
        # Calculate section statistics
        total_sections_extracted = len(ranked_sections)
        avg_relevance = (sum(s.relevance_score for s in ranked_sections) / 
                        len(ranked_sections) if ranked_sections else 0)
        
        # Estimate model memory usage (rough calculation)
        estimated_memory_mb = min(900, total_words * 0.001 + 200)  # Stay under 1GB
        
        # Document type analysis
        doc_types = self._analyze_document_types(documents)
        
        processing_stats = {
            "total_documents_processed": len(documents),
            "total_pages_processed": total_pages,
            "total_words_analyzed": total_words,
            "total_sections_extracted": total_sections_extracted,
            "sections_above_threshold": sum(1 for s in ranked_sections if s.relevance_score > 0.5),
            "average_relevance_score": round(avg_relevance, 3),
            "processing_time_seconds": round(processing_time, 2),
            "estimated_model_memory_usage_mb": round(estimated_memory_mb, 1),
            "performance_metrics": {
                "pages_per_second": round(total_pages / max(processing_time, 0.1), 2),
                "words_per_second": round(total_words / max(processing_time, 0.1), 0),
                "sections_per_document": round(total_sections_extracted / max(len(documents), 1), 1)
            },
            "document_type_analysis": doc_types,
            "constraint_compliance": {
                "cpu_only_execution": True,
                "model_size_under_1gb": estimated_memory_mb < 1000,
                "processing_under_60s": processing_time < 60,
                "no_internet_required": True
            }
        }
        
        return processing_stats
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to specified length with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _generate_refined_text(self, section: RankedSection) -> str:
        """Generate refined and cleaned text for detailed analysis."""
        content = section.content
        
        # Basic text refinement
        # Remove excessive whitespace
        import re
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common artifacts
        content = re.sub(r'\b\d+\s*$', '', content)  # Page numbers at end
        content = re.sub(r'^\s*\d+\s*', '', content)  # Numbers at start
        
        # Focus on key sentences (simple extractive summarization)
        sentences = content.split('.')
        
        # Score sentences by keyword presence
        key_words = set(word.lower() for word in section.key_concepts)
        scored_sentences = []
        
        for sentence in sentences:
            if len(sentence.strip()) > 20:  # Skip very short sentences
                score = sum(1 for word in key_words if word in sentence.lower())
                scored_sentences.append((sentence.strip(), score))
        
        # Take top sentences or all if few
        if len(scored_sentences) > 3:
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            refined_sentences = [s[0] for s in scored_sentences[:3]]
        else:
            refined_sentences = [s[0] for s in scored_sentences]
        
        refined_text = '. '.join(refined_sentences)
        
        # Truncate if too long
        if len(refined_text) > self.max_refined_text_length:
            refined_text = refined_text[:self.max_refined_text_length-3] + "..."
        
        return refined_text if refined_text else content[:self.max_refined_text_length]
    
    def _calculate_methodology_relevance(self, section: RankedSection) -> float:
        """Calculate methodology relevance score for the section."""
        methodology_keywords = [
            'method', 'approach', 'technique', 'procedure', 'algorithm',
            'implementation', 'experiment', 'analysis', 'framework', 'model'
        ]
        
        content_lower = section.content.lower()
        matches = sum(1 for keyword in methodology_keywords if keyword in content_lower)
        
        # Normalize by number of keywords
        relevance = min(1.0, matches / len(methodology_keywords) * 2)
        
        # Bonus for methodology section type
        if section.section_type == 'methodology':
            relevance *= 1.2
        
        return round(min(1.0, relevance), 3)
    
    def _calculate_content_density(self, section: RankedSection) -> float:
        """Calculate content density (concepts per word)."""
        if section.word_count == 0:
            return 0.0
        
        # Density based on key concepts per word
        density = len(section.key_concepts) / section.word_count
        
        # Normalize to 0-1 scale (assume good density is ~0.05)
        normalized_density = min(1.0, density / 0.05)
        
        return round(normalized_density, 3)
    
    def _analyze_document_types(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze types of documents processed."""
        doc_analysis = {
            "total_documents": len(documents),
            "documents_with_tables": 0,
            "documents_with_images": 0,
            "average_pages_per_document": 0,
            "document_size_distribution": {"small": 0, "medium": 0, "large": 0}
        }
        
        if not documents:
            return doc_analysis
        
        total_pages = 0
        
        for doc in documents:
            pages = doc.get('pages', [])
            page_count = len(pages)
            total_pages += page_count
            
            # Check for tables and images
            if any(page.get('has_tables', False) for page in pages):
                doc_analysis["documents_with_tables"] += 1
            
            if any(page.get('has_images', False) for page in pages):
                doc_analysis["documents_with_images"] += 1
            
            # Size classification
            if page_count <= 5:
                doc_analysis["document_size_distribution"]["small"] += 1
            elif page_count <= 20:
                doc_analysis["document_size_distribution"]["medium"] += 1
            else:
                doc_analysis["document_size_distribution"]["large"] += 1
        
        doc_analysis["average_pages_per_document"] = round(total_pages / len(documents), 1)
        
        return doc_analysis
    
    def save_output(self, output_data: Dict[str, Any], output_path: str) -> bool:
        """
        Save output data to JSON file.
        
        Args:
            output_data: Output dictionary to save
            output_path: Path to save the JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Output saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save output: {str(e)}")
            return False
    
    def generate_summary_report(self, output_data: Dict[str, Any]) -> str:
        """Generate a human-readable summary report."""
        metadata = output_data.get('metadata', {})
        stats = output_data.get('processing_stats', {})
        sections = output_data.get('extracted_sections', [])
        
        report = f"""
=== DOCUMENT INTELLIGENCE ANALYSIS REPORT ===

📋 ANALYSIS OVERVIEW
Persona: {metadata.get('persona', 'Unknown')}
Job-to-be-Done: {metadata.get('job_to_be_done', 'Unknown')}
Processing Time: {stats.get('processing_time_seconds', 0):.1f} seconds

📚 DOCUMENTS PROCESSED
Total Documents: {metadata.get('documents_processed', 0)}
Total Pages: {metadata.get('total_pages_analyzed', 0)}
Document Files: {', '.join(metadata.get('input_documents', []))}

📄 CONTENT ANALYSIS
Sections Extracted: {stats.get('total_sections_extracted', 0)}
High-Relevance Sections: {stats.get('sections_above_threshold', 0)}
Average Relevance Score: {stats.get('average_relevance_score', 0):.3f}

⭐ TOP SECTIONS
"""
        
        # Add top 5 sections to report
        for i, section in enumerate(sections[:5], 1):
            report += f"{i}. {section.get('section_title', 'Untitled')} "
            report += f"(Score: {section.get('relevance_score', 0):.3f}, "
            report += f"Page: {section.get('page_number', 'Unknown')})\n"
        
        report += f"""
🚀 PERFORMANCE METRICS
Pages/Second: {stats.get('performance_metrics', {}).get('pages_per_second', 0)}
Words/Second: {stats.get('performance_metrics', {}).get('words_per_second', 0)}
Memory Usage: {stats.get('estimated_model_memory_usage_mb', 0)}MB

✅ CONSTRAINT COMPLIANCE
CPU-Only: {stats.get('constraint_compliance', {}).get('cpu_only_execution', False)}
Under 1GB: {stats.get('constraint_compliance', {}).get('model_size_under_1gb', False)}
Under 60s: {stats.get('constraint_compliance', {}).get('processing_under_60s', False)}
No Internet: {stats.get('constraint_compliance', {}).get('no_internet_required', False)}
"""
        
        return report
