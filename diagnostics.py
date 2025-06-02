from parser import parser, ParseError
import json

def generage_diagnostics(source_code) -> list:
    diagnostic = {
        "result": "success",
        "diagnostic": {}
    }
    try:
        parser.parse(source_code)
    except ParseError as e:
        diagnostic = {
            "result": "error",
            "diagnostic": e.diagnostic
        }
    return diagnostic

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
    diagnostics = generage_diagnostics(source_code)
    print(json.dumps(diagnostics, indent=2))