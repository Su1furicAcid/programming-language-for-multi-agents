from lexer import lexer
from parser import parser
from type_checker import TypeChecker
from code_gen import CodeGenerator
import traceback

def run_code(source_code):
    try:
        ast = parser.parse(source_code, lexer=lexer)
        type_checker = TypeChecker()
        type_checker.checkProgram(ast)
        code_generator = CodeGenerator()
        py_code = code_generator.generate(ast)
        return py_code
    except Exception as e:
        return "Error: " + str(e) + "\n" + traceback.format_exc()

def repl():
    print("Multi-Agent Language REPL. 输入 exit 退出。")
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
                py_code = run_code(code)
                buffer.clear()
            else:
                buffer.append(line)
        except EOFError:
            break
        except Exception as e:
            print("REPL 错误：", e)
            buffer.clear()

if __name__ == "__main__":
    repl()