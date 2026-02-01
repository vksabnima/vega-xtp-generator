"""
VEGA Engine - Multi-Model XTP Generator

Supports:
- Claude (Anthropic)
- OpenAI GPT-4
- OpenAI Assistants (for large PDFs - stores file)

From: "Cognitive Verification Architecture: The VEGA Framework"
Author: Vikash
"""

import os
import base64
import time


class VegaEngine:
    """
    Multi-model verification test plan generator.
    """
    
    SUPPORTED_MODELS = ['claude', 'openai', 'openai-assistant']
    
    def __init__(self, model='claude', api_key=None):
        """
        Constructor.
        
        Args:
            model: 'claude', 'openai', or 'openai-assistant'
            api_key: API key (or set via environment variable)
        """
        self.model = model.lower()
        
        if self.model not in self.SUPPORTED_MODELS:
            print(f"ERROR: Unknown model '{model}'")
            print(f"Supported: {', '.join(self.SUPPORTED_MODELS)}")
            self.model = 'claude'
        
        # Get appropriate API key
        if self.model == 'claude':
            self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            self.key_name = 'ANTHROPIC_API_KEY'
        else:
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
            self.key_name = 'OPENAI_API_KEY'
        
        if not self.api_key:
            print("")
            print("!" * 60)
            print(f"  ERROR: No API key found for {self.model}!")
            print("!" * 60)
            print(f"  Set: {self.key_name}=your-key-here")
            print("!" * 60)
        
        # For OpenAI Assistant
        self.assistant_id = None
        self.file_id = None
    
    def read_pdf(self, pdf_path):
        """Read PDF and convert to base64."""
        if not os.path.exists(pdf_path):
            print(f"ERROR: File not found: {pdf_path}")
            return None
        
        if not pdf_path.lower().endswith('.pdf'):
            print(f"ERROR: Not a PDF file: {pdf_path}")
            return None

        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        self.pdf_bytes = pdf_bytes  # Store for OpenAI Assistant
        pdf_base64 = base64.standard_b64encode(pdf_bytes).decode('utf-8')
        
        print(f"Read PDF: {pdf_path}")
        print(f"Size: {len(pdf_bytes) / 1024:.1f} KB")
        
        return pdf_base64
    
    def generate_xtp(self, pdf_path, output_path=None):
        """
        Main function: Generate XTP using selected model.
        """
        print("")
        print("=" * 60)
        print("  VEGA XTP Generator")
        print(f"  Model: {self.model.upper()}")
        print("  Cognitive Verification Architecture by Vikash")
        print("=" * 60)
        
        if not self.api_key:
            print("ERROR: No API key configured.")
            return False
        
        # Read PDF
        print("\n[1/3] Reading PDF...")
        pdf_base64 = self.read_pdf(pdf_path)
        
        if pdf_base64 is None:
            return False
        
        filename = os.path.basename(pdf_path)
        
        # Generate based on model
        print(f"\n[2/3] Generating with {self.model.upper()}...")
        
        if self.model == 'claude':
            xtp_content = self._generate_with_claude(pdf_base64, filename)
        elif self.model == 'openai':
            xtp_content = self._generate_with_openai(pdf_base64, filename)
        elif self.model == 'openai-assistant':
            xtp_content = self._generate_with_assistant(pdf_path, filename)
        
        if xtp_content is None:
            print("Generation failed.")
            return False
        
        # Clean and validate
        xtp_content = self._clean_xml(xtp_content)
        xtp_content = self._ensure_complete_xml(xtp_content, filename)
        
        # Save
        print("\n[3/3] Saving XTP file...")
        
        if output_path is None:
            base_name = os.path.splitext(pdf_path)[0]
            output_path = f"{base_name}_testplan.xtp"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xtp_content)
        
        
        print(f"Saved: {output_path}")
        print("=" * 60)
        print("DONE!")
        print("=" * 60)
        
        return True
    
    # =========================================================================
    # CLAUDE
    # =========================================================================
    
    def _generate_with_claude(self, pdf_base64, filename):
        """Generate XTP using Claude API."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            prompt = self._build_prompt(filename)
            
            print("  Calling Claude API...")
            print("  (This may take 30-60 seconds)")
            
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
            
            print("  Response received!")
            return message.content[0].text
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return None
    
    # =========================================================================
    # OPENAI GPT-4
    # =========================================================================
    
    def _generate_with_openai(self, pdf_base64, filename):
        """Generate XTP using OpenAI GPT-4."""
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            prompt = self._build_prompt(filename)
            
            print("  Calling OpenAI API...")
            print("  (This may take 30-60 seconds)")
            
            # GPT-4 doesn't support PDF directly, need to describe
            # For now, we'll note this limitation
            print("  NOTE: GPT-4 has limited PDF support.")
            print("  For large PDFs, use --model openai-assistant")
            
            response = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=8000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"I have a PDF specification called {filename}. {prompt}"
                            }
                        ]
                    }
                ]
            )
            
            print("  Response received!")
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return None
    
    # =========================================================================
    # OPENAI ASSISTANTS (Best for large PDFs)
    # =========================================================================
    
    def _generate_with_assistant(self, pdf_path, filename):
        """
        Generate XTP using OpenAI Assistants API.
        This STORES the PDF and allows multiple queries.
        Best for large specifications.
        """
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.api_key)
            
            # Step 1: Upload the PDF file
            print("  Uploading PDF to OpenAI...")
            with open(pdf_path, 'rb') as f:
                file = client.files.create(
                    file=f,
                    purpose='assistants'
                )
            self.file_id = file.id
            print(f"  File uploaded: {self.file_id}")
            
            # Step 2: Create an Assistant with file access
            print("  Creating assistant...")
            assistant = client.beta.assistants.create(
                name="VEGA XTP Generator",
                instructions="""You are an expert hardware verification engineer.
