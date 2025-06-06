# TODO: Generate Python code based on tree pattern matching.
from typing import Optional
from contextlib import contextmanager
from pllm_parser.pllm_ast import *
from type_system.type_pre import Type, string_to_type, RecordType, ListType, FunctionType
from generate.triplestring_parser import process_string
from generate.topo_manager import TopoManager

class IndentManager:
    """
    IndentManager 是一个用于管理缩进层级的工具类，通常用于生成格式化的代码或文本。
    属性:
        indent_str (str): 单层缩进所使用的字符串（默认为四个空格）。
        current_level (int): 当前缩进层级。
    方法:
        get_indent():
            根据当前缩进层级返回对应的缩进字符串。
        indent():
            一个上下文管理器，进入时增加缩进层级，退出时减少缩进层级。
    """
    def __init__(self, indent_str="    "):
        self.indent_str = indent_str
        self.current_level = 0
    
    def get_indent(self):
        """
        根据当前缩进层级返回对应的缩进字符串。
        """
        return self.indent_str * self.current_level
    
    @contextmanager
    def indent(self):
        """
        一个上下文管理器，在进入上下文时增加缩进层级，退出时减少缩进层级。
        适用于生成需要缩进的代码块。
        用法示例：
            with indent_manager.indent():
            # 该代码块内的内容会自动缩进
            pass
        """
        self.current_level += 1
        try:
            yield
        finally:
            self.current_level -= 1

