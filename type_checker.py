from typing import Optional
from pllm_ast import *
from type_env import TypeEnvironment
from type_pre import Type, Any, Int, Float, Bool, Str, Void, ListType, RecordType, string_to_type

class TypeErrorHandler:
    def __init__(self):
        self.errors = []

    def report(self, message: str = "", node: Optional[ASTNode] = None) -> None:
        """
        记录一个类型错误。
        :param message: 错误信息。
        :param node: 发生错误的AST节点
        """
        if node:
            # 利用 repr 打印 AST 节点的详细信息
            error_message = f"Error at {type(node).__name__}: {message}\n  Node details: {repr(node)}"
        else:
            error_message = f"Error: {message}"
        self.errors.append(error_message)

    def show(self) -> None:
        if len(self.errors) == 0:
            print("Type checking successfully.")
        else:
            for err in self.errors:
                print(err)

class TypeChecker:
    def __init__(self):
        self.type_env = TypeEnvironment()
        self.agent_io = TypeEnvironment()
        self.err_handler = TypeErrorHandler()

    def _initTypeEnvironment(self) -> None:
        # TODO: 初始化库函数或者一些其他的东西，但是暂时还没有实现库函数
        return
    
    def _show(self) -> None:
        self.err_handler.show()

    def checkProgram(self, program_node: Program) -> None:
        self._initTypeEnvironment()
        self.visit(program_node)
        self._show()

    def visit(self, ast_node: ASTNode) -> Optional[Type]:
        method_name: str = f"visit{type(ast_node).__name__}"
        visitor = getattr(self, method_name, self._defaultVisitor)
        return visitor(ast_node)
    
    def _defaultVisitor(self) -> None:
        # TODO: 抛出一个错误
        print("Not implemented yet.")

    # Program
    def visitProgram(self, node: Program) -> None:
        with self.type_env.scoped():
            for child in node.body:
                self.visit(child)

    # VarDecl
    def visitVarDecl(self, node: VarDecl) -> None:
        decl_var_name = node.name
        decl_var_type = string_to_type(node.var_type)
        decl_var_expr = node.value
        env_var_type = self.type_env.lookup(decl_var_name)

        # Case 1: id : type = expr
        if decl_var_expr is not None:
            exp_var_type = self.visit(decl_var_expr)
            # type(expr) <: type
            if not exp_var_type.isSubtypeOf(decl_var_type):
                self.err_handler.report(node=node)
                return
            # Handle gradual typing: Allow Any in the environment
            if env_var_type is not None and env_var_type is not Any:
                # type == history_type
                if not decl_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
                # type(expr) == history_type
                if not exp_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return

        # Case 2: id : type
        else:
            # Handle gradual typing: Allow Any in the environment
            if env_var_type is not None and env_var_type is not Any:
                if not decl_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return
        
    # AgentDef
    # TODO: Assign a type to Agent, current type system is not complete
    def visitAgentDef(self, node: AgentDef) -> None:
        with self.type_env.scoped():
            for child in node.body:
                self.visit(child)
                if isinstance(child, InputBlock):
                    for var in child.variables:
                        self.agent_io.define(f"{node.name}.input.{var.name}", self.type_env.lookup(var.name));
                if isinstance(child, OutputBlock):
                    for var in child.variables:
                        self.agent_io.define(f"{node.name}.output.{var.name}", self.type_env.lookup(var.name));

    # InputBlock
    def visitInputBlock(self, node: InputBlock) -> None:
        for child in node.variables:
            self.visit(child)

    # OutputBlock
    def visitOutputBlock(self, node: OutputBlock) -> None:
        for child in node.variables:
            self.visit(child)

    # ModelBlock
    def visitModelBlock(self, node: ModelBlock) -> None:
        return
    
    # ChatBlock
    def visitChatBlock(self, node: ChatBlock) -> None:
        return
    
    # ConnectBlock
    def visitConnectBlock(self, node: ConnectBlock) -> None:
        for child in node.connections:
            self.visit(child)

    # Connection
    def visitConnection(self, node: Connection) -> None:
        source = f"{node.source.parts[0]}.{node.source.parts[1]}.{node.source.parts[2]}"
        target = f"{node.target.parts[0]}.{node.target.parts[1]}.{node.target.parts[2]}"
        source_type = self.agent_io.lookup(source)
        target_type = self.agent_io.lookup(target)
        if not source_type.isSubtypeOf(target_type):
            self.err_handler.report(node=node)
            return
    
    # AgentRef
    def visitAgentRef(self, node: AgentRef) -> None:
        # handled in Connection
        return
    
    # FuncDef
    # TODO: Assign a type to function
    def visitFuncDef(self, node: FuncDef) -> None:
        with self.type_env.scoped():
            for param in node.params:
                self.visit(param)
            for stmt in node.stmt_body:
                self.visit(stmt)

    # ParamDecl
    def visitParamDecl(self, node: ParamDecl) -> None:
        decl_var_name = node.name
        decl_var_type = node.param_type
        decl_var_expr = node.default_value
        env_var_type = self.type_env.lookup(decl_var_name)

        # Case 1: id : type = expr
        if decl_var_expr is not None:
            exp_var_type = self.visit(decl_var_expr)
            # type(expr) <: type
            if not exp_var_type.isSubtypeOf(decl_var_type):
                self.err_handler.report(node=node)
                return
            # Handle gradual typing: Allow Any in the environment
            if env_var_type is not None and env_var_type is not Any:
                # type == history_type
                if not decl_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
                # type(expr) == history_type
                if not exp_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return

        # Case 2: id : type
        else:
            # Handle gradual typing: Allow Any in the environment
            if env_var_type is not None and env_var_type is not Any:
                if not decl_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return
        
    # AssignStmt
    def visitAssignStmt(self, node: AssignStmt) -> None:
        decl_var_name = node.target
        decl_var_type = string_to_type(node.var_type)
        decl_var_expr = node.value
        env_var_type = self.type_env.lookup(decl_var_name)
        exp_var_type = self.visit(decl_var_expr)

        # Case 1 id : type = expr
        if decl_var_type is not None:
            # type(expr) <: type
            if not exp_var_type.isSubtypeOf(decl_var_type):
                self.err_handler.report(node=node)
                return
            # Handle gradual typing: Allow Any in the environment
            if env_var_type is not None and env_var_type is not Any:
                # type == history_type
                if not decl_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
                # type(expr) == history_type
                if not exp_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
            # Update the type environment
            self.type_env.define(decl_var_name, decl_var_type)
            return
        else:
        # Case 2 id = expr
            if env_var_type is not None and env_var_type is not Any:
                if not exp_var_type.isEquivalentTo(env_var_type):
                    self.err_handler.report(node=node)
                    return
            self.type_env.define(decl_var_name, decl_var_type)
            return

    # ReturnStmt
    # TODO: Assign a type to function
    def visitReturnStmt(self, node: ReturnStmt) -> None:
        return
    
    # IfStmt
    def visitIfStmt(self, node: IfStmt) -> None:
        cond_expr = node.condition
        cond_expr_type = self.visit(cond_expr)
        if not cond_expr_type.isEquivalentTo(Bool):
            self.err_handler.report(node=node)
        for stmt in node.body:
            with self.type_env.scoped():
                self.visit(stmt)
        for stmt in node.else_block:
            with self.type_env.scoped():
                self.visit(stmt)
        return
    
    # WhileStmt
    def visitWhileStmt(self, node: WhileStmt) -> None:
        cond_expr = node.condition
        cond_expr_type = self.visit(cond_expr)
        if not cond_expr_type.isEquivalentTo(Bool):
            self.err_handler.report(node=node)
        for stmt in node.body:
            with self.type_env.scoped():
                self.visit(stmt)
        return
    
    # ForStmt
    def visitForStmt(self, node: ForStmt) -> None:
        iterator = node.iterator
        iterable = node.iterable
        iterator_type = self.type_env.lookup(iterator)
        if iterator_type is None:
            print("TypeError")

        iterable_type = self.visit(iterable)
        if not isinstance(iterable_type, ListType):
            print("TypeError")

        element_type = iterable_type.element_type
        if not iterator_type.isSubtypeOf(element_type):
            print("TypeError")

        for stmt in node.body:
            self.visit(stmt)

    # BreakStmt
    def visitBreakStmt(self, node: BreakStmt) -> None:
        pass

    # ContinueStmt
    def visitContinueStmt(self, node: ContinueStmt) -> None:
        pass

    # BinaryOp
    def visitBinaryOp(self, node: BinaryOp) -> Type:
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # 检查操作符类型约束
        if node.op in {"+", "-", "*", "/", "%"}:
            if not (left_type.isSubtypeOf(Int) or left_type.isSubtypeOf(Float)):
                self.err_handler.report(node=node)
            if not (right_type.isSubtypeOf(Int) or right_type.isSubtypeOf(Float)):
                self.err_handler.report(node=node)
            if left_type.isSubtypeOf(Float) or right_type.isSubtypeOf(Float):
                return Float
            return Int
        elif node.op in {"==", "!=", "<", ">", "<=", ">="}:
            if not left_type.isSubtypeOf(right_type) and not right_type.isSubtypeOf(left_type):
                self.err_handler.report(node=node)
            return Bool
        else:
            self.err_handler.report(node=node)

    # Atom
    def visitAtom(self, node: Atom) -> Type:
        value = node.value
        if isinstance(value, int):
            return Int
        elif isinstance(value, float):
            return Float
        elif isinstance(value, str):
            return Str
        elif isinstance(value, bool):
            return Bool
        else:
            var_type = self.type_env.lookup(value)
            return var_type
        
    # ListExpr
    def visitListExpr(self, node: ListExpr) -> Type:
        element_types = [self.visit(element) for element in node.elements]
        # TODO: lub
        if len(set(element_types)) > 1:
            self.err_handler.report(node=node)
        return ListType(element_types[0]) if element_types else ListType(Any)
    
    # RecordExpr
    def visitRecordExpr(self, node: RecordExpr) -> Type:
        fields = {}
        for inst_assign in node.fields:
            if not isinstance(inst_assign, InstanceAssign):
                self.error_handler.report(
                    f"Expected InstanceAssign in RecordExpr, but got {type(inst_assign).__name__}",
                    node
                )
                continue
            field_type = self.visit(inst_assign)
            fields[inst_assign.field] = field_type
        return RecordType(fields)

    # InstanceAssign
    def visitInstanceAssign(self, node: InstanceAssign) -> Type:
        field_name = node.field
        field_value_type = self.visit(node.value)  # 检查字段值的类型
        
        if not field_value_type:
            self.error_handler.report(
                f"Cannot determine type of value assigned to field '{field_name}'",
                node
            )
            return Any
        
        return field_value_type
    
    # FieldAccess
    def visitFieldAccess(self, node: FieldAccess) -> Type:
        obj = node.obj
        obj_type = self.type_env.lookup(obj)
        if not isinstance(obj_type, RecordType):
            self.err_handler.report(node=node)
        if node.field not in obj_type.fields:
            self.err_handler.report(node=node)
        return obj_type.fields[node.field]

    # FuncCall
    # TODO
    def visitFuncCall(self, node: FuncCall) -> Type:
        return Any