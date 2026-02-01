"""
Test script for VEGA XTP Generator
Run this to verify everything is working.
"""

import os
import sys

def test_imports():
    """Test 1: Check all imports work."""
    print("Test 1: Checking imports...")
    try:
        from vega_generator.engine import VegaEngine
        print("  PASS: VegaEngine imported")
        return True
    except ImportError as e:
        print(f"  FAIL: {e}")
        return False

def test_anthropic():
    """Test 2: Check anthropic package is installed."""
    print("Test 2: Checking anthropic package...")
    try:
        import anthropic
        print("  PASS: anthropic installed")
        return True
    except ImportError:
        print("  FAIL: anthropic not installed")
        print("  Fix: pip install anthropic")
        return False

def test_api_key():
    """Test 3: Check API key is set."""
    print("Test 3: Checking API key...")
    key = os.getenv('ANTHROPIC_API_KEY')
    if key:
        print(f"  PASS: API key found (starts with {key[:10]}...)")
        return True
    else:
        print("  FAIL: ANTHROPIC_API_KEY not set")
        print("  Fix: set ANTHROPIC_API_KEY=your-key-here")
        return False

def test_pdf_exists():
    """Test 4: Check if any PDF exists in folder."""
    print("Test 4: Checking for PDF files...")
    pdfs = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if pdfs:
        print(f"  PASS: Found {len(pdfs)} PDF file(s):")
        for pdf in pdfs:
            print(f"    - {pdf}")
        return True
    else:
        print("  FAIL: No PDF files in current folder")
        print("  Fix: Copy a PDF spec to this folder")
        return False

def test_engine_creation():
    """Test 5: Check VegaEngine can be created."""
    print("Test 5: Creating VegaEngine...")
    try:
        from vega_generator.engine import VegaEngine
        engine = VegaEngine()
        print("  PASS: VegaEngine created")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False

def main():
    print("")
    print("=" * 60)
    print("  VEGA XTP Generator - Test Suite")
    print("=" * 60)
    print("")
    
    results = []
    
    results.append(test_imports())
    results.append(test_anthropic())
    results.append(test_api_key())
    results.append(test_pdf_exists())
    results.append(test_engine_creation())
    
    print("")
    print("=" * 60)
    print("  RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"  Passed: {passed}/{total}")
    
    if passed == total:
        print("")
        print("  All tests PASSED!")
        print("  You can run: python -m vega_generator.cli your_spec.pdf")
    else:
        print("")
        print("  Some tests FAILED. Please fix the issues above.")
    
    print("=" * 60)
    print("")

if __name__ == "__main__":
    main()
