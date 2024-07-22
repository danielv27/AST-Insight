# AST Insight

AST Insight is a tool designed to detect and provide suggestions for correcting buffer overflow vulnerabilities in C programs. It combines static code analysis using Facebook's Infer tool with Abstract Syntax Tree (AST) parsing to enhance the detection and correction of vulnerabilities. This dual approach enables AST Insight to provide more precise and actionable suggestions for mitigating the detected vulnerabilities.

## Features

- **Detection of Buffer Overflows:** Leverages Facebook Infer to detect potential buffer overflow vulnerabilities in C code.
- **AST Parsing:** Uses Abstract Syntax Tree (AST) parsing to keep track of variable declarations, allocations, and usage within the code.
- **Detailed Suggestions:** Provides detailed and multiple suggestions for mitigating detected vulnerabilities, including adjustments to buffer sizes and loop conditions.
- **Support for Complex Allocations:** Handles complex memory allocation expressions, including those involving casts and `sizeof` operations.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/ast-insight.git
    cd ast-insight
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Infer:**
    - Download and install Facebook Infer from [Infer's official site](https://fbinfer.com/).
    - Ensure that the `infer` binary is accessible in your `PATH`.

## Usage

### Running the Server

To start the server, run:

```bash
python server.py
