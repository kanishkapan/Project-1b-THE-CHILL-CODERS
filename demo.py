#!/usr/bin/env python3
"""
Demo Script for Document Intelligence System
Demonstrates the system with sample persona and job descriptions.
"""

import os
import sys
from pathlib import Path

def run_demo():
    """Run a demonstration of the system."""
    print("🚀 Document Intelligence System Demo")
    print("=" * 50)
    
    # Check if sample documents exist
    sample_docs = Path("sample_docs")
    if not sample_docs.exists():
        sample_docs.mkdir(exist_ok=True)
    
    pdf_files = list(sample_docs.glob("*.pdf"))
    
    if not pdf_files:
        print("📄 No PDF files found in sample_docs directory.")
        print("📋 Please add some PDF files to test the system:")
        print("   1. Research papers (for academic personas)")
        print("   2. Business reports (for analyst personas)")
        print("   3. Educational content (for student personas)")
        print("   4. Technical documentation (for developer personas)")
        print("")
        print("💡 Once you add PDFs, run this script again!")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF documents:")
    for pdf in pdf_files:
        print(f"   - {pdf.name}")
    print("")
    
    # Demo personas and jobs
    demo_cases = [
        {
            "name": "Academic Research",
            "persona": "PhD Researcher in Computational Biology",
            "job": "Prepare comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
        },
        {
            "name": "Business Analysis", 
            "persona": "Investment Analyst",
            "job": "Analyze revenue trends, R&D investments, and market positioning strategies"
        },
        {
            "name": "Educational Content",
            "persona": "Undergraduate Chemistry Student", 
            "job": "Identify key concepts and mechanisms for exam preparation on reaction kinetics"
        }
    ]
    
    print("🎯 Available Demo Cases:")
    for i, case in enumerate(demo_cases, 1):
        print(f"   {i}. {case['name']}")
        print(f"      Persona: {case['persona']}")
        print(f"      Job: {case['job'][:60]}...")
    print("")
    
    try:
        choice = input("Select a demo case (1-3) or press Enter for case 1: ").strip()
        if not choice:
            choice = "1"
        
        case_index = int(choice) - 1
        if case_index < 0 or case_index >= len(demo_cases):
            case_index = 0
        
        selected_case = demo_cases[case_index]
        
        print(f"\n🎪 Running Demo: {selected_case['name']}")
        print("=" * 50)
        
        # Construct command
        command = f'python main.py --documents_dir sample_docs --persona "{selected_case["persona"]}" --job "{selected_case["job"]}"'
        
        print(f"🏃 Executing: {command}")
        print("")
        
        # Execute the main system
        os.system(command)
        
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Demo cancelled.")
        return
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("💡 Try running: python quick_install.py")

if __name__ == "__main__":
    run_demo()
