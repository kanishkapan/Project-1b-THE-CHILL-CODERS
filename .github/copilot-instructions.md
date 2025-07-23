<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Copilot Instructions for Document Intelligence System

## Project Context
This is a persona-driven document intelligence system for the Adobe Hackathon Round 1B. The system extracts and prioritizes relevant sections from PDF documents based on specific personas and their job-to-be-done.

## Key Constraints
- **CPU-only execution** - No GPU dependencies
- **Model size ≤ 1GB** - Use lightweight models only
- **Processing time ≤ 60 seconds** - Optimize for speed
- **No internet access** - All models must be pre-downloaded

## Architecture Guidelines
- Use modular design with separate components for document processing, persona analysis, content extraction, ranking, and output generation
- Implement efficient PDF parsing with PyPDF2 and pdfplumber
- Use sentence-transformers for semantic similarity (CPU-optimized models)
- Apply scikit-learn for lightweight ML operations
- Structure output according to challenge1b_output.json format

## Code Standards
- Include comprehensive error handling and logging
- Add type hints for better code clarity
- Implement progress tracking for long operations
- Use pathlib for cross-platform file operations
- Follow PEP 8 coding standards

## Performance Optimization
- Cache model loading to avoid repeated initialization
- Use batch processing where possible
- Implement early stopping for ranking algorithms
- Monitor memory usage and processing time
- Prefer vectorized operations over loops
