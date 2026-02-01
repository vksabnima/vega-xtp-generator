\# VEGA XTP Generator



\*\*AI-Powered Verification Test Plan Generator from PDF Specifications\*\*



VEGA (Verification Engineering Graph Architecture) automatically generates executable test plans (XTP) from hardware specification documents using Claude AI.



---



\## What It Does



1\. \*\*Input:\*\* Any PDF specification (protocol specs, IP datasheets, etc.)

2\. \*\*AI Analysis:\*\* Claude reads the entire PDF including diagrams and tables

3\. \*\*Output:\*\* Complete XTP test plan with requirements and test cases

```

PDF Specification ──▶ VEGA ──▶ XTP Test Plan

```



---



\## Features



\- ✅ Extracts requirements from text, tables, and diagrams

\- ✅ References page numbers from source document

\- ✅ Generates positive and negative test cases

\- ✅ Creates structured XTP format output

\- ✅ Handles timing diagrams and state machines



---



\## Quick Start



\### 1. Clone the Repository

```bash

git clone https://github.com/vksabnima/vega-xtp-generator.git

cd vega-xtp-generator

```



\### 2. Install Dependencies

```bash

pip install anthropic

```



\### 3. Set Your API Key



\*\*Windows:\*\*

```bash

set ANTHROPIC\_API\_KEY=your-key-here

```



\*\*Mac/Linux:\*\*

```bash

export ANTHROPIC\_API\_KEY=your-key-here

```



\### 4. Run

```bash

python -m vega\_generator.cli your\_specification.pdf

```



---



\## Example Output



Input: `apb\_spec.pdf` (ARM APB Protocol Specification)



Output: `apb\_spec\_testplan.xtp`

```xml

<?xml version="1.0" encoding="UTF-8"?>

<testplan name="apb\_spec.pdf\_verification" version="1.0">

&nbsp;   <metadata>

&nbsp;       <author>VEGA XTP Generator</author>

&nbsp;       <methodology>Cognitive Verification Architecture</methodology>

&nbsp;       <book>Cognitive Verification Architecture: The VEGA Framework by Vikash</book>

&nbsp;   </metadata>

&nbsp;   

&nbsp;   <requirements>

&nbsp;       <requirement id="REQ\_001" source="page 3-20">

&nbsp;           Setup phase occurs when PSEL is asserted

&nbsp;       </requirement>

&nbsp;       ...

&nbsp;   </requirements>

&nbsp;   

&nbsp;   <test\_suite name="basic\_protocol\_tests">

&nbsp;       <test\_case id="TC\_001" name="basic\_write\_no\_wait\_states">

&nbsp;           <objective>Verify basic write transfer completes in 2 cycles</objective>

&nbsp;           <source>Page 3-20, Figure 3-1</source>

&nbsp;           ...

&nbsp;       </test\_case>

&nbsp;   </test\_suite>

</testplan>

```



---



\## How It Works

```

┌─────────────────┐

│   PDF Spec      │

│  (any format)   │

└────────┬────────┘

&nbsp;        │

&nbsp;        ▼

┌─────────────────┐

│  VEGA Engine    │

│                 │

│ • Reads PDF     │

│ • Sends to AI   │

│ • Processes     │

│   response      │

└────────┬────────┘

&nbsp;        │

&nbsp;        ▼

┌─────────────────┐

│  Claude AI      │

│                 │

│ • Analyzes text │

│ • Reads diagrams│

│ • Extracts      │

│   requirements  │

└────────┬────────┘

&nbsp;        │

&nbsp;        ▼

┌─────────────────┐

│  XTP Output     │

│                 │

│ • Requirements  │

│ • Test suites   │

│ • Test cases    │

│ • Coverage      │

└─────────────────┘

```



---



\## Methodology



This tool implements the \*\*Cognitive Verification Architecture\*\* methodology described in:



\*\*"Cognitive Verification Architecture: The VEGA Framework"\*\* by Vikash



The approach focuses on:

\- Extracting verification intent from specifications

\- Mapping requirements to executable test cases

\- Ensuring traceability from spec to test



---



\## Requirements



\- Python 3.10 or higher

\- Anthropic API key (\[Get one here](https://console.anthropic.com))



---



\## File Structure

```

vega-xtp-generator/

├── vega\_generator/

│   ├── \_\_init\_\_.py      # Package info

│   ├── engine.py        # Core AI engine

│   └── cli.py           # Command line interface

├── examples/            # Example specifications

├── output/              # Generated test plans

├── README.md

└── LICENSE

```



---



\## Author



\*\*Vikash\*\*



\- Methodology: Cognitive Verification Architecture

\- Framework: VEGA (Verification Engineering Graph Architecture)



---



\## License



MIT License - See \[LICENSE](LICENSE) for details.



---



\## Contributing



Contributions welcome! Please feel free to submit issues or pull requests.

