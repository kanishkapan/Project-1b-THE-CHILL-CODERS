#!/usr/bin/env python3
"""
Quick Install Script - Installs minimal dependencies for the system to work
"""

import subprocess
import sys

def install_package(package):
    """Install a single package."""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("🚀 Quick installation of core dependencies...")
    
    # Core packages that should install without issues
    core_packages = [
        "PyPDF2",
        "pdfplumber", 
        "scikit-learn",
        "numpy",
        "pandas",
        "tqdm",
        "nltk",
        "fuzzywuzzy",
        "python-Levenshtein",
        "jsonschema"
    ]
    
    success_count = 0
    for package in core_packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installed {success_count}/{len(core_packages)} core packages")
    
    # Optional packages
    print("\n🔧 Installing optional packages...")
    optional_packages = [
        ("spacy", "Advanced NLP processing"),
        ("transformers", "Advanced AI models"),
        ("sentence-transformers", "Semantic similarity")
    ]
    
    for package, description in optional_packages:
        print(f"\nTrying {package} ({description})...")
        install_package(package)
    
    # Try to download spacy model if spacy was installed
    try:
        import spacy
        print("\n📥 Downloading spaCy English model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ spaCy model downloaded")
    except:
        print("⚠️  spaCy model download failed (optional)")
    
    print(f"\n🎉 Installation complete!")
    print("🧪 Test the system with: python test_system.py")

if __name__ == "__main__":
    main()
