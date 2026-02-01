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
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            print("")
            print("!" * 60)
            print("  ERROR: No API key found!")
            print("!" * 60)
            print("")
            print("  To fix this, run the following command:")
            print("")
            print("  Windows:")
            print("    set ANTHROPIC_API_KEY=your-key-here")
            print("")
            print("  Mac/Linux:")
            print("    export ANTHROPIC_API_KEY=your-key-here")
            print("")
            print("  Get your key at: https://console.anthropic.com")
            print("!" * 60)
            print("")
    
    def read_pdf(self, pdf_path):
        """
        Read PDF file and convert to base64 text.
        """
        if not os.path.exists(pdf_path):
            print("")
            print("!" * 60)
            print(f"  ERROR: File not found")
            print(f"  Path: {pdf_path}")
            print("!" * 60)
            print("")
            print("  Please check:")
            print("  1. The filename is spelled correctly")
            print("  2. The file is in the current folder")
            print("  3. Include .pdf extension")
            print("")
            print("  Current folder contents:")
            for f in os.listdir('.'):
                if f.endswith('.pdf'):
                    print(f"    - {f}")
            print("!" * 60)
            return None
        
        if not pdf_path.lower().endswith('.pdf'):
            print("")
            print("!" * 60)
            print(f"  ERROR: Not a PDF file")
            print(f"  File: {pdf_path}")
            print("!" * 60)
            print("  This tool only accepts PDF files.")
            print("!" * 60)
            return None

        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        pdf_base64 = base64.standard_b64encode(pdf_bytes).decode('utf-8')
        
        print(f"Read PDF: {pdf_path}")
        print(f"Size: {len(pdf_bytes)} bytes")
        
        return pdf_base64
    
    def generate_xtp(self, pdf_path, output_path=None):
        """
        Main function: PDF in, XTP out.
        """
        print("="*60)
        print("VEGA XTP Generator")
        print("From: Cognitive Verification Architecture by Vikash")
        print("="*60)
        
        print("\n[1/3] Reading PDF...")
        pdf_base64 = self.read_pdf(pdf_path)
        
        if pdf_base64 is None:
            return False
        
        print("\n[2/3] Sending to Claude AI...")
        
        if not self.api_key:
            print("ERROR: No API key. Cannot call Claude.")
            return False
        
        xtp_content = self._call_claude(pdf_base64, pdf_path)
        
        if xtp_content is None:
            return False

        is_valid, error = self._validate_xml(xtp_content)
        if not is_valid:
            print(f"WARNING: XML validation failed: {error}")
            print("Saving anyway - please check the output manually")

        print("\n[3/3] Saving XTP file...")
        
        if output_path is None:
            base_name = os.path.splitext(pdf_path)[0]
            output_path = f"{base_name}_testplan.xtp"
        
        with open(output_path, 'w') as f:
            f.write(xtp_content)
        
        print(f"Saved: {output_path}")
        print("="*60)
        print("DONE!")
        print("="*60)
        
        return True
    
    def _call_claude(self, pdf_base64, pdf_path, max_attempts=3):
        """
        Call Claude API with PDF. Auto-retry if response is incomplete.
        """
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            filename = os.path.basename(pdf_path)
            prompt = self._build_prompt(filename)
            
            attempt = 0
            cleaned_response = None
            
            while attempt < max_attempts:
                attempt += 1
                print(f"Calling Claude API (attempt {attempt}/{max_attempts})...")
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
                
                cleaned_response = self._clean_xml_response(response_text)
                is_valid, error = self._validate_xml(cleaned_response)
                
                if is_valid:
                    print(f"Success on attempt {attempt}")
                    return cleaned_response
                else:
                    print(f"Attempt {attempt} failed: {error}")
                    if attempt < max_attempts:
                        print("Retrying with stronger prompt...")
                        prompt = self._build_retry_prompt(filename, error)
            
            print(f"WARNING: All {max_attempts} attempts had issues")
            print("Returning best effort response")
            return cleaned_response
            
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

IMPORTANT:
- Extract ALL testable requirements  
- Include timing from diagrams
- Reference page numbers
- Generate positive AND negative tests

Output ONLY the XML. No explanations. No markdown."""
        
        return prompt
    
    def _build_retry_prompt(self, filename, previous_error):
        """
        Build a stronger prompt when first attempt fails.
        """
        prompt = f"""You are an expert hardware verification engineer.

I am providing a PDF specification document: {filename}

IMPORTANT: Your previous response had an issue: {previous_error}

Please generate a COMPLETE and VALID XTP test plan.

REQUIREMENTS:
1. Response must be valid XML
2. Root element must be <testplan>
3. Must include at least one <test_suite>
4. Each test_suite must have at least one <test_case>
5. Output ONLY the XML - no explanations, no markdown

<?xml version="1.0" encoding="UTF-8"?>
<testplan name="{filename}_verification" version="1.0">
    <metadata>
        <author>VEGA XTP Generator</author>
        <methodology>Cognitive Verification Architecture</methodology>
        <book>Cognitive Verification Architecture: The VEGA Framework by Vikash</book>
        <source>{filename}</source>
    </metadata>
    
    <requirements>
        <requirement id="REQ_001" source="page X">[Requirement]</requirement>
    </requirements>
    
    <test_suite name="[feature]_tests">
        <test_case id="TC_001" name="[name]">
            <objective>[objective]</objective>
            <source>Page X</source>
            <preconditions>
                <condition>[condition]</condition>
            </preconditions>
            <stimulus>
                <step order="1">[step]</step>
            </stimulus>
            <expected_results>
                <result>[result]</result>
            </expected_results>
            <pass_criteria>[criteria]</pass_criteria>
        </test_case>
    </test_suite>
</testplan>

Output ONLY valid XML. Start with <?xml and end with </testplan>."""
        
        return prompt
    
    def _clean_xml_response(self, response_text):
        """
        Clean the AI response to extract pure XML.
        """
        import re
        
        text = response_text.strip()
        
        match = re.search(r'```xml\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
            print("Cleaned: Removed ```xml wrapper")
            return text
        
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
            print("Cleaned: Removed ``` wrapper")
            return text
        
        if text.startswith('<?xml') or text.startswith('<testplan'):
            print("Cleaned: Already pure XML")
            return text
        
        match = re.search(r'(<\?xml.*</testplan>)', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
            print("Cleaned: Extracted XML from text")
            return text
        
        match = re.search(r'(<testplan.*</testplan>)', text, re.DOTALL)
        if match:
            text = match.group(1).strip()
            print("Cleaned: Extracted testplan from text")
            return text
        
        print("Warning: Could not identify XML structure")
        return text
    
    def _validate_xml(self, xml_text):
        """
        Check if the XML is valid.
        """
        import xml.etree.ElementTree as ET
        
        try:
            root = ET.fromstring(xml_text)
            
            if root.tag != 'testplan':
                return False, f"Root element is '{root.tag}', expected 'testplan'"
            
            test_suites = root.findall('.//test_suite')
            if len(test_suites) == 0:
                return False, "No test_suite elements found"
            
            test_cases = root.findall('.//test_case')
            if len(test_cases) == 0:
                return False, "No test_case elements found"
            
            print(f"Validated: {len(test_suites)} test suites, {len(test_cases)} test cases")
            return True, None
            
        except ET.ParseError as e:
            return False, f"XML parse error: {e}"


if __name__ == "__main__":
    print("VEGA Engine loaded successfully!")
