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
    parser.add_argument('--documents_dir', help='Directory containing PDF documents')
    parser.add_argument('--persona', help='Persona description')
    parser.add_argument('--job', help='Job-to-be-done description')
    parser.add_argument('--input_json', help='JSON input file with challenge info')
    parser.add_argument('--output_dir', default='./output', help='Output directory for results')
    parser.add_argument('--output_file', default='results.json', help='Output JSON filename')
    parser.add_argument('--max_documents', type=int, default=10, help='Maximum number of documents to process')
    
    args = parser.parse_args()
    
    # Handle JSON input format
    input_data = None
    if args.input_json:
        with open(args.input_json, 'r') as f:
            input_data = json.load(f)
        
        # Extract parameters from JSON
        if not args.documents_dir:
            args.documents_dir = 'sample_docs'  # Default documents directory
        if not args.persona:
            args.persona = input_data['persona']['role']
        if not args.job:
            args.job = input_data['job_to_be_done']['task']
        if args.output_file == 'results.json':
            args.output_file = f"{input_data['challenge_info']['test_case_name']}_output.json"
    
    # Validate required arguments after potential JSON override
    if not args.documents_dir:
        parser.error("Missing --documents_dir")
    if not args.persona:
        parser.error("Missing --persona (provide via --persona or --input_json)")
    if not args.job:
        parser.error("Missing --job (provide via --job or --input_json)")
    
    # Remove the second parse_args() call that was causing the issue
    
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
        if input_data:
            # Use challenge format for JSON input
            output_data = output_generator.generate_challenge_output(
                documents=documents,
                persona=args.persona,
                job=args.job,
                ranked_sections=top_sections,
                processing_time=time.time() - start_time,
                input_data=input_data
            )
        else:
            # Use standard format for command line input
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
        if len(top_sections) > 0:
            print(f"🔍 Average relevance score: {sum(s.relevance_score for s in top_sections) / len(top_sections):.3f}")
        else:
            print(f"🔍 Average relevance score: 0.000")
        
        # Generate and display summary report
        summary_report = output_generator.generate_summary_report(output_data)
        print(summary_report)
        
    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        raise

if __name__ == "__main__":
    main()
