# AST Insight

AST Insight is a tool designed to detect buffer overflow (BOF) vulnerabilities in C programs and provide suggestions for correcting them. It utilizes an Abstract Syntax Tree (AST) along with reasoning-based approach to provide a solution that
is flexible, modular, and easy to reason about.

## Features

- **Context Tracking:** Uses Abstract Syntax Tree (AST) parsing to keep track of variable declarations, allocations, and usage within the code.
- **Detailed Suggestions:** Provides detailed and multiple suggestions for mitigating detected vulnerabilities, including context-specific information to aid in detection and learnability

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/ast-insight.git
    cd ast-insight
    ```

2. **Install Pycparser:**
    ```bash
    pip install pycparser
    ```
## Usage
AST Insight can be run either as a server (Flask) or as a CLI tool
### Running the Server
To start the server, run:
```bash
python server.py
```
Once running, The server will accept POST requests to the `/analyze` endpoint. Code to be analyzed should be passed as a string to the `code` parameter.

Other configurations should be passed as other parameters although as of now the only configuration available is the Juliet flag which includes expected Juliet Test Suite headers to run benchmarks.

An interactive frontend application was written in Vue.js to work witht this API. Click [here](https://github.com/danielv27/AST-Insight-Frontend) to access it. 

### CLI Tool
To run the analysis through the CLI run:
```bash
python3 analyze.py <path-to-file>
```