class CodeGenerator:
    def __init__(self):
        self.indent_manager = IndentManager()
        self.code = []

    def add_line(self, line):
        """
        加入一行代码
        """
        indent = self.indent_manager.get_indent()
        self.code.append(f"{indent}{line}\n")

    def get_pos(self):
        return len(self.code)
    
    def insert_line(self, line, pos):
        indent = self.indent_manager.get_indent()
        self.code.insert(pos, f"{indent}{line}\n")

    @contextmanager
    def indent(self):
        with self.indent_manager.indent():
            yield

    def _initCodeGenerator(self):
        # TODO: Prepare for generating
        self._include_built_in_functions("generate/built_in.py")
        return
    
    def _include_built_in_functions(self, built_in_path: str) -> None:
        with open(built_in_path, 'r', encoding="utf-8") as f:
            built_in_code = f.read()
            self.add_line(built_in_code)
    
    def show(self):
        # TODO: Write to file and compile
        with open('test.py', 'w', encoding="utf-8") as f:
            for line in self.code:
                f.write(line)

    def generate(self, program_node: Program) -> str:
        self._initCodeGenerator()
        self.visit(program_node)
        return ''.join(self.code)

    def visit(self, ast_node: ASTNode) -> Optional[str]:
        method_name: str = f"visit{type(ast_node).__name__}"
        visitor = getattr(self, method_name, self._defaultVisitor)
        return visitor(ast_node)

    def _defaultVisitor(self, node) -> None:
        # TODO: 抛出一个错误
        print(type(node).__name__)
        return
    
    def visitTypeDefStmt(self, node) -> None:
        return

    def visitProgram(self, node: Program) -> None:
        for child in node.body:
            self.visit(child)

    def visitVarDecl(self, node: VarDecl) -> str:
        decl_var_name_str = self.visit(node.name)
        decl_var_expr = node.value
        if decl_var_expr != "":
            decl_var_expr_str = self.visit(decl_var_expr)
            return f"{decl_var_name_str}={decl_var_expr_str}"
        else:
            return f"{decl_var_name_str}=None"

    def visitAgentDef(self, node: AgentDef) -> None:
        agent_name_str = self.visit(node.name)
        agent_def_pos = self.get_pos()
        agent_params = []
        agent_returns = []
        with self.indent():
            for child in node.body:
                if isinstance(child, InputBlock):
                    for var_decl in child.variables:
                        agent_params.append(self.visit(var_decl))
                elif isinstance(child, OutputBlock):
                    for var_decl in child.variables:
                        agent_returns.append(self.visit(var_decl))
                else:
                    self.visit(child)
        agent_def_str = f"async def {agent_name_str}({', '.join(agent_params)}):"
        self.insert_line(agent_def_str, agent_def_pos)
        with self.indent():
            if agent_returns:
                return_dict = ", ".join(f"'{var.split('=')[0]}': {var.split('=')[0]}" for var in agent_returns)
                self.add_line(f"return {{{return_dict}}}")
            else:
                pass
        return

    def visitInputBlock(self, node: InputBlock) -> None:
        # Implemented in AgentDef
        return
    
    def visitOutputBlock(self, node: OutputBlock) -> None:
        # Implemented in AgentDef
        return
    
    def visitModelBlock(self, node: ModelBlock) -> None:
        model_name = self.visit(node.model_name)
        self.add_line(f"model_name={model_name}")

    def visitChatBlock(self, node: ChatBlock) -> None:
        input_vars, output_vars, processed_string = process_string(node.template)
        if input_vars:
            input_formatting = ", ".join([f"{var}={var}" for var in input_vars])
            self.add_line(f'prompt={processed_string}.format({input_formatting})')
        else:
            self.add_line(f'prompt={processed_string}')
        self.add_line('client=AsyncOpenAI(')
        self.add_line('    base_url=BASE_URL,')
        self.add_line('    api_key=API_KEY')
        self.add_line(')')
        self.add_line('try:')
        with self.indent():
            self.add_line('response=await client.chat.completions.create(')
            with self.indent():
                    self.add_line('model=model_name,')
                    self.add_line('messages=[')
                    self.add_line('    {"role": "system", "content": SYS_PROMPT},')
                    self.add_line('    {"role": "user", "content": prompt}')
                    self.add_line(']')
            self.add_line(')')
            if output_vars:
                for i, var in enumerate(output_vars):
                    self.add_line(f'import re')
                    self.add_line(f'match_{i}=re.search(r"<completion{i}>(.*?)</completion{i}>", response.choices[0].message.content, re.DOTALL)')
                    self.add_line(f'{var}=match_{i}.group(1).strip() if match_{i} else ""')
        self.add_line('except Exception as e:')
        with self.indent():
            self.add_line('print(f"Error in chat block: {e}")')
            self.add_line(f'{", ".join(output_vars)}=""')  # Set outputs to empty string on error

    def _extract_agent_name(self, agent_ref: AgentRef) -> str:
        """
        从 AgentRef 对象中提取并返回代理(agent)名称。

        该方法会遍历 agent_ref 的每个部分，如果部分是 Identifier，则调用 visit 处理。
        如果存在至少一个部分，则返回第一个部分作为代理名称。

        参数:
            agent_ref (AgentRef): 包含代理标识各部分的 AgentRef 对象。

        返回:
            str: 提取到的代理名称（agent_ref 的第一个部分）。
        """
        parts = [self.visit(part) if isinstance(part, Identifier) else part for part in agent_ref.parts]
        if len(parts) >= 1:
            return parts[0]
                
    def visitConnectBlock(self, node: ConnectBlock) -> None:
        topo_manager = TopoManager()
        topo_manager.build_graph(node.connections, self._extract_agent_name)
        graph_code = f"graph = {repr(topo_manager.graph)}"
        self.add_line(graph_code)
        param_mapping_code = f"param_mapping={repr(topo_manager.param_mapping)}"
        self.add_line(param_mapping_code)
        self.add_line('if __name__ == "__main__":')
        with self.indent():
            execute_call = "asyncio.run(execute(graph, param_mapping))"
            self.add_line(execute_call)
    
    def visitFuncDef(self, node: FuncDef) -> None:
        func_name = self.visit(node.name)
        param_codes = []
        for param in node.params:
            param_code = self.visitParamDecl(param)
            param_codes.append(param_code)
        self.add_line(f"def {func_name}({', '.join(param_codes)}):")
        with self.indent():
            for stmt in node.stmt_body:
                self.visit(stmt)
    
    def visitParamDecl(self, node: VarDecl) -> str:
        param_name = self.visit(node.name)
        return f"{param_name}"
    
    def visitReturnStmt(self, node: ReturnStmt) -> None:
        if node.value != "":
            return_value_code = self.visit(node.value)
            self.add_line(f"return {return_value_code}")
        else:
            self.add_line("return")
    
    def visitAssignStmt(self, node: AssignStmt) -> None:
        if isinstance(node.target, Identifier):
            target_code = self.visit(node.target)
            expr_code = self.visit(node.value)
            assign_code = f"{target_code} = {expr_code}"
            self.add_line(assign_code)
        elif isinstance(node.target, FieldAccess):
            target_code = f"{self.visit(node.target.obj)}['{node.target.field.name}']"
            expr_code = self.visit(node.value)
            assign_code = f"{target_code} = {expr_code}"
            self.add_line(assign_code)
        elif isinstance(node.target, IndexAccess):
            obj_code = self.visit(node.target.obj)
            index_code = self.visit(node.target.index)
            expr_code = self.visit(node.value)
            assign_code = f"{obj_code}[{index_code}] = {expr_code}"
            self.add_line(assign_code)
    
    def visitIfStmt(self, node: IfStmt) -> None:
        cond_code = self.visit(node.condition)
        self.add_line(f"if {cond_code}:")
        with self.indent():
            for stmt in node.body:
                self.visit(stmt)
        if node.else_block:
            self.add_line("else:")
            with self.indent():
                for stmt in node.else_block:
                    self.visit(stmt)

    def visitWhileStmt(self, node: WhileStmt) -> None:
        cond_code = self.visit(node.condition)
        self.add_line(f"while {cond_code}:")
        with self.indent():
            for stmt in node.body:
                self.visit(stmt)

    def visitForStmt(self, node: ForStmt) -> None:
        iterator_code = node.iterator.name
        iterable_code = self.visit(node.iterable)
        self.add_line(f"for {iterator_code} in {iterable_code}:")
        with self.indent():
            for stmt in node.body:
                self.visit(stmt)

    def visitBreakStmt(self, node: BreakStmt) -> None:
        self.add_line("break")

    def visitContinueStmt(self, node: ContinueStmt) -> None:
        self.add_line("continue")

    def visitBinaryOp(self, node: BinaryOp) -> str:
        left_code = self.visit(node.left)
        right_code = self.visit(node.right)
        op = node.op
        return f"({left_code} {op} {right_code})"

    def visitIdentifier(self, node: Identifier) -> str:
        return str(node.name)
    
    def visitConstant(self, node: Constant) -> str:
        value = node.value
        if isinstance(value, str):
            return f'{value}'
        elif isinstance(value, bool):
            return "True" if value else "False"
        else:
            return str(value)
        
    def visitListExpr(self, node: ListExpr) -> str:
        elements_code = [self.visit(element) for element in node.elements]
        return f"[{', '.join(elements_code)}]"
    
    def visitRecordExpr(self, node: RecordExpr) -> str:
        fields_code = []
        for inst_assign in node.fields:
            field_name = inst_assign.field.name
            field_value_code = self.visit(inst_assign.value)
            fields_code.append(f'"{field_name}": {field_value_code}')
        return f"{{{', '.join(fields_code)}}}"

    def visitInstanceAssign(self, node: InstanceAssign) -> str:
        return f"{self.visit(node.field)} = {self.visit(node.value)}"

    def visitFieldAccess(self, node: FieldAccess) -> str:
        obj_code = self.visit(node.obj)
        field_name = node.field.name
        return f"{obj_code}['{field_name}']"
    
    def visitIndexAccess(self, node: IndexAccess) -> str:
        obj_code = self.visit(node.obj)
        index = self.visit(node.index)
        return f"{obj_code}[{index}]"

    def visitFuncCall(self, node: FuncCall) -> str:
        func_name = self.visit(node.func_name)
        arg_codes = [self.visit(arg) for arg in node.args]
        return f"{func_name}({', '.join(arg_codes)})"