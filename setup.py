#!/usr/bin/env python3
"""
Setup script for the Document Intelligence System
Installs dependencies and downloads required models
"""

import subprocess
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    try:
        logger.info(f"Running: {description}")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup process."""
    logger.info("🚀 Setting up Document Intelligence System...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    logger.info(f"✅ Python {sys.version} detected")
    
    # Install core dependencies first
    core_packages = [
        "numpy",
        "pandas", 
        "tqdm",
        "regex"
    ]
    
    logger.info("📦 Installing core packages...")
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            logger.warning(f"⚠️  Failed to install {package}, continuing...")
    
    # Install PDF processing
    pdf_packages = ["PyPDF2", "pdfplumber"]
    logger.info("📄 Installing PDF processing packages...")
    for package in pdf_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            logger.warning(f"⚠️  Failed to install {package}, continuing...")
    
    # Install ML packages
    ml_packages = ["scikit-learn", "nltk", "fuzzywuzzy", "python-Levenshtein"]
    logger.info("🤖 Installing ML packages...")
    for package in ml_packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            logger.warning(f"⚠️  Failed to install {package}, continuing...")
    
    # Install NLP packages (optional)
    logger.info("🧠 Installing NLP packages...")
    
    # Try spaCy
    if run_command("pip install spacy", "Installing spaCy"):
        run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model")
    else:
        logger.warning("⚠️  spaCy installation failed, will use fallback processing")
    
    # Try transformers (optional for advanced features)
    if not run_command("pip install transformers torch --index-url https://download.pytorch.org/whl/cpu", "Installing transformers with CPU-only PyTorch"):
        logger.warning("⚠️  Transformers installation failed, will use basic NLP only")
    
    # Try sentence-transformers (optional)
    if not run_command("pip install sentence-transformers", "Installing sentence-transformers"):
        logger.warning("⚠️  Sentence-transformers installation failed, will use basic similarity")
    
    # Install remaining packages
    remaining_packages = ["jsonschema"]
    for package in remaining_packages:
        run_command(f"pip install {package}", f"Installing {package}")
    
    # Create necessary directories
    directories = ['output', 'models', 'logs']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        logger.info(f"✅ Created directory: {dir_name}")
    
    # Test core imports
    logger.info("🧪 Testing core imports...")
    try:
        import PyPDF2
        import pdfplumber
        import sklearn
        import pandas
        import numpy
        logger.info("✅ Core packages imported successfully")
    except ImportError as e:
        logger.error(f"❌ Core import error: {e}")
        logger.error("Please manually install missing packages")
        
    # Test optional imports
    logger.info("🧪 Testing optional imports...")
    optional_modules = {
        'spacy': 'spaCy (for advanced NLP)',
        'transformers': 'Transformers (for advanced models)',
        'sentence_transformers': 'Sentence Transformers (for semantic similarity)'
    }
    
    for module, description in optional_modules.items():
        try:
            __import__(module)
            logger.info(f"✅ {description} available")
        except ImportError:
            logger.warning(f"⚠️  {description} not available - using fallback")
    
    logger.info("🎉 Setup completed!")
    logger.info("📚 Place your PDF documents in the 'sample_docs' directory")
    logger.info("🏃 Run the system with: python main.py --documents_dir sample_docs --persona 'Your Persona' --job 'Your Job Description'")

if __name__ == "__main__":
    main()
