"""
VEGA Command Line Interface
Run this from command prompt to generate XTP from PDF.

Usage:
    python -m vega_generator.cli your_spec.pdf
"""

import sys
import os

from .engine import VegaEngine


def print_banner():
    print("")
    print("=" * 60)
    print("   VEGA XTP Generator v1.0")
    print("   AI-Powered Test Plan Generation from PDF")
    print("")
    print("   From: Cognitive Verification Architecture")
    print("   Author: Vikash")
    print("=" * 60)
    print("")


def print_usage():
    print("Usage:")
    print("    python -m vega_generator.cli <pdf_file> [output_file]")
    print("")
    print("Examples:")
    print("    python -m vega_generator.cli spec.pdf")
    print("    python -m vega_generator.cli spec.pdf my_testplan.xtp")
    print("")
    print("Before running, set your API key:")
    print("    set ANTHROPIC_API_KEY=your-key-here")
    print("")


def main():
    print_banner()
    
    if len(sys.argv) < 2:
        print("ERROR: No PDF file specified.")
        print("")
        print_usage()
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if len(sys.argv) >= 3:
        output_path = sys.argv[2]
    else:
        output_path = None
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"ERROR: File must be a PDF: {pdf_path}")
        sys.exit(1)
    
    engine = VegaEngine()
    
    success = engine.generate_xtp(pdf_path, output_path)
    
    if success:
        print("")
        print("Test plan generated successfully!")
        sys.exit(0)
    else:
        print("")
        print("Failed to generate test plan.")
        sys.exit(1)


if __name__ == "__main__":
    main()
