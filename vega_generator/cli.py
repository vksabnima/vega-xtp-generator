"""
VEGA Command Line Interface
Multi-model XTP generator from PDF specifications.

Usage:
    python -m vega_generator.cli spec.pdf
    python -m vega_generator.cli spec.pdf --model claude
    python -m vega_generator.cli spec.pdf --model openai
    python -m vega_generator.cli spec.pdf --model openai-assistant
"""

import sys
import os

from .engine import VegaEngine


def print_banner():
    print("")
    print("=" * 60)
    print("   VEGA XTP Generator v2.0")
    print("   AI-Powered Test Plan Generation from PDF")
    print("")
    print("   Supported Models:")
    print("     - claude           (Anthropic Claude)")
    print("     - openai           (OpenAI GPT-4)")
    print("     - openai-assistant (OpenAI with file storage)")
    print("")
    print("   From: Cognitive Verification Architecture")
    print("   Author: Vikash")
    print("=" * 60)


def print_usage():
    print("")
    print("Usage:")
    print("    python -m vega_generator.cli <pdf_file> [options]")
    print("")
    print("Options:")
    print("    --model <name>    Model to use (default: claude)")
    print("                      claude, openai, openai-assistant")
    print("    --output <file>   Output file path")
    print("    --help            Show this help")
    print("")
    print("Examples:")
    print("    python -m vega_generator.cli spec.pdf")
    print("    python -m vega_generator.cli spec.pdf --model openai-assistant")
    print("    python -m vega_generator.cli spec.pdf --model claude --output my_plan.xtp")
    print("")
    print("Environment Variables:")
    print("    ANTHROPIC_API_KEY    For Claude model")
    print("    OPENAI_API_KEY       For OpenAI models")
    print("")
    print("Model Recommendations:")
    print("    - Small PDFs (<500KB):  Use 'claude' or 'openai'")
    print("    - Large PDFs (>500KB):  Use 'openai-assistant'")
    print("    - Best quality:         Use 'claude'")
    print("    - File stays in memory: Use 'openai-assistant'")
    print("")


def parse_args(args):
    """Parse command line arguments."""
    result = {
        'pdf_path': None,
        'model': 'claude',
        'output': None,
        'help': False
    }
    
    i = 0
    while i < len(args):
        arg = args[i]
        
        if arg == '--help' or arg == '-h':
            result['help'] = True
        elif arg == '--model' or arg == '-m':
            if i + 1 < len(args):
                result['model'] = args[i + 1]
                i += 1
        elif arg == '--output' or arg == '-o':
            if i + 1 < len(args):
                result['output'] = args[i + 1]
                i += 1
        elif not arg.startswith('-'):
            if result['pdf_path'] is None:
                result['pdf_path'] = arg
        
        i += 1
    
    return result


def main():
    print_banner()
    
    args = parse_args(sys.argv[1:])
    
    if args['help']:
        print_usage()
        sys.exit(0)
    
    if args['pdf_path'] is None:
        print("ERROR: No PDF file specified.")
        print_usage()
        sys.exit(1)
    
    pdf_path = args['pdf_path']
    model = args['model']
    output = args['output']
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"ERROR: File must be a PDF: {pdf_path}")
        sys.exit(1)
    
    if model not in VegaEngine.SUPPORTED_MODELS:
        print(f"ERROR: Unknown model: {model}")
        print(f"Supported: {', '.join(VegaEngine.SUPPORTED_MODELS)}")
        sys.exit(1)
    
    print(f"PDF:   {pdf_path}")
    print(f"Model: {model}")
    if output:
        print(f"Output: {output}")
    
    engine = VegaEngine(model=model)
    
    success = engine.generate_xtp(pdf_path, output)
    
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
