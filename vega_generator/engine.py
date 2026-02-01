"""
VEGA Engine - Sends PDF to Claude AI and gets XTP test plan back.

Think of this like a SystemVerilog driver:
- Input:  PDF specification (like a transaction)
- Output: XTP test plan (like a response)
"""

import os
import base64


class VegaEngine:
    """
    Main engine class.
    
    SystemVerilog equivalent:
        class vega_engine;
            string api_key;
            function new();
            task generate_xtp();
        endclass
    """
    
    def __init__(self, api_key=None):
        """
        Constructor - runs when you create the object.
        
        SystemVerilog equivalent:
            function new(string api_key = "");
                this.api_key = api_key;
            endfunction
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            print("WARNING: No API key found!")
            print("Set it with: set ANTHROPIC_API_KEY=your-key-here")
    
    def read_pdf(self, pdf_path):
        """
        Read PDF file and convert to base64 text.
        
        Why base64? 
        - PDF is binary (like a .bin file)
        - Internet APIs need text
        - base64 converts binary to text safely
        
        SystemVerilog equivalent:
            function string read_file(string path);
        """
        if not os.path.exists(pdf_path):
            print(f"ERROR: File not found: {pdf_path}");
            return None
        
        with open(pdf_path, 'rb') as f:    # 'rb' = read binary
            pdf_bytes = f.read()
        
        pdf_base64 = base64.standard_b64encode(pdf_bytes).decode('utf-8')
        
        print(f"Read PDF: {pdf_path}")
        print(f"Size: {len(pdf_bytes)} bytes")
        
        return pdf_base64
    
    def generate_xtp(self, pdf_path, output_path=None):
        """
        Main function: PDF in, XTP out.
        
        SystemVerilog equivalent:
            task generate_xtp(string pdf_path, string output_path = "");
        """
        print("="*60)
        print("VEGA XTP Generator")
        print("From: Cognitive Verification Architecture by Vikash")
        print("="*60)
        
        # Step 1: Read PDF
        print("\n[1/3] Reading PDF...")
        pdf_base64 = self.read_pdf(pdf_path)
        
        if pdf_base64 is None:
            return False
        
        # Step 2: Send to Claude
        print("\n[2/3] Sending to Claude AI...")
        
        if not self.api_key:
            print("ERROR: No API key. Cannot call Claude.")
            return False
        
        xtp_content = self._call_claude(pdf_base64, pdf_path)
        
        if xtp_content is None:
            return False
        
        # Step 3: Save output
        print("\n[3/3] Saving XTP file...")
        
        if output_path is None:
            base_name = os.path.splitext(pdf_path)[0]
            output_path = f"{base_name}_testplan.xtp"
        
        with open(output_path, 'w') as f:    # 'w' = write text
            f.write(xtp_content)
        
        print(f"Saved: {output_path}")
        print("="*60)
        print("DONE!")
        print("="*60)
        
        return True
    
    def _call_claude(self, pdf_base64, pdf_path):
        """
        Call Claude API with PDF.
        
        The underscore means 'private' - only used inside this class.
        Like 'local' in SystemVerilog.
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            filename = os.path.basename(pdf_path)
            prompt = self._build_prompt(filename)
            
            print("Calling Claude API...")
            print("(This may take 30-60 seconds)")
            
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            response_text = message.content[0].text
            print("Response received!")
            
            return response_text
            
        except ImportError:
            print("ERROR: 'anthropic' package not installed")
            print("Run: pip install anthropic")
            return None
            
        except Exception as e:
            print(f"ERROR calling Claude: {e}")
            return None
    
    def _build_prompt(self, filename):
        """
        The instruction we give to Claude.
        
        This tells Claude exactly what to do with the PDF
        and what format we want the output in.
        """
        prompt = f"""You are an expert hardware verification engineer.

I am providing a PDF specification document: {filename}

This PDF contains:
- Protocol descriptions
- Timing diagrams  
- Signal definitions
- Register maps
- State machines

YOUR TASK:
Analyze the ENTIRE PDF including all diagrams, tables, and text.
Generate a comprehensive XTP (XML Test Plan).

OUTPUT FORMAT:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testplan name="{filename}_verification" version="1.0">
    <metadata>
        <author>VEGA XTP Generator</author>
        <methodology>Cognitive Verification Architecture</methodology>
        <book>Cognitive Verification Architecture: The VEGA Framework by Vikash</book>
        <source>{filename}</source>
    </metadata>
    
    <requirements>
        <requirement id="REQ_001" source="page X">
            [Requirement from spec]
        </requirement>
    </requirements>
    
    <test_suite name="[feature]_tests">
        <test_case id="TC_001" name="[test name]">
            <objective>[What is being verified]</objective>
            <source>Page X, Section Y</source>
            <preconditions>
                <condition>[Setup needed]</condition>
            </preconditions>
            <stimulus>
                <step order="1">[Action]</step>
                <step order="2">[Action]</step>
            </stimulus>
            <expected_results>
                <result>[Expected outcome]</result>
            </expected_results>
            <pass_criteria>[How to judge pass/fail]</pass_criteria>
        </test_case>
    </test_suite>
</testplan>
```

IMPORTANT:
- Extract ALL testable requirements  
- Include timing from diagrams
- Reference page numbers
- Generate positive AND negative tests

Output ONLY the XML. No explanations."""
        
        return prompt


# This runs only if you execute this file directly
# Like a 'program' block in SystemVerilog
if __name__ == "__main__":
    print("VEGA Engine loaded successfully!")


