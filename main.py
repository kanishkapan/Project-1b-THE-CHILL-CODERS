#!/usr/bin/env python3
"""
Persona-Driven Document Intelligence System
Main entry point for processing documents based on persona and job-to-be-done.
"""

import argparse
import json
import time
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

from src.document_processor import DocumentProcessor
from src.persona_analyzer import PersonaAnalyzer
from src.content_extractor import ContentExtractor
from src.ranking_engine import RankingEngine
from src.output_generator import OutputGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Persona-Driven Document Intelligence System')
    parser.add_argument('--documents_dir', required=True, help='Directory containing PDF documents')
    parser.add_argument('--persona', required=True, help='Persona description')
    parser.add_argument('--job', required=True, help='Job-to-be-done description')
    parser.add_argument('--output_dir', default='./output', help='Output directory for results')
    parser.add_argument('--output_file', default='results.json', help='Output JSON filename')
    parser.add_argument('--max_documents', type=int, default=10, help='Maximum number of documents to process')
    
    args = parser.parse_args()
    
    # Start timer
    start_time = time.time()
    
    try:
        # Initialize components
        logger.info("Initializing document intelligence system...")
        document_processor = DocumentProcessor()
        persona_analyzer = PersonaAnalyzer()
        content_extractor = ContentExtractor()
        ranking_engine = RankingEngine()
        output_generator = OutputGenerator()
        
        # Process documents
        logger.info(f"Processing documents from: {args.documents_dir}")
        documents = document_processor.load_documents(args.documents_dir, max_docs=args.max_documents)
        
        if not documents:
            logger.error("No PDF documents found in the specified directory")
            return
        
        logger.info(f"Found {len(documents)} documents to process")
        
        # Analyze persona and job
        logger.info("Analyzing persona and job requirements...")
        persona_context = persona_analyzer.analyze_persona(args.persona, args.job)
        
        # Extract content from documents
        logger.info("Extracting relevant content from documents...")
        extracted_sections = []
        for doc in documents:
            sections = content_extractor.extract_sections(doc, persona_context)
            extracted_sections.extend(sections)
        
        logger.info(f"Extracted {len(extracted_sections)} sections")
        
        # Rank sections by relevance
        logger.info("Ranking sections by relevance...")
        ranked_sections = ranking_engine.rank_sections(extracted_sections, persona_context)
        
        # Filter to top sections
        top_sections = ranking_engine.filter_top_sections(
            ranked_sections, 
            max_sections=15, 
            min_score_threshold=0.2
        )
        
        logger.info(f"Selected {len(top_sections)} top sections for output")
        
        # Generate output
        logger.info("Generating structured output...")
        output_data = output_generator.generate_output(
            documents=documents,
            persona=args.persona,
            job=args.job,
            ranked_sections=top_sections,
            processing_time=time.time() - start_time
        )
        
        # Save results
        output_path = Path(args.output_dir) / args.output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        logger.info(f"Results saved to: {output_path}")
        
        # Verify constraints
        if processing_time > 60:
            logger.warning(f"Processing time ({processing_time:.2f}s) exceeded 60-second constraint")
        else:
            logger.info(f"✅ Processing time constraint met: {processing_time:.2f}s")
        
        print(f"\n🎉 Document intelligence processing completed successfully!")
        print(f"📊 Processed {len(documents)} documents in {processing_time:.2f} seconds")
        print(f"📄 Results saved to: {output_path}")
        print(f"⭐ Found {len(top_sections)} highly relevant sections")
        print(f"🔍 Average relevance score: {sum(s.relevance_score for s in top_sections) / len(top_sections):.3f}")
        
        # Generate and display summary report
        summary_report = output_generator.generate_summary_report(output_data)
        print(summary_report)
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    main()
