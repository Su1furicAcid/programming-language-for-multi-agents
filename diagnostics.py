"""
File name: diagnostics.py
Description: This script generates diagnostics for a given source code file. The diagonostics will be delivered to VSCode language server.
Author: Sun Ao
Last edited: 2025-6-2
"""
from pllm_parser import parse
import json

def generate_diagnostics(source_code) -> dict:
    """
    Generates diagnostics for the provided source code.
    Args:
        source_code (str): The source code to analyze.
    Returns:
        dict: A dictionary containing the result and any diagnostics found.
    """
    diagnostics = {
        "result": "success",
        "diagnostics": []
    }
    _, parse_errors = parse(source_code)
    if parse_errors:
        diagnostics["result"] = "error"
        diagnostics["diagnostics"] = parse_errors
        return diagnostics
    return diagnostics

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python diagnostics.py <source_code_path>")
        sys.exit(1)

    source_code_path = sys.argv[1]
    try:
        with open(source_code_path, 'r') as file:
            source_code = file.read()
    except FileNotFoundError:
        print(f"Error: File '{source_code_path}' not found.")
        sys.exit(1)
    diagnostics = generate_diagnostics(source_code)
    print(json.dumps(diagnostics, indent=2))