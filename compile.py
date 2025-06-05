import argparse
from parser.pllm_lexer import lexer
from parser.pllm_parser import parser
from type_system.type_checker import TypeChecker
from generate.code_gen import CodeGenerator
from ast_visual import ASTVisualizer

def main():
    # 命令行参数解析
    parser_args = argparse.ArgumentParser(description="Compile source code into Python code.")
    parser_args.add_argument("input_file", help="Path to the input source code file.")
    parser_args.add_argument("--output_file", default="output/output.py", help="Path to save the generated Python code.")
    args = parser_args.parse_args()

    input_file = args.input_file
    output_file = args.output_file

    # 加载输入文件
    try:
        with open(input_file, 'r') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        return
    except Exception as e:
        print(f"Error reading file '{input_file}': {e}")
        return

    # 初始化类型检查器和代码生成器
    type_checker = TypeChecker()
    code_generator = CodeGenerator()
    ast_visualizer = ASTVisualizer()

    try:
        # 解析源代码
        print("Parsing source code...")
        result = parser.parse(data, lexer=lexer)
        print("Parsing completed.")
        ast_visualizer.visualize(result)
        ast_visualizer.render()

        # 类型检查
        print("Performing type checking...")
        type_checker.checkProgram(result)
        print("Type checking completed.")

        # 代码生成
        print("Generating Python code...")
        generated_code = code_generator.generate(result)
        print("Code generation completed.")

        # 保存生成的代码到输出文件
        with open(output_file, 'w') as f:
            f.write(generated_code)
        print(f"Generated code has been saved to '{output_file}'.")

    except Exception as e:
        print(f"Compilation failed: {e}")

if __name__ == "__main__":
    main()