Your task is to analyze hardware specifications and generate comprehensive XML test plans.
Always output valid XML. Include requirements, test suites, and test cases.
Reference page numbers from the source document.""",
                model="gpt-4o",
                tools=[{"type": "file_search"}]
            )
            self.assistant_id = assistant.id
            print(f"  Assistant created: {self.assistant_id}")
            
            # Step 3: Create a thread with the file
            print("  Creating conversation thread...")
            
            # Create vector store and add file
            vector_store = client.beta.vector_stores.create(
                name="Spec Documents"
            )
            
            client.beta.vector_stores.files.create(
                vector_store_id=vector_store.id,
                file_id=self.file_id
            )
            
            # Update assistant to use vector store
            client.beta.assistants.update(
                assistant_id=self.assistant_id,
                tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
            )
            
            thread = client.beta.threads.create()
            
            # Step 4: Send the prompt
            print("  Analyzing specification (this may take 1-2 minutes)...")
            
            prompt = self._build_prompt(filename)
            
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            # Step 5: Run and wait for completion
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Poll for completion
            while True:
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    print(f"  Run failed: {run_status.last_error}")
                    return None
                elif run_status.status in ['cancelled', 'expired']:
                    print(f"  Run {run_status.status}")
                    return None
                
                print(f"    Status: {run_status.status}...")
                time.sleep(5)
            
            # Step 6: Get the response
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            response_text = messages.data[0].content[0].text.value
            print("  Response received!")
            
            # Step 7: Cleanup (optional - keep for more queries)
            # self._cleanup_assistant(client)
            
            return response_text
            
        except ImportError:
            print("  ERROR: openai package not installed")
            print("  Run: pip install openai")
            return None
            
        except Exception as e:
            print(f"  ERROR: {e}")
            return None
    
    def _cleanup_assistant(self, client):
        """Clean up OpenAI resources."""
        try:
            if self.file_id:
                client.files.delete(self.file_id)
                print(f"  Deleted file: {self.file_id}")
            if self.assistant_id:
                client.beta.assistants.delete(self.assistant_id)
                print(f"  Deleted assistant: {self.assistant_id}")
        except Exception as e:
            print(f"  Cleanup warning: {e}")
    
    # =========================================================================
    # SHARED UTILITIES
    # =========================================================================
    
    def _build_prompt(self, filename):
        """Build the prompt for any model."""
        return f"""Analyze the specification document: {filename}

Generate a comprehensive XTP (XML Test Plan) with:
1. All requirements extracted from the document
2. Test suites for each feature
3. Test cases with stimulus and expected results
4. Cross-feature integration tests

OUTPUT FORMAT (valid XML only, no markdown):

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
                <step order="2">[step]</step>
            </stimulus>
            <expected_results>
                <result>[result]</result>
            </expected_results>
            <pass_criteria>[criteria]</pass_criteria>
        </test_case>
    </test_suite>
    
    <test_suite name="cross_feature_tests">
        <test_case id="TC_CF_001" name="[cross-feature test]">
            <objective>[Test interaction between features]</objective>
            <features_involved>[Feature A, Feature B]</features_involved>
            <stimulus>
                <step order="1">[step]</step>
            </stimulus>
            <expected_results>
                <result>[result]</result>
            </expected_results>
        </test_case>
    </test_suite>
</testplan>

IMPORTANT:
- Extract ALL requirements
- Include timing from diagrams
- Reference page numbers
- Include cross-feature tests
- Output ONLY valid XML, no explanations"""
    
    def _clean_xml(self, response):
        """Remove markdown wrappers."""
        import re
        
        if response is None:
            return ""
        
        text = response.strip()
        
        # Remove ```xml wrapper
        match = re.search(r'```xml\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Remove ``` wrapper
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Extract XML if mixed with text
        match = re.search(r'(<\?xml.*</testplan>)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        match = re.search(r'(<testplan.*</testplan>)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return text
    
    def _ensure_complete_xml(self, xml_text, filename):
        """Ensure XML is complete and valid."""
        if not xml_text:
            return self._create_empty_xtp(filename)
        
        # Add XML declaration if missing
        if not xml_text.strip().startswith('<?xml'):
            xml_text = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_text
        
        # Check for incomplete testplan
        if '<testplan' in xml_text and '</testplan>' not in xml_text:
            # Try to find a good cutoff point
            last_close = xml_text.rfind('</test_case>')
            if last_close > 0:
                xml_text = xml_text[:last_close + len('</test_case>')]
            xml_text += '\n    </test_suite>\n</testplan>'
        
        return xml_text
    
    def _create_empty_xtp(self, filename):
        """Create minimal valid XTP if generation fails."""
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<testplan name="{filename}_verification" version="1.0">
    <metadata>
        <author>VEGA XTP Generator</author>
        <source>{filename}</source>
        <note>Generation incomplete - please retry</note>
    </metadata>
    <requirements>
        <requirement id="REQ_001" source="manual">Review specification manually</requirement>
    </requirements>
    <test_suite name="placeholder_tests">
        <test_case id="TC_001" name="placeholder">
            <objective>Placeholder - generation incomplete</objective>
        </test_case>
    </test_suite>
</testplan>'''


if __name__ == "__main__":
    print("VEGA Engine loaded successfully!")
    print(f"Supported models: {', '.join(VegaEngine.SUPPORTED_MODELS)}")
