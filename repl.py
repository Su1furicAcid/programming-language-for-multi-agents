from pllm_lexer import lexer
from pllm_parser import parser
from type_checker import TypeChecker
from code_gen import CodeGenerator
import traceback

from pllm_lexer import lexer
from pllm_parser import parser
from type_checker import TypeChecker
from code_gen import CodeGenerator
import traceback

def run_code(source_code):
    try:
        # 解析代码生成 AST
        ast = parser.parse(source_code, lexer=lexer)
        # 类型检查
        type_checker = TypeChecker()
        type_checker.checkProgram(ast)
        # 代码生成
        code_generator = CodeGenerator()
        py_code = code_generator.generate(ast)
        # 执行生成的 Python 代码
        exec(py_code, globals(), {})
    except Exception as e:
        print("Error: " + str(e))
        print(traceback.format_exc())

def repl():
    print("Multi-Agent Language REPL")
    buffer = []
    while True:
        try:
            line = input(">>> ")
            if line.strip() in ("exit", "quit"):
                break
            if line.strip() == "":
                code = "\n".join(buffer)
                if not code.strip():
                    continue
                run_code(code)
            else:
                buffer.append(line)
        except EOFError:
            break
        except Exception as e:
            print("REPL Error: ", e)
            buffer.clear()

if __name__ == "__main__":
    repl()