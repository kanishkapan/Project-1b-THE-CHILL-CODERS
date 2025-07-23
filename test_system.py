#!/usr/bin/env python3
"""
Test script for Document Processor
Tests the document processing functionality with sample data
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from document_processor import DocumentProcessor
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_document_processor():
    """Test the document processor with mock data."""
    logger.info("🧪 Testing Document Processor...")
    
    try:
        # Initialize processor
        processor = DocumentProcessor(max_pages_per_doc=10)
        logger.info("✅ Document processor initialized")
        
        # Test with sample_docs directory
        sample_docs_dir = Path(__file__).parent / 'sample_docs'
        
        if not sample_docs_dir.exists():
            logger.warning(f"Sample docs directory not found: {sample_docs_dir}")
            logger.info("📁 Creating sample docs directory...")
            sample_docs_dir.mkdir(exist_ok=True)
            
            # Create a simple test README in sample_docs
            test_readme = sample_docs_dir / "test_info.txt"
            test_readme.write_text("""
This is a test directory for PDF documents.
Place your PDF files here for testing the system.

Supported formats: .pdf
Maximum recommended: 10 documents
Maximum pages per document: 50
            """)
            logger.info("📄 Created test info file")
        
        # Test loading (will be empty initially)
        documents = processor.load_documents(str(sample_docs_dir), max_docs=5)
        logger.info(f"📚 Found {len(documents)} PDF documents")
        
        if documents:
            # Test summary generation
            summary = processor.get_document_summary(documents)
            logger.info(f"📊 Document summary: {summary}")
        else:
            logger.info("ℹ️  No PDF documents found - this is expected for initial setup")
        
        logger.info("✅ Document processor test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Document processor test failed: {str(e)}")
        return False

def test_persona_analyzer():
    """Test the persona analyzer."""
    logger.info("🧪 Testing Persona Analyzer...")
    
    try:
        from persona_analyzer import PersonaAnalyzer
        
        analyzer = PersonaAnalyzer()
        
        # Test with sample persona and job
        persona = "PhD Researcher in Computational Biology"
        job = "Prepare comprehensive literature review focusing on methodologies and performance benchmarks"
        
        context = analyzer.analyze_persona(persona, job)
        
        logger.info(f"✅ Persona analysis complete:")
        logger.info(f"   Role: {context.role}")
        logger.info(f"   Domain: {context.domain}")
        logger.info(f"   Job Intent: {context.job_intent}")
        logger.info(f"   Analysis Depth: {context.analysis_depth}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Persona analyzer test failed: {str(e)}")
        return False

def test_integration():
    """Test the complete system integration."""
    logger.info("🧪 Testing System Integration...")
    
    try:
        # Test imports
        from persona_analyzer import PersonaAnalyzer
        from content_extractor import ContentExtractor
        from ranking_engine import RankingEngine
        from output_generator import OutputGenerator
        
        logger.info("✅ All modules imported successfully")
        
        # Test initialization
        persona_analyzer = PersonaAnalyzer()
        content_extractor = ContentExtractor()
        ranking_engine = RankingEngine()
        output_generator = OutputGenerator()
        
        logger.info("✅ All components initialized successfully")
        
        # Test with mock data
        persona = "Investment Analyst"
        job = "Analyze revenue trends and market positioning strategies"
        
        context = persona_analyzer.analyze_persona(persona, job)
        logger.info("✅ Persona analysis working")
        
        # Test output generation with empty data
        output_data = output_generator.generate_output(
            documents=[],
            persona=persona,
            job=job,
            ranked_sections=[],
            processing_time=1.0
        )
        
        logger.info("✅ Output generation working")
        logger.info(f"   Generated output keys: {list(output_data.keys())}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    logger.info("🚀 Running Document Intelligence System Tests...")
    
    tests = [
        test_document_processor,
        test_persona_analyzer,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                logger.error(f"❌ Test {test.__name__} failed")
        except Exception as e:
            logger.error(f"❌ Test {test.__name__} crashed: {str(e)}")
    
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        logger.info("📋 Next steps:")
        logger.info("  1. Run: python quick_install.py  (to install dependencies)")
        logger.info("  2. Place PDF documents in 'sample_docs' directory")
        logger.info("  3. Run: python main.py --documents_dir sample_docs --persona 'Your Persona' --job 'Your Job'")
    else:
        logger.error("❌ Some tests failed!")
        logger.info("💡 Try running: python quick_install.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
